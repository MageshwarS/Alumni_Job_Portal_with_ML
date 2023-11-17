from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
User = get_user_model()
from rest_framework.authtoken.views import Token
from django.utils.translation import gettext_lazy as _
import ast
from django.urls import reverse
from django.core.mail import send_mail
import secrets
import random
import string
from django.conf import settings
from apis.models import  AlumniDetails, StudentsDetails, Student, PortalUser, Alumniu, Alumni, Students


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=email, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return user, token.key

class StudentRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    #username = serializers.CharField(required=True)
    current_sem = serializers.IntegerField(required=True)
    current_cgpa = serializers.FloatField(required=True)
    standing_arrears = serializers.IntegerField(required=True)
    skillset = serializers.ListField(child=serializers.CharField(), required=False)
    projects = serializers.JSONField(required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name','current_sem', 'current_cgpa','standing_arrears','skillset','projects','email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
            
        }
  
    def save(self):
        email = self.validated_data['email']
        if not Students.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email not found in Students table. Contact Admin for further details'})
        '''username=self.validated_data['username'],
        if  PortalUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'username already exists.'})'''
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=email,
            email=email,
            role=PortalUser.Role.STUDENT 
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        user.set_password(password)
        # Generate a verification token
        '''token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))'''
        
        # Save the user with is_active=False and the verification token
        '''user.is_active = False
        user.verification_token = token'''
        user.save()

        # Send a verification email to the user
        '''subject = 'Verify your email'
        message = f'Hi {user.first_name},\n\nPlease click the following link to verify your email:\n\nhttp://127.0.0.1:8000/verify-email/?token={token}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)'''
        
        
        student = Student.objects.get(id=user.id)
        stud = Students.objects.get(email=email)
        student_profile = StudentsDetails.objects.create(user=student,
            current_sem=self.validated_data['current_sem'],
            current_cgpa=self.validated_data['current_cgpa'],
            standing_arrears=self.validated_data['standing_arrears'],
            skillset=self.validated_data.get('skillset'),
            projects=self.validated_data.get('projects'),
            register_no = stud.register_no,
            branch = stud.branch,
            specialization = stud.specialization,
            department = stud.department,
            name = stud.name,
            email=email,
            mobile_no=stud.mobile_no,
            password=self.validated_data['password'])
        student_profile.save()
        return user

class AlumniRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    #username = serializers.CharField(required=True)
    current_company = serializers.CharField(required=True)
    domain = serializers.CharField(required=True)
    current_jobrole = serializers.CharField(required=True)


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'current_company','domain','current_jobrole', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def save(self):
        email = self.validated_data['email']
        if not Alumni.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email not found in Students table. Contact Admin for further details'})
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=email,
            email=email,
            role=PortalUser.Role.ALUMNI
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        user.set_password(password)
        user.save()
        #Alumniu.objects.get(id=user.id)
        alumni = Alumniu.objects.get(id=user.id)
        alu = Alumni.objects.get(email=email)
        alumni_profile = AlumniDetails.objects.create(user=alumni,
            current_company=self.validated_data['current_company'],
            domain=self.validated_data['domain'],
            current_jobrole=self.validated_data['current_jobrole'],
            register_no = alu.register_no,
            branch = alu.branch,
            specialization = alu.specialization,
            department = alu.department,
            name = alu.name,
            email=email,
            mobile_no=alu.mobile_no,
            passed_out_year = alu.passed_out_year,
            password=self.validated_data['password'])
        alumni_profile.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError({'email': 'Invalid email or password.'})
        else:
            raise serializers.ValidationError({'email': 'Email and password are required.'})

        data['user'] = user
        return data
    

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalUser
        fields = '__all__'

class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = '__all__'

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'

class AlumniDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDetails
        fields = '__all__'

class StudentsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsDetails
        fields = '__all__'

class EditAlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDetails
        fields = ['current_company', 'domain', 'current_jobrole', 'mobile_no']

class EditStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsDetails
        fields = ['current_sem', 'current_cgpa', 'standing_arrears','skillset', 'mobile_no']

"""class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                return user
            else:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

class AlumniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumni
        fields = '__all__'

        extra_kwargs = {'password':{
                        'write_only':True,
                        'required':True
                        }}
        def create(self, validate_data):
            alumni = Alumni.objects.create_user(**validate_data)
            Token.objects.create(alumni =alumni)
            return alumni
        
class AlumniDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDetails
        fields = '__all__'

class StudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'

        extra_kwargs = {'password':{
                        'write_only':True,
                        'required':True
                        }}
        
class StudentsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentsDetails
        fields = '__all__'
"""