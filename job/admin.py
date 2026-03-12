from django.contrib import admin
from .models import Register, Job_listings, Applications

@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone')

@admin.register(Job_listings)
class Job_listingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'salary', 'location', 'category','company')

@admin.register(Applications)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','email', 'phone', 'city', 'state', 'job', 'qualification','college','passing_year','percentage')