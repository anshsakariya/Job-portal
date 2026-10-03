from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from .models import Job_listings, Applications

User = get_user_model()


# ---------------- WELCOME / HOME ----------------
def welcome(request):
    total_jobs = Job_listings.objects.count()
    total_seekers = User.objects.filter(role='candidate').count()
    total_employers = User.objects.filter(role='employer').count()
    categories_list = Job_listings.objects.values_list('category', flat=True).distinct()[:8]
    recent_jobs = Job_listings.objects.all().order_by('-created_at')[:4]
    
    context = {
        'total_jobs': total_jobs,
        'total_seekers': total_seekers or User.objects.count(),
        'total_employers': total_employers,
        'categories_list': categories_list,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'welcome.html', context)


# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'candidate').strip().lower()

        if role not in ['candidate', 'employer']:
            role = 'candidate'

        # Password match validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'register.html', {'username': username, 'email': email, 'phone': phone, 'selected_role': role})

        # Email validation (Must be UNIQUE)
        if not email:
            messages.error(request, "Email address is required.")
            return render(request, 'register.html', {'username': username, 'email': email, 'phone': phone, 'selected_role': role})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email address already exists. Please use a different email or log in.")
            return render(request, 'register.html', {'username': username, 'email': email, 'phone': phone, 'selected_role': role})

        # Phone validation (Must be UNIQUE, 10 digits)
        phone_cleaned = ''.join(filter(str.isdigit, phone))
        if len(phone_cleaned) > 10:
            phone_cleaned = phone_cleaned[-10:]

        if len(phone_cleaned) != 10:
            messages.error(request, "Please enter a valid 10-digit phone number.")
            return render(request, 'register.html', {'username': username, 'email': email, 'phone': phone, 'selected_role': role})

        if User.objects.filter(phone=phone_cleaned).exists():
            messages.error(request, "An account with this phone number already exists. Please use a different phone number.")
            return render(request, 'register.html', {'username': username, 'email': email, 'phone': phone, 'selected_role': role})

        # Username / Name is allowed to be same as others!
        if not username:
            username = email.split('@')[0]

        # Create user instance
        user = User(
            username=username,
            email=email,
            phone=phone_cleaned,
            role=role
        )
        if role == 'employer':
            user.is_staff = True
        user.set_password(password)
        user.save()

        # Redirect to login page after successful registration
        if role == 'employer':
            messages.success(request, f"🎉 Employer account created successfully! Please log in to continue.")
        else:
            messages.success(request, f"🎉 Job Seeker account created successfully! Please log in to continue.")
        
        return redirect('login')

    return render(request, 'register.html', {'selected_role': 'candidate'})


