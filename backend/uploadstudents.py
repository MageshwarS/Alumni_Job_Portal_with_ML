import csv
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apis.models import PortalUser
from django.db import transaction
from apis.models import StudentsDetails
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()
def create_users_from_csv(file_path):
    created_users = []

    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            skillset = row['skillset'].split(', ')
            user = PortalUser.objects.create_user(
                email=row['Email address'],
                password='maanja',
                username=row['Email address'],
                role=PortalUser.Role.STUDENT
            )
            created_users.append(user)
            student_details = StudentsDetails.objects.create(
                user=user,
                current_sem=row['Current sem'],
                current_cgpa=row['Current cgpa'],
                email=row['Email address'],
                mobile_no=row['mobile number'],
                password='maanja',
                register_no=row['Register number'],
                branch=row['Branch'],
                specialization=row['Specialization'],
                department=row['Department'],
                name=row['Name'],
                skillset=skillset
            )

    return created_users

file_path = 'C:\\Users\\User\\Desktop\\IstNetWork\\backend\\batch4.csv'
with transaction.atomic():
    users = create_users_from_csv(file_path)
    print(f"Created {len(users)} users.")
