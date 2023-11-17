from django.contrib import admin

# Register your models here.

from apis.models import PortalUser, StudentsDetails, AlumniDetails, Students, Alumni


class StudentAdmin(admin.ModelAdmin):
    list_display=('name','register_no', 'email', 'mobile_no', 'branch')
    search_fields=('name','register_no', 'email', 'mobile_no', 'branch')

class AlumniAdmin(admin.ModelAdmin):
    list_display=('name','register_no', 'email', 'mobile_no', 'passed_out_year', 'current_company')
    search_fields=('name','register_no', 'email', 'mobile_no', 'passed_out_year', 'current_company')

admin.site.register(PortalUser)
admin.site.register(Alumni)
admin.site.register(Students)
admin.site.register(StudentsDetails, StudentAdmin)
admin.site.register(AlumniDetails, AlumniAdmin)