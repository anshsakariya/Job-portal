from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings

class Register(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Job Seeker / Candidate'),
        ('employer', 'Employer / Recruiter'),
    )
    first_name = None
    last_name = None
    phone = models.CharField(max_length=10, unique=True)
    username = models.CharField(max_length=100, unique=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def __str__(self):
        role_title = "Employer" if self.role == 'employer' else "Job Seeker"
        return f"{self.username} ({self.email}) - [{role_title}]"


class JobSeekerUser(Register):
    class Meta:
        proxy = True
        verbose_name = "🧑‍💼 Job Seeker"
        verbose_name_plural = "🧑‍💼 1. Job Seekers (Candidates)"


class EmployerUser(Register):
    class Meta:
        proxy = True
        verbose_name = "🏢 Employer"
        verbose_name_plural = "🏢 2. Employers (Recruiters)"

class Job_listings(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.title
    
class Applications(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job_listings, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    college = models.CharField(max_length=100, null=True, blank=True)
    passing_year = models.IntegerField(null=True, blank=True)
    percentage = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.job.title}"