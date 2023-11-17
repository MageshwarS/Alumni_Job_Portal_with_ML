from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework import status, permissions
from rest_framework.parsers import JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
User = get_user_model()
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.viewsets import ViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.authtoken.models import Token
from .models import PortalUser

from apis.models import  StudentsDetails,  AlumniDetails, Student, Alumniu, Students, Alumni
from apis.serializers import StudentCreateSerializer, AlumniDetailsSerializer, StudentsDetailsSerializer, \
StudentRegistrationSerializer, AlumniRegistrationSerializer, UserLoginSerializer, AuthTokenSerializer, StudentsSerializer, AlumniSerializer, \
EditAlumniSerializer, EditStudentSerializer
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from django.core.mail import send_mail
from django.core.mail import EmailMessage
from backend.settings import EMAIL_HOST_USER

from rest_framework.decorators import api_view

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import File
import os
from django.http import FileResponse

# Create your views here.
@csrf_exempt
def upload_resume(request, user_id):
    try:
        resume_file = request.FILES['resume']
    except:
        return JsonResponse({'error': 'No resume file provided or user not found.'}, status=400)
    student = StudentsDetails.objects.get(user=user_id)
    # student.resume_path=f'{user_id}.pdf'
    # student.save()

    if resume_file and student:

        resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')


        with open(resume_path, 'wb') as file:
            for chunk in resume_file.chunks():
                file.write(chunk)
    
        return JsonResponse({'message': 'Resume uploaded successfully.'})
    else:
        return JsonResponse({'error': 'No resume file provided or user not found.'}, status=400)

    
    
from django.http import FileResponse

def resume_view(request, user_id):
    resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')

    try:
        resume_file = open(resume_path, 'rb')
        return FileResponse(resume_file)
    except FileNotFoundError:
        return JsonResponse({'error': 'No resume file found.'}, status=400)


def check_resume(request, user_id):
    resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')

    try:
        with open(resume_path, 'rb'):
            return JsonResponse({'hasResume': True, 'resumeUrl': resume_path})
    except FileNotFoundError:
        return JsonResponse({'hasResume': False})
    
    
def home(request):
    return render(request, 'base.html')


class AlumniLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthTokenSerializer

    def get(self, request):
        return render(request, 'alumnilogin.html', {'user': request.user})

    

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if user.role == PortalUser.Role.ALUMNI:
            #return Response({'error': 'Invalid user credentials'})
            login(request, user)
            alu = AlumniDetails.objects.get(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'email': user.email,
                'domain': alu.domain
                 })
    

class AlumniLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        
        token = request.headers.get('Authorization').split(' ')[1] # Get the token value from the header
        user = Token.objects.get(key=token).user
        if user.is_authenticated:
            Token.objects.filter(user=user).delete()
            response = redirect('/alumnilogin/')
            response.delete_cookie('auth_token')
            if 'auth_token' in request.session:
                del request.session['auth_token']
            #return response
            logout(request)
            #return redirect('/alumnilogin/')
            return Response({'success': 'You have been logged out.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You are not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)


class StudentLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthTokenSerializer

    def get(self, request):
        return render(request, 'studentlogin.html')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if user.role != PortalUser.Role.STUDENT:
            return Response({'error': 'Invalid user credentials'})
        login(request, user)
        # subject ='Loged in'
        # message='successful testing'
        # recipient_list =[user.email] 
        # send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)

        stu = StudentsDetails.objects.get(user = user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'mobile': stu.mobile_no,
            'skillset': stu.skillset
        })

class StudentRegistrationAPIView(APIView):
    serializer_class = StudentRegistrationSerializer

    def get(self, request, *args, **kwargs):
        return render(request, 'studentregistration.html')

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AlumniRegistrationAPIView(APIView):
    serializer_class = AlumniRegistrationSerializer

    def get(self, request, *args, **kwargs):
        return render(request, 'alumniregistration.html')

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(View):
    def get(self, request):
        token = request.GET.get('token')
        try:
            user = User.objects.get(verification_token=token)
        except User.DoesNotExist:
            return redirect('invalid_token')
        user.is_active = True
        user.verification_token = ''
        user.save()
        return redirect('studentlogin/')

class Pagination1(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


#for Students table
class StudentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    pagination_class = Pagination1
    authentication_classes = (TokenAuthentication,)


#for Alumni table
class AlumniViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Alumni.objects.all()
    serializer_class = AlumniSerializer
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]
    pagination_class = Pagination1

#for Students Details table
class StudentDetailViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = StudentsDetails.objects.all()
    serializer_class = StudentsDetailsSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    lookup_field= "user_id"
    pagination_class = Pagination1


#for Alumni Details table
class AlumniDetailViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = AlumniDetails.objects.all()
    serializer_class = AlumniDetailsSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    lookup_field= "user_id"
    pagination_class = Pagination1


from rest_framework.permissions import AllowAny
class EditAlumniViewSet(generics.RetrieveUpdateAPIView):
    #authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = EditAlumniSerializer
    queryset = AlumniDetails.objects.all()

    def get_object(self):
        # Retrieve the alumni details for the authenticated user
        user_id = self.kwargs.get('user_id')
        return AlumniDetails.objects.get(user__id=user_id)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context = {'form': serializer.data}
        return render(request, 'alumnidetails.html', context)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class EditStudentViewSet(generics.RetrieveUpdateAPIView):
    #authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = EditStudentSerializer
    queryset = StudentsDetails.objects.all()

    def get_object(self):
        # Retrieve the alumni details for the authenticated user
        user_id = self.kwargs.get('user_id')
        return StudentsDetails.objects.get(user__id=user_id)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        context = {'form': serializer.data}
        return render(request, 'studentdetails.html', context)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)




