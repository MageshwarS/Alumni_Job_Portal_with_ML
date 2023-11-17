from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.authtoken.views import obtain_auth_token


admin.site.site_header='Alumni Student job portal Admin'
admin.site.site_title='Alumni Student job portal Admin panel'
admin.site.index_title='Portal Administration'
urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^',include('apis.urls')),
    re_path(r'^',include('jobs.urls')),
    path('auth/', obtain_auth_token)
]