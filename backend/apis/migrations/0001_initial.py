# Generated by Django 4.1.7 on 2023-03-25 21:36

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="PortalUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("STUDENT", "Student"),
                            ("ALUMNI", "Alumni"),
                        ],
                        max_length=50,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[("objects", django.contrib.auth.models.UserManager()),],
        ),
        migrations.CreateModel(
            name="StudentsDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("current_sem", models.IntegerField()),
                ("current_year", models.IntegerField()),
                ("current_cgpa", models.FloatField()),
                ("standing_arrears", models.IntegerField(blank=True, null=True)),
                (
                    "skillset",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                ("projects", models.JSONField(blank=True, null=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("mobile_no", models.CharField(max_length=15)),
                ("password", models.CharField(max_length=255)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="studentu_id",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "students_details",},
        ),
        migrations.CreateModel(
            name="AlumniDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("current_company", models.CharField(max_length=255)),
                ("domain", models.CharField(max_length=255)),
                ("current_jobrole", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("mobile_no", models.CharField(max_length=15)),
                ("password", models.CharField(max_length=255)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alumniu_id",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "alumni_details",},
        ),
        migrations.CreateModel(
            name="Alumniu",
            fields=[],
            options={"proxy": True, "indexes": [], "constraints": [],},
            bases=("apis.portaluser",),
            managers=[
                ("alumni", django.db.models.manager.Manager()),
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[],
            options={"proxy": True, "indexes": [], "constraints": [],},
            bases=("apis.portaluser",),
        ),
    ]
