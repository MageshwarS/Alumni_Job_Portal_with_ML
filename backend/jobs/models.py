# Create your models here.
from django.db import models
from apis.models import PortalUser
from django.contrib.postgres.fields import ArrayField

class Job(models.Model):
    title = models.CharField(max_length=255)
    short_description = models.TextField()
    long_description = models.TextField()
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=455)
    posted_by = models.ForeignKey(PortalUser, on_delete=models.CASCADE)
    pay_offered = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=(("active", "Active"), ("hidden", "Hidden"),("hired","Hired")))
    skills_required = ArrayField(models.CharField(max_length=60), blank=True)
    job_offer_type = models.CharField(max_length=10, choices=(("intern", "Intern"), ("fulltime", "Full-Time")))
    posted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'jobs'

    def __str__(self):
        return self.title
    
    

class Application(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    content = models.TextField()
    experience = models.TextField()
    created_by = models.ForeignKey(PortalUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=(("active", "Active"), ("closed", "Closed")), default="active")

    class Meta:
        db_table = 'applications'

class Clicked(models.Model):
    other_job = models.ForeignKey('OtherJobs', on_delete=models.CASCADE)
    created_by = models.ForeignKey(PortalUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'other_jobs_clicked'

class OtherPortals(models.Model):
    portal_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'other_portals'

    def __str__(self):
        return self.portal_name

class OtherJobs(models.Model):
    title = models.CharField(max_length=355)
    company_name = models.CharField(max_length=455)
    location = models.CharField(max_length=255)
    description = models.TextField()
    link = models.TextField()
    experience_needed = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    skills_required = ArrayField(models.CharField(max_length=355), blank=True)
    other_portal = models.ForeignKey('OtherPortals', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('closed', 'Closed')],
        default='active'
    )

    class Meta:
        db_table = 'other_jobs'

    def __str__(self):
        return self.title