@require_GET
def filter_students(request):
    # location = request.GET.get('location')
    skillset = request.GET.get('skillset')
    branch = request.GET.get('branch')
    current_sem = request.GET.get('current_sem')
    q = Q()

    # if location:
    #     q &= Q(location=location)
    if skillset:
        q &= Q(skillset__contains=[skillset])
    if current_sem:
        q &= Q(current_sem=current_sem)
    if branch:
        q &= Q(branch=branch)

    students = StudentsDetails.objects.filter(q)

    data = {
        'students': [
            {
                'id': student.id,
                'name': student.name,
                #'location': student.location,
                'current_sem': student.current_sem,
                'skills': student.skillset,
                'branch': student.branch,
                'email': student.email,
            } for student in students
        ]
    }

    return JsonResponse(data)

# @require_GET
# def get_locations(request):
#     locations = StudentsDetails.objects.values_list('location', flat=True).distinct()
#     data = {'locations': list(locations)}
#     return JsonResponse(data)

@require_GET
def get_branches_dropdown(request):
    branches = StudentsDetails.objects.values_list('branch', flat=True).distinct()
    data = {'branchs': list(branches)}
    return JsonResponse(data)

@require_GET
def get_current_sem_dropdown(request):
    current_sems = StudentsDetails.objects.values_list('current_sem', flat=True).distinct()
    data = {'current_sem': list(current_sems)}
    return JsonResponse(data)

    
    
    



























class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
            'user_id': user.pk,
            'email': user.email})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
class Pagination1(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


#for Students table
class StudentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    pagination_class = Pagination1
    authentication_classes = (TokenAuthentication,)

#for Students Details table
class StudentDetailsViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = StudentsDetails.objects.all()
    serializer_class = StudentsDetailsSerializer
    pagination_class = Pagination1

#for Alumni table
class AlumniViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Alumni.objects.all()
    serializer_class = AlumniSerializer
    pagination_class = Pagination1

#for Alumni Details table
class AlumniDetailsViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = AlumniDetails.objects.all()
    serializer_class = AlumniDetailsSerializer
    pagination_class = Pagination1

class StudentLoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    @action(methods=['post'], detail=False)
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = get_user_model()
        user = authenticate(email=email, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid login credentials", email: password}, status=status.HTTP_401_UNAUTHORIZED)
        
    def get_queryset(self):
        return PortalUser.objects.filter(role=PortalUser.Role.STUDENT)'''


class StudentRegisterView(viewsets.ModelViewSet):
    serializer_class = StudentCreateSerializer
    @action(methods=['post'], detail=False)
    def register(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = PortalUser.Role.STUDENT

        # Check if email already exists in students_defaultdata table
        '''if Students.objects.filter(email=email).exists():'''
        user = PortalUser.objects.create_user(email=email, password=password, role=role)
        student = Student.objects.get(id=user.id)
        student_profile = StudentsDetails.objects.create(user=student)
        #student_profile.sem = StudentDefaultData.objects.get(email=email).sem
        student_profile.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        '''else:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)'''
    def get_queryset(self):
        return PortalUser.objects.filter(role=PortalUser.Role.STUDENT)
    

'''class LoginView(APIView):
    permission_classes = [~IsAuthenticated]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        role = user.role
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key, 'role': role}, status=status.HTTP_200_OK)

class StudentLogin(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password, role='STUDENT')
        if user is not None:
            login(request, user)
            return Response({'success': True})
        else:
            return Response({'success': False, 'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

class AlumniLogin(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password, role='ALUMNI')
        if user is not None:
            login(request, user)
            return Response({'success': True})
        else:
            return Response({'success': False, 'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)'''
'''class StudentLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password, role=PortalUser.Role.STUDENT)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)'''
'''
class TeacherLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password, role=User.Role.TEACHER)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class TeacherRegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = User.Role.TEACHER

        # Check if email already exists in teacher_defaultdata table
        if TeacherDefaultData.objects.filter(email=email).exists():
            user = User.objects.create_user(email=email, password=password, role=role)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)
'''