# ---------------- LOGIN (Supports Email, Phone, or Username) ----------------
def login_view(request):
    remembered_username = request.COOKIES.get('remember_username', '')

    if request.method == "POST":
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        user_candidate = None

        # 1. Try finding user by Email (Unique)
        if '@' in login_input:
            user_candidate = User.objects.filter(email__iexact=login_input).first()

        # 2. Try finding user by Phone Number (Unique)
        if not user_candidate:
            phone_digits = ''.join(filter(str.isdigit, login_input))
            if len(phone_digits) >= 10:
                user_candidate = User.objects.filter(phone=phone_digits[-10:]).first()

        # 3. Try finding user by Username / Name
        if not user_candidate:
            matching_users = User.objects.filter(username__iexact=login_input)
            if matching_users.count() == 1:
                user_candidate = matching_users.first()
            elif matching_users.count() > 1:
                matched_with_pw = [u for u in matching_users if u.check_password(password)]
                if len(matched_with_pw) == 1:
                    user_candidate = matched_with_pw[0]
                elif len(matched_with_pw) > 1:
                    messages.error(request, "Multiple accounts exist with this name. Please log in using your Email or Phone Number.")
                    return render(request, 'login.html', {'remembered_username': login_input, 'next': request.POST.get('next') or request.GET.get('next')})

        # 4. Fallback check by email without '@'
        if not user_candidate:
            user_candidate = User.objects.filter(email__iexact=login_input).first()

        if user_candidate is not None and user_candidate.check_password(password):
            user = user_candidate
            login(request, user)

            is_employer = (getattr(user, 'role', 'candidate') == 'employer' or user.is_superuser)

            # Session storage
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['email'] = user.email
            request.session['phone'] = getattr(user, 'phone', '')
            request.session['role'] = 'Employer' if is_employer else 'Job Seeker'
            request.session['login_time'] = timezone.now().strftime('%d %b %Y, %I:%M %p')

            # Pre-cache candidate's applied jobs & profile
            if not is_employer:
                applied_ids = list(Applications.objects.filter(user=user).values_list('job_id', flat=True))
                request.session['applied_job_ids'] = applied_ids

                latest_app = Applications.objects.filter(user=user).last()
                if latest_app:
                    request.session['user_profile'] = {
                        'name': latest_app.name or user.username,
                        'email': latest_app.email or user.email,
                        'phone': latest_app.phone or getattr(user, 'phone', ''),
                        'city': latest_app.city or '',
                        'state': latest_app.state or '',
                        'qualification': latest_app.qualification or '',
                        'college': latest_app.college or '',
                        'passing_year': latest_app.passing_year or '',
                        'percentage': latest_app.percentage or '',
                    }
                else:
                    request.session['user_profile'] = {
                        'name': user.username,
                        'email': user.email,
                        'phone': getattr(user, 'phone', ''),
                        'city': '',
                        'state': '',
                        'qualification': '',
                        'college': '',
                        'passing_year': '',
                        'percentage': '',
                    }

            next_url = request.POST.get('next') or request.GET.get('next')
            messages.success(request, f"Welcome back, {user.username}!")

            if is_employer:
                if next_url and next_url.startswith('/'):
                    response = redirect(next_url)
                else:
                    response = redirect('emp_dashboard')
            else:
                if next_url and next_url.startswith('/') and not next_url.startswith('/emp') and not next_url.startswith('/post_job'):
                    response = redirect(next_url)
                else:
                    response = redirect('user_dashboard')

            # Cookie and Session Expiry
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)
                response.set_cookie('remember_username', login_input, max_age=60 * 60 * 24 * 30, httponly=True, samesite='Lax')
            else:
                request.session.set_expiry(0)
                response.delete_cookie('remember_username')

            return response
        else:
            messages.error(request, "Invalid credentials. Please check your Email/Phone/Username and Password.")

    next_url = request.GET.get('next', '')
    return render(request, 'login.html', {'remembered_username': remembered_username, 'next': next_url})


# ---------------- LOGOUT ----------------
def logout_view(request):
    username = request.user.username if request.user.is_authenticated else "User"
    auth.logout(request)
    request.session.flush()
    messages.info(request, f"Goodbye, {username}. You have been securely logged out.")
    return redirect('login')


# ---------------- CANDIDATE / USER DASHBOARD ----------------
@login_required
def user_dashboard_view(request):
    search_query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    company = request.GET.get('company', '').strip()
    category = request.GET.get('category', '').strip()

    jobs = Job_listings.objects.all().order_by('-created_at')

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if company:
        jobs = jobs.filter(company__icontains=company)

    if category and category.lower() != 'all':
        jobs = jobs.filter(category__iexact=category)

    # Candidate's applied jobs set
    applied_job_ids = set(Applications.objects.filter(user=request.user).values_list('job_id', flat=True))
    my_applications_count = len(applied_job_ids)

    # Available categories
    available_categories = Job_listings.objects.values_list('category', flat=True).distinct()

    is_employer = (getattr(request.user, 'role', 'candidate') == 'employer' or request.user.is_superuser)

    session_data = {
        'username': request.session.get('username', request.user.username),
        'email': request.session.get('email', request.user.email),
        'phone': request.session.get('phone', getattr(request.user, 'phone', '')),
        'role': 'Employer' if is_employer else 'Job Seeker',
        'login_time': request.session.get('login_time', 'Active Session'),
    }

    context = {
        'jobs': jobs,
        'total_jobs_count': jobs.count(),
        'my_applications_count': my_applications_count,
        'applied_job_ids': applied_job_ids,
        'available_categories': available_categories,
        'selected_category': category,
        'location': location,
        'company': company,
        'search_query': search_query,
        'session_data': session_data,
        'is_employer': is_employer,
    }
    return render(request, 'user_dashboard.html', context)


