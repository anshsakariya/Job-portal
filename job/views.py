from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Job_listings ,Applications 
User = get_user_model()


def welcome(request):
    return render(request, 'welcome.html')


# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'register.html')

        # username exist
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'register.html')

        # phone exist
        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Mobile number already registered")
            return render(request, 'register.html')

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.phone = phone
        user.save()

        return redirect('login')

    return render(request, 'register.html')


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'login.html')


# ---------------- USER DASHBOARD ----------------
@login_required
def user_dashboard_view(request):
    location = request.GET.get('location')
    company = request.GET.get('company')
    category = request.GET.get('category')

    jobs = Job_listings.objects.all()

    if location:
        jobs = jobs.filter(location__icontains=location)

    if company:
        jobs = jobs.filter(company__icontains=company)

    if category:
        jobs = jobs.filter(category__icontains=category)
    
    return render(request, 'user_dashboard.html', {'jobs': jobs})


# ---------------- EMP DASHBOARD ----------------
@login_required
def emp_dashboard_view(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        salary = request.POST.get('salary')
        category = request.POST.get('category')
        company = request.POST.get('company')
        location = request.POST.get('location')

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
        return redirect('emp_dashboard')

    jobs = Job_listings.objects.all().order_by('-created_at')
    return render(request, 'emp_dashboard.html', {'jobs': jobs})

def edit_job_view(request, id):
    job = get_object_or_404(Job_listings, id=id)

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.description = request.POST.get('description')
        job.salary = request.POST.get('salary')
        job.category = request.POST.get('category') 
        job.company = request.POST.get('company')   
        job.location = request.POST.get('location')
        job.save()
        return redirect('emp_dashboard')

    return render(request, 'edit_job.html', {'job': job})

def delete_job(request, id):
    job = Job_listings.objects.get(id=id)
    job.delete()
    return redirect('emp_dashboard')

# ---------------- Apply DASHBOARD ----------------
@login_required
def Apply_job_view(request, job_id):
    job = get_object_or_404(Job_listings, id=job_id)
   
    if request.method == "POST":
        Applications.objects.create(
            user=request.user,
            job=job,
            title=job.title,
            name=request.POST.get('u_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'), 
            city=request.POST.get('city'),    
            state=request.POST.get('state'),  
            qualification=request.POST.get('qualification'),
            college=request.POST.get('college'),
            passing_year=request.POST.get('passing_year'),
            percentage=request.POST.get('percentage'),
        )
        messages.success(request, "Applied successfully!")
        return redirect('user_dashboard')

    return render(request, 'Apply__job.html', {'job': job})