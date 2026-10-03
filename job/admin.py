from django.contrib import admin
from django.utils.html import format_html
from .models import Register, JobSeekerUser, EmployerUser, Job_listings, Applications

admin.site.site_header = "JobPortal Administration Panel"
admin.site.site_title = "JobPortal Admin"
admin.site.index_title = "Portal Database & User Roles Management"


# ---------------- 1. DEDICATED JOB SEEKERS ADMIN VIEW ----------------
@admin.register(JobSeekerUser)
class JobSeekerUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'applied_jobs_count', 'badge_view', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-id',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='candidate')

    @admin.display(description='Role Badge')
    def badge_view(self, obj):
        return format_html(
            '<span style="background:#4f46e5; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px;">'
            '🧑‍💼 Job Seeker'
            '</span>'
        )

    @admin.display(description='Total Applied Jobs')
    def applied_jobs_count(self, obj):
        count = Applications.objects.filter(user=obj).count()
        return format_html(f'<strong style="color:#6366f1;">{count} Application(s)</strong>')


# ---------------- 2. DEDICATED EMPLOYERS ADMIN VIEW ----------------
@admin.register(EmployerUser)
class EmployerUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'posted_jobs_count', 'badge_view', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'date_joined')
    ordering = ('-id',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='employer')

    @admin.display(description='Role Badge')
    def badge_view(self, obj):
        return format_html(
            '<span style="background:#059669; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px;">'
            '🏢 Employer / Recruiter'
            '</span>'
        )

    @admin.display(description='Total Posted Jobs')
    def posted_jobs_count(self, obj):
        count = Job_listings.objects.filter(user=obj).count()
        return format_html(f'<strong style="color:#10b981;">{count} Job(s) Posted</strong>')


# ---------------- 3. MASTER ALL-USERS REGISTER ADMIN ----------------
@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone', 'account_type_badge', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-id',)

    fieldsets = (
        ('User Credentials & Role', {
            'fields': ('username', 'email', 'phone', 'role', 'password')
        }),
        ('Permissions & Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Timestamps', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    @admin.display(description='Account Type (Role)', ordering='role')
    def account_type_badge(self, obj):
        if obj.role == 'employer':
            return format_html(
                '<span style="background:#10b981; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px; display:inline-block;">'
                '🏢 Employer / Recruiter'
                '</span>'
            )
        return format_html(
            '<span style="background:#6366f1; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:12px; display:inline-block;">'
            '🧑‍💼 Job Seeker'
            '</span>'
        )


# ---------------- 4. JOB LISTINGS ADMIN ----------------
@admin.register(Job_listings)
class Job_listingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'posted_by_employer', 'salary', 'location', 'category', 'created_at')
    list_filter = ('category', 'location', 'created_at')
    search_fields = ('title', 'company', 'location', 'description', 'user__username', 'user__email')
    ordering = ('-created_at',)

    @admin.display(description='Posted By (Employer)')
    def posted_by_employer(self, obj):
        return f"🏢 {obj.user.username} ({obj.user.email})"


# ---------------- 5. APPLICATIONS ADMIN ----------------
@admin.register(Applications)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'applicant_candidate', 'email', 'phone', 'applied_for_job', 'qualification', 'city')
    list_filter = ('qualification', 'city', 'state')
    search_fields = ('name', 'email', 'phone', 'college', 'job__title')
    ordering = ('-id',)

    @admin.display(description='Applicant (Job Seeker)')
    def applicant_candidate(self, obj):
        return f"🧑‍💼 {obj.name or obj.user.username}"

    @admin.display(description='Applied Job')
    def applied_for_job(self, obj):
        return f"{obj.job.title} ({obj.job.company or 'Company'})"