# ---------------- MY APPLICATIONS (Job Seeker / Candidate Only) ----------------
@login_required
def my_applications_view(request):
    if getattr(request.user, 'role', 'candidate') == 'employer' and not request.user.is_superuser:
        messages.info(request, "Employers do not have candidate applications. Redirecting to Employer Console.")
        return redirect('emp_dashboard')

    applications = Applications.objects.filter(user=request.user).select_related('job').order_by('-id')
    return render(request, 'my_applications.html', {'applications': applications})


# ---------------- APPLY JOB (Job Seeker / Candidate Only) ----------------
@login_required
def Apply_job_view(request, job_id):
    if getattr(request.user, 'role', 'candidate') == 'employer' and not request.user.is_superuser:
        messages.warning(request, "Employer accounts cannot submit job applications. Please use a Job Seeker account.")
        return redirect('emp_dashboard')

    job = get_object_or_404(Job_listings, id=job_id)

    already_applied = Applications.objects.filter(user=request.user, job=job).exists()
    if already_applied and request.method != "POST":
        messages.info(request, f"You have already applied for '{job.title}'. Submitting again will update your application.")

    if request.method == "POST":
        name = request.POST.get('u_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        qualification = request.POST.get('qualification', '').strip()
        college = request.POST.get('college', '').strip()
        passing_year = request.POST.get('passing_year', '').strip() or None
        percentage = request.POST.get('percentage', '').strip()

        Applications.objects.create(
            user=request.user,
            job=job,
            title=job.title,
            name=name,
            email=email,
            phone=phone,
            city=city,
            state=state,
            qualification=qualification,
            college=college,
            passing_year=passing_year,
            percentage=percentage,
        )

        request.session['user_profile'] = {
            'name': name,
            'email': email,
            'phone': phone,
            'city': city,
            'state': state,
            'qualification': qualification,
            'college': college,
            'passing_year': passing_year,
            'percentage': percentage,
        }

        applied_list = request.session.get('applied_job_ids', [])
        if job.id not in applied_list:
            applied_list.append(job.id)
            request.session['applied_job_ids'] = applied_list
        request.session.modified = True

        messages.success(request, f"🎉 Application for '{job.title}' submitted successfully!")
        return redirect('user_dashboard')

    session_profile = request.session.get('user_profile', {})
    initial_data = {
        'name': session_profile.get('name') or request.user.username,
        'email': session_profile.get('email') or request.user.email,
        'phone': session_profile.get('phone') or getattr(request.user, 'phone', ''),
        'city': session_profile.get('city', ''),
        'state': session_profile.get('state', ''),
        'qualification': session_profile.get('qualification', ''),
        'college': session_profile.get('college', ''),
        'passing_year': session_profile.get('passing_year', ''),
        'percentage': session_profile.get('percentage', ''),
    }

    return render(request, 'Apply__job.html', {
        'job': job,
        'initial': initial_data,
        'already_applied': already_applied
    })


# ---------------- EMPLOYER DASHBOARD (Employer Only) ----------------
@login_required
def emp_dashboard_view(request):
    if getattr(request.user, 'role', 'candidate') != 'employer' and not request.user.is_superuser:
        messages.error(request, "❌ Access restricted: Job Seekers cannot access Employer Console.")
        return redirect('user_dashboard')

    my_jobs = Job_listings.objects.filter(user=request.user).order_by('-created_at')
    employer_job_ids = my_jobs.values_list('id', flat=True)
    my_applications = Applications.objects.filter(job_id__in=employer_job_ids).select_related('job', 'user').order_by('-id')

    context = {
        'jobs': my_jobs,
        'my_jobs_count': my_jobs.count(),
        'total_applications_count': my_applications.count(),
        'applications': my_applications,
        'session_role': 'Employer',
    }
    return render(request, 'emp_dashboard.html', context)


# ---------------- POST JOB (Employer Only - Job Seekers Forbidden) ----------------
@login_required
def post_job_view(request):
    if getattr(request.user, 'role', 'candidate') != 'employer' and not request.user.is_superuser:
        messages.error(request, "❌ Access Denied: Job Seekers cannot post jobs. Only Employer accounts can post job listings.")
        return redirect('user_dashboard')

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        salary = request.POST.get('salary', '').strip()
        category = request.POST.get('category', '').strip()
        company = request.POST.get('company', '').strip()
        location = request.POST.get('location', '').strip()

        if not company:
            company = "Not Specified"

        Job_listings.objects.create(
            user=request.user,
            title=title,
            description=description,
            salary=salary,
            category=category,
            company=company,
            location=location
        )
        messages.success(request, f"🎉 Job listing '{title}' published successfully!")
        return redirect('emp_dashboard')

    return render(request, 'post_job.html')


# ---------------- EMPLOYER APPLICANTS REVIEW (Employer Only) ----------------
@login_required
def employer_applicants_view(request, job_id):
    if getattr(request.user, 'role', 'candidate') != 'employer' and not request.user.is_superuser:
        messages.error(request, "❌ Access restricted: Only Employer accounts can review applicants.")
        return redirect('user_dashboard')

    if request.user.is_superuser:
        job = get_object_or_404(Job_listings, id=job_id)
    else:
        job = get_object_or_404(Job_listings, id=job_id, user=request.user)

    applicants = Applications.objects.filter(job=job).order_by('-id')
    
    return render(request, 'employer_applicants.html', {
        'job': job,
        'applicants': applicants,
        'total_count': applicants.count()
    })


# ---------------- EDIT JOB (Employer Only) ----------------
@login_required
def edit_job_view(request, id):
    if getattr(request.user, 'role', 'candidate') != 'employer' and not request.user.is_superuser:
        messages.error(request, "❌ Access restricted: Only Employer accounts can edit job listings.")
        return redirect('user_dashboard')

    if request.user.is_superuser:
        job = get_object_or_404(Job_listings, id=id)
    else:
        job = get_object_or_404(Job_listings, id=id, user=request.user)

    if request.method == "POST":
        job.title = request.POST.get('title', '').strip()
        job.description = request.POST.get('description', '').strip()
        job.salary = request.POST.get('salary', '').strip()
        job.category = request.POST.get('category', '').strip()
        job.company = request.POST.get('company', '').strip()
        job.location = request.POST.get('location', '').strip()
        job.save()
        messages.success(request, f"Job listing '{job.title}' updated successfully!")
        return redirect('emp_dashboard')

    return render(request, 'edit_job.html', {'job': job})


# ---------------- DELETE JOB (Employer Only) ----------------
@login_required
def delete_job(request, id):
    if getattr(request.user, 'role', 'candidate') != 'employer' and not request.user.is_superuser:
        messages.error(request, "❌ Access restricted: Only Employer accounts can delete job listings.")
        return redirect('user_dashboard')

    if request.user.is_superuser:
        job = get_object_or_404(Job_listings, id=id)
    else:
        job = get_object_or_404(Job_listings, id=id, user=request.user)

    job_title = job.title
    job.delete()
    messages.success(request, f"Job '{job_title}' deleted successfully.")
    return redirect('emp_dashboard')