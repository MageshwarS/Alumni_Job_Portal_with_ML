# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class PortalUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        ALUMNI = "ALUMNI", "Alumni"

    #base_role = Role.ADMIN
    role = models.CharField(max_length=50, choices=Role.choices)
    #is_active = models.BooleanField(default=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # remove 'email' from this list
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.role
            self.is_active = True
            return super().save(*args, **kwargs)


class StudentManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        '''try:
            Students.objects.get(email=email)
        except Students.DoesNotExist:
            raise ValueError("Email not found in students data")'''
        extra_fields.setdefault('role', PortalUser.Role.STUDENT)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=PortalUser.Role.STUDENT)


class Student(PortalUser):
    base_role = PortalUser.Role.STUDENT
    objects = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for students"


@receiver(post_save, sender=Student)
def create_student_profile(sender, instance, created, **kwargs):
    print("Signal triggered")
    if created and instance.role == PortalUser.Role.STUDENT:
        student_details = StudentsDetails.objects.create(
            user=instance,  # link the Student instance to StudentsDetails
            current_sem=0,
            current_year=0,
            current_cgpa=0.0,
            email=instance.email,
            mobile_no='4',
            password=instance.password,
        )
        student_details.save()
        

class StudentsDetails(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE, related_name='studentu_id')
    #student = models.ForeignKey(Students,models.DO_NOTHING, null=False, null=True, blank=True)
    current_sem = models.IntegerField()
    current_cgpa = models.FloatField()
    standing_arrears = models.IntegerField(blank=True, null=True)
    skillset = ArrayField(models.CharField(max_length=455), blank=True, null=True)
    projects = models.JSONField(blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    register_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    department = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=455, blank=True, null=True)
    resume_path = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    class Meta:
        db_table = 'students_details'
    def __str__(self):
        return self.name

class AlumniManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=PortalUser.Role.ALUMNI)

class Alumniu(PortalUser):
    base_role = PortalUser.Role.ALUMNI
    alumni = AlumniManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Alumni"

@receiver(post_save, sender=Alumniu)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "ALUMNI":
        AlumniDetails.objects.create(user=instance)

class AlumniDetails(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE, related_name='alumniu_id')
    #alumni = models.ForeignKey(Alumni, models.DO_NOTHING,null=False, null=True, blank=True)
    current_company = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    current_jobrole = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    register_no = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    passed_out_year = models.IntegerField()
    department = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=455, blank=True, null=True)

    class Meta:
        db_table = 'alumni_details'
    def __str__(self):
        return self.name

class Alumni(models.Model):
    name = models.CharField(max_length=455)
    register_no = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    passed_out_year = models.IntegerField()
    department = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'alumni'
    def __str__(self):
        return self.name

class Students(models.Model):
    name = models.CharField(max_length=455)
    register_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    department = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    email = models.CharField(max_length=355)

    class Meta:
        managed = False
        db_table = 'students'
    def __str__(self):
        return self.name

"""class Alumni(models.Model):
    name = models.CharField(max_length=455)
    register_no = models.CharField(max_length=20, blank=True, null=True)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    passed_out_year = models.IntegerField()
    department = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    email = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'alumni'

class Students(models.Model):
    name = models.CharField(max_length=455)
    register_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=255)
    specialization = models.CharField(max_length=355)
    department = models.CharField(max_length=255, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    email = models.CharField(max_length=355)

    class Meta:
        managed = False
        db_table = 'students'"""


'''class PortalUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    base_role = Role.OTHER

    role = models.CharField(max_length=50, choices=Role.choices)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=PortalUser.Role.STUDENT)


class Student(PortalUser):

    base_role = PortalUser.Role.STUDENT

    student = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for students"


@receiver(post_save, sender=Student)
def create_student_profile(sender, instance, created, **kwargs):
    if created and instance.role == PortalUser.Role.STUDENT:
        # Check if the email is in student_defaultdata table
        email = instance.email
        try:
            student_default_data = Students.objects.get(email=email)
        except Students.DoesNotExist:
            raise ValueError("Email not found in student_defaultdata")

        # Create the student profile
        student_profile = StudentProfile.objects.create(user=instance)
        
        # Store the student's sem in the profile
        student_profile.sem = student_default_data.sem
        student_profile.save()



class StudentProfile(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE)
    student_id = models.IntegerField(null=True, blank=True)


class TeacherManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=PortalUser.Role.TEACHER)


class Teacher(PortalUser):

    base_role = PortalUser.Role.TEACHER

    teacher = TeacherManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for teachers"


class TeacherProfile(models.Model):
    user = models.OneToOneField(PortalUser, on_delete=models.CASCADE)
    teacher_id = models.IntegerField(null=True, blank=True)


@receiver(post_save, sender=Teacher)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "TEACHER":
        TeacherProfile.objects.create(user=instance)'''

