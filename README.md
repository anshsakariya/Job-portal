Job Portal Web Application

Project Overview

This is a Job Portal Web Application built using Django.
The purpose of this project is to help users find and apply for jobs and allow employers to post and manage jobs.

Technologies Used

Frontend

* HTML
* CSS

Backend

* Python
* Django

Database

* SQLite

Purpose of the Project

The main purpose of this project is to allow:

* Users to search and apply for jobs
* Employers to post, edit, and delete jobs
* Store job and application data in the database


Run the Project

Run the following command in the terminal:

python manage.py runserver

Then open the browser and visit:

http://127.0.0.1:8000/

Application Flow

Welcome Page

When the URL is opened, the Welcome Page appears.

Top side buttons:

* Register
* Login

Register

User fills the registration form.

After successful registration, the user is redirected to the Login Page.

Login

* If login is successful, the user is redirected to User Dashboard
* If login fails, the User Dashboard is not shown

User Dashboard Features

Users can:

* View all job posts
* Search jobs using:

  * Location
  * Company
  * Category

Apply for Job

* User clicks Apply button
* Application form opens
* After submitting, the data is stored in the database

If there are no jobs posted, the message will show:

No job available

Employer Dashboard Features

Employers can:

Post Job

* A job posting form is available
* After posting, the job will appear:

  * In User Dashboard
  * In Employer Dashboard job list
  * In the Database

If no job is posted, message shows:

No posted job available

Edit Job

Employer can click Edit button.

* All job details can be modified
* Changes update in:

  * User Dashboard
  * Employer Dashboard
  * Database

Delete Job

Employer can click **Delete button**.

The job will be removed from:

* User Dashboard
* Employer Dashboard job list
* Database

Django Admin Panel

Admin panel URL:http://127.0.0.1:8000/admin

Admin Login Credentials:

Username:Jobseeker
Email:jobseeker@gmail.com
Password: Jobseeker@123

Admin Panel Applications

In the Django Admin Panel:

Applications

Shows all job applications submitted by users

Job_listings

Shows all job postings created by employers

Users

Shows all registered users

Database Tables (SQLite)

The following tables store project data:

job_register

Stores user registration data

 job_job_listing

Stores job posting data

 job_applications

Stores job application data


command used


## Commands

1. Create Django Project
   python -m django startproject config .
        
2. Create Superuser
   python manage.py createsuperuser
   Username: Jobseeker
   Email: jobseeker@gmail.com
   Password: Jobseeker@123

3. Make Migrations
   python manage.py makemigrations

4. Apply Migrations
   python manage.py migrate

5. Run Server
   python manage.py runserver

Open in browser: http://127.0.0.1:8000/
