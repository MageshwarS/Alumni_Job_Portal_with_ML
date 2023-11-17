from rest_framework import serializers

from jobs.models import Job
from apis.models import AlumniDetails

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


class AlumniJobDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniDetails
        fields = ['user_id', 'name', 'email', 'mobile_no']

class JobDataSerializer(serializers.ModelSerializer):
    posted_by = AlumniJobDetailsSerializer()

    class Meta:
        model = Job
        fields = ['id', 'title', 'job_offer_type', 'company_name', 'location', 'skills_required', 'pay_offered', 'posted_by', 'posted_on']
