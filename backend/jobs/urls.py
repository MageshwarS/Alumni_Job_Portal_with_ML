from django.urls import path, include

from .views import add_job, frontpage, CountsView, get_job_counts, get_jobs_by_user, JobViewSet, CreateJobView, TotalCountsView, \
 location_list, company_list, filter_jobs, get_job_details, get_recommendations, apply_job, get_applied_counts, linkedin_jobs, \
 get_location_suggestions, naukri_jobs, naukri_recommended_jobs, get_naukri_recommendations, nlocation_list, ncompany_list, \
 nsalary_list, nexperience_needed_list, get_collaborative_recommendations, click_job, get_ncollaborative_recommendations

urlpatterns = [
    path('add/', add_job, name='add_job'),
    path('viewjobs', frontpage , name='viewJobs'),
    path('count/', CountsView.as_view(), name='count'),
    path('totalcount/', TotalCountsView.as_view(), name='totalcount'),
    path('userjobcount/<int:user_id>', get_job_counts, name='userjobcount'),
    path('jobappliedcounts/<int:user_id>', get_applied_counts, name='get_applied_counts'),
    path('userpostedjobs/<int:user_id>', get_jobs_by_user, name='userjob'),
    path('jobs/<int:pk>', JobViewSet.as_view(), name='jobs'),
    path('createjobs/', CreateJobView.as_view(), name='createjobs'),
    path('jobs/', filter_jobs, name='job_list'),
    path('jobs/locations/', location_list, name='job_location_list'),
    path('jobs/companies/', company_list, name='job_company_list'),
    path('jobs/nlocations/', nlocation_list, name='njob_location_list'),
    path('jobs/ncompanies/', ncompany_list, name='njob_company_list'),
    path('jobs/nsalary/', nsalary_list, name='nsalary_list'),
    path('jobs/nexperience/', nexperience_needed_list, name='nexperience_needed_list'),
    path('jobdetails/<int:job_id>/', get_job_details, name='job-detail'),
    path('jobrecommendations/', get_recommendations, name='job-recommendations'),

    path('naukrijobrecommendations/', get_naukri_recommendations, name='get_naukri_recommendations'),

    path('applyJob/', apply_job, name='apply_job'),

    path('clickjob/', click_job, name='click_job'),

    path('linkedinjobs/', linkedin_jobs, name='linkedin_jobs'),
    path('api/locations', get_location_suggestions, name='get_location_suggestions'),
    path('naukrijobs/', naukri_jobs, name='naukri_jobs'),
    path('naukrirecommendedjobs/<str:title>/<str:location>/', naukri_recommended_jobs, name='naukri_recommended_jobs'),

    path('collaborativejobrecommendations/', get_collaborative_recommendations, name='get_collaborative_recommendations'),
    path('ncollaborativejobrecommendations/', get_ncollaborative_recommendations, name='get_collaborative_recommendations'),
]