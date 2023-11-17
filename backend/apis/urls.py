from django.urls import path, include
from apis.views import StudentRegisterView, UserLoginAPIView, AlumniLoginView, StudentRegistrationAPIView, \
    AlumniRegistrationAPIView, StudentLoginView, StudentViewSet, AlumniViewSet, VerifyEmailView, AlumniDetailViewSet, StudentDetailViewSet, \
    home, EditAlumniViewSet,EditStudentViewSet, AlumniLogoutView, filter_students, get_branches_dropdown, get_current_sem_dropdown,\
    upload_resume, check_resume, resume_view
    
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register('alumni', AlumniViewSet, basename='alumni')
router.register('students', StudentViewSet, basename='student')
router.register('alumnidetails', AlumniDetailViewSet, basename='alumnidetails') 
router.register('studentsdetails', StudentDetailViewSet, basename='studentdetails')

# new

#router.register('editalumnidetails', EditAlumniViewSet, basename='editalumnidetails') 
'''
router.register('alumni', AlumniViewSet, basename='alumni')

router.register('students', StudentViewSet, basename='student')

router.register('studentregister/', StudentRegistrationAPIView, basename='studentregister')
router.register('studentsregister', StudentRegisterView, basename='studentsregister')'''
#router.register('users', UserViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path('', home, name='frontpage' ),
    path('alumnilogin/', AlumniLoginView.as_view(), name='alumnilogin'),
    path('logout/', AlumniLogoutView.as_view(), name='alumni_logout'),
    path('studentlogin/', StudentLoginView.as_view(), name='studentlogin'),
    path('studentregister/', StudentRegistrationAPIView.as_view(), name='studentregister'), # actual
    path('alumniregister/', AlumniRegistrationAPIView.as_view(), name='alumniregister'), # actual
    #path('login/', UserLoginAPIView.as_view(),name='login'), #actual login
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('get_branches_dropdown/', get_branches_dropdown, name='get_branches_dropdown' ),
    path('get_current_sem_dropdown/', get_current_sem_dropdown, name='get_current_sem_dropdown' ),
    path('filter_students/', filter_students, name='filter_students' ),


   path('api/editalumnidetails/<int:user_id>/', EditAlumniViewSet.as_view(),name='edit_alumni'),
   path('api/editstudentdetails/<int:user_id>/', EditStudentViewSet.as_view(),name='edit_student'),

   path('upload_resume/<int:user_id>/', upload_resume, name='upload_resume'),
   path('resume_view/<int:user_id>/', resume_view),
   #check_resume
   path('check_resume/<int:user_id>/', check_resume),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)