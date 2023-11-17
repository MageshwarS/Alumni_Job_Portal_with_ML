import csv
from django.utils import timezone
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from apis.models import PortalUser
from jobs.models import Job
import random


def add_jobs_to_database():
    # posted_by_user = PortalUser.objects.get(id=33)
    portal_user_ids = [33, 34, 35, 39]
    count = 0
    with open('C:\\Users\\User\\Desktop\\IstNetWork\\backend\\Naukri_scrape.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)

        for row in csv_reader:
            pay_offered = random.randint(500000 // 1000, 1000000 // 1000) * 1000
            skills_required = [skill.strip() for skill in row[7].strip("[]").split(",")] 
            count=count +3
            if count % 9 == 0:
                job_type = 'intern'
            else:
                job_type='fulltime'
            portal_user_id = random.choice(portal_user_ids)
            posted_by_user = PortalUser.objects.get(id=portal_user_id)
            job = Job.objects.create(
                title=row[0],
                short_description=row[3],
                long_description=row[4],
                location=row[2],
                company_name=row[1],
                posted_by=posted_by_user,
                pay_offered=pay_offered,
                status='active',
                skills_required=skills_required,
                job_offer_type= job_type,
                posted_on=timezone.now()
            )
add_jobs_to_database()