from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.conf import settings

class Register(AbstractUser):
    first_name = None
    last_name = None
    phone = models.CharField(max_length=10)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)

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