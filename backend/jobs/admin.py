from django.contrib import admin
from jobs.models import Job, OtherJobs, OtherPortals, Application
from django.utils import timezone
# Register your models here.



class JobAdmin(admin.ModelAdmin):
    list_display=('title','company_name', 'pay_offered', 'job_offer_type','skills_required', 'posted_by','location', 'posted_on', 'status')
    search_fields=('title','company_name', 'pay_offered', 'job_offer_type','skills_required', 'posted_by','location', 'status')

    # def days_since_creation(self, Job):
    #     diff = timezone.localtime(timezone.now()) - timezone.localtime(Job.posted_on)
    #     return diff.days
    # days_since_creation.short_description = 'Days Since Creation'
    
class ApplicationAdmin(admin.ModelAdmin):
    list_display=('job','created_by', 'created_at', 'status')
    search_fields=('job', 'created_by', 'status')
class OtherPortalAdmin(admin.ModelAdmin):
    list_display=('portal_name',)
    search_fields=('portal_name',)
class OtherJobAdmin(admin.ModelAdmin):
    list_display=('title','company_name', 'experience_needed', 'other_portal','skills_required', 'location','link', 'status')
    search_fields=('title','company_name', 'experience_needed', 'other_portal','skills_required', 'location', 'status')
admin.site.register(Job, JobAdmin)
admin.site.register(OtherJobs, OtherJobAdmin)
admin.site.register(OtherPortals, OtherPortalAdmin)
admin.site.register(Application, ApplicationAdmin)