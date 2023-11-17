from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Func, Value
from .forms import AddJobForm
from .serializers import JobSerializer, AlumniJobDetailsSerializer, JobDataSerializer
from .models import Job, Application, OtherPortals, OtherJobs, Clicked
from apis.models import StudentsDetails, AlumniDetails, PortalUser
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from django.core.mail import send_mail
from django.core.mail import EmailMessage
from backend.settings import EMAIL_HOST_USER

from django.db.models import Q
from django.views.decorators.http import require_GET

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.metrics import pairwise_distances

from django.views.decorators.csrf import csrf_exempt
import json

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import os
import textract
from django.conf import settings
from pytesseract import image_to_string
from PIL import Image
from pdf2image import convert_from_path
import PyPDF2

from nltk.corpus import stopwords

# Create your views here.


# def job_list(request):
#     jobs = Job.objects.filter(status='active')
#     serialized_jobs = []
#     for job in jobs:
#         serialized_jobs.append({
#             'id': job.id,
#             'title': job.title,
#             'location': job.location,
#             'job_offer_type': job.job_offer_type,
#             'company_name': job.company_name,
#         })
#     return JsonResponse({'jobs': serialized_jobs})


def click_update(request):
    user_id = request.GET.get('user_id')
    other_job = request.GET.get('other_job_id')
    student = StudentsDetails.objects.get(user = user_id)
    clicked = Clicked.objects.filter(created_by = user_id, other_job = other_job).first()
    if not clicked:
        Clicked.objects.create(created_by = user_id, other_job = other_job)

@csrf_exempt
def click_job(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            other_job = data.get('other_job_id')
            # experience = data.get('experience')

            if user_id and other_job:
                try:
                    job = OtherJobs.objects.get(id=other_job)
                    stu = PortalUser.objects.get(id=user_id)
                    # Check if the student has already applied for the job
                    # stu = StudentsDetails.objects.get(user=st)


                    already_clicked = Clicked.objects.filter(other_job=job, created_by=stu).exists()
                    if not already_clicked:
                        application = Clicked(other_job=job, created_by=stu)
                        application.save()
                    

                    return JsonResponse({'message': 'Application submitted successfully'})

                except Job.DoesNotExist:
                    return JsonResponse({'error': 'Invalid job ID'}, status=400)

                except PortalUser.DoesNotExist:
                    return JsonResponse({'error': 'Invalid student ID'}, status=400)

            # return JsonResponse({'error': 'Invalid parameters'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_ncollaborative_recommendations(request):
    user_id = request.GET.get('user_id')
    try:
        # Check if resume exists for the given user_id
        resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
        if os.path.exists(resume_path):
            user_has_resume = True
            # print("exists")
        else:
            user_has_resume = False
            # print("nope")
    except Exception as e:
        return JsonResponse({'error': str(e)})

    # Get student details for the given user_id
    student = StudentsDetails.objects.get(user__id=user_id)

    # Find similar students based on skillset, branch, degree, and specialization
    similar_students = StudentsDetails.objects.exclude(user__id=user_id)
    # similar_students = similar_students.filter(branch=student.branch, specialization=student.specialization)

    recommended_students = []
    
    # Calculate tfidf similarity with similar students' resumes or details
    for similar_student in similar_students:
        # print(similar_student.user_id)
        similarity_score = tfidf_similarity_student(student, similar_student, user_has_resume)
        recommended_students.append((similar_student, similarity_score))

    recommended_students.sort(key=lambda x: x[1], reverse=True)
    recommended_students = recommended_students[:10]  # Select top 2 recommended students
    user_applied_job_ids = set(Clicked.objects.filter(created_by=user_id).values_list('other_job_id', flat=True))
    top_similar_students = []
    for similar_student, _ in recommended_students:
        student_applied_job_ids = set(Clicked.objects.filter(created_by=similar_student.user_id).values_list('other_job_id', flat=True))
        common_job_ids = user_applied_job_ids.intersection(student_applied_job_ids)
        top_similar_students.append((similar_student, len(common_job_ids)))

    # Sort the top similar students by the number of common job applications in descending order
    top_similar_students.sort(key=lambda x: x[1], reverse=True)

    # Select the top 5 similar students
    top_similar_students = top_similar_students[:5]
    # print("top:",top_similar_students)

    # Prepare response with recommended students' names
    recommended_students_names = [ student.user_id for student, _ in top_similar_students]
    # print(recommended_students_names)
    colrecommended_jobs = []
    

    for uid in recommended_students_names:
        appl = Clicked.objects.filter(created_by = uid)
        for ap in appl:
            job = OtherJobs.objects.get(id=ap.other_job.id)
            colrecommended_jobs.append({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'skills_required': job.skills_required,
            'location': job.location,
            'company_name': job.company_name,
            'salary': job.salary,
            'link': job.link,
            'experience_needed': job.experience_needed
        })
    # print(len(colrecommended_jobs))
    # print(colrecommended_jobs)
    return JsonResponse(colrecommended_jobs, safe=False)

def get_collaborative_recommendations(request):
    user_id = request.GET.get('user_id')
    # print(user_id)
    try:
        # Check if resume exists for the given user_id
        resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
        if os.path.exists(resume_path):
            user_has_resume = True
        else:
            user_has_resume = False
            # print("nope")
    except Exception as e:
        return JsonResponse({'error': str(e)})

    student = StudentsDetails.objects.get(user__id=user_id)

    similar_students = StudentsDetails.objects.exclude(user__id=user_id)
    # similar_students = similar_students.filter(branch=student.branch, specialization=student.specialization)

    recommended_students = []
    
    for similar_student in similar_students:
        similarity_score = tfidf_similarity_student(student, similar_student, user_has_resume)
        recommended_students.append((similar_student, similarity_score))

    recommended_students.sort(key=lambda x: x[1], reverse=True)
    recommended_students = recommended_students[:10]  
    user_applied_job_ids = set(Application.objects.filter(created_by=user_id).values_list('job_id', flat=True))
    top_similar_students = []
    for similar_student, _ in recommended_students:
        student_applied_job_ids = set(Application.objects.filter(created_by=similar_student.user_id).values_list('job_id', flat=True))
        common_job_ids = user_applied_job_ids.intersection(student_applied_job_ids)
        if common_job_ids:
            top_similar_students.append((similar_student, len(common_job_ids)))


    top_similar_students.sort(key=lambda x: x[1], reverse=True)

 
    top_similar_students = top_similar_students[:5]

 
    recommended_students_names = [ student.user_id for student, _ in top_similar_students]
    colrecommended_jobs = []
    

    for uid in recommended_students_names:
        appl = Application.objects.filter(created_by = uid)
        for ap in appl:
            job_id = ap.job.id
            if job_id not in user_applied_job_ids:
                job = Job.objects.get(id=job_id)
                colrecommended_jobs.append({
            'id': job.id,
            'title': job.title,
            'short_description': job.short_description,
            'skills_required': job.skills_required,
            'job_offer_type': job.job_offer_type,
            'location': job.location,
            'company_name': job.company_name,
            'pay_offered': job.pay_offered,
        })
    # print(len(colrecommended_jobs))
    # print(colrecommended_jobs)
    return JsonResponse(colrecommended_jobs, safe=False)


def cosine_similarity_student(student1, student2):
    feature_vector1 = [
        ' '.join(student1.skillset),  # Convert char[] to string
    ]
    
    feature_vector2 = [
        ' '.join(student2.skillset),  # Convert char[] to string
    ]
    
    vectorizer = CountVectorizer()
    combined_features = feature_vector1 + feature_vector2
    feature_matrix = vectorizer.fit_transform(combined_features)
    
    # Extract the feature vectors
    feature_vector1 = feature_matrix.getrow(0)
    feature_vector2 = feature_matrix.getrow(1)
    
    # Calculate cosine similarity
    similarity_score = cosine_similarity(feature_vector1, feature_vector2)[0][0]
    # print(similarity_score)
    
    return similarity_score



def tfidf_similarity_student(student1, student2, user_has_resume):
    if user_has_resume:
        # Calculate tfidf similarity using texts from user's resume and similar student's resume
        student1_resume = os.path.join(settings.MEDIA_ROOT, f'{student1.user_id}.pdf')
        user_resume = extract_text_from_pdf(student1_resume)
        student2_resume = os.path.join(settings.MEDIA_ROOT, f'{student2.user_id}.pdf')
        if os.path.exists(student2_resume):
            similar_student_resume = extract_text_from_pdf(student2_resume)
        
            similarity_score = compute_tfidf_similarity(user_resume, similar_student_resume)
        else:
            similarity_score = cosine_similarity_student(student1, student2)
    else:
        # Calculate tfidf similarity based on student details from the table
        similarity_score = cosine_similarity_student(student1, student2)
    
    return similarity_score

def compute_tfidf_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    matrix1 = vectorizer.fit_transform([text1])
    matrix2 = vectorizer.transform([text2])

    similarity_score = cosine_similarity(matrix1, matrix2).flatten()
    return similarity_score

job_indices = {}  
Naukri_job_indices = {}
stop_words = list(stopwords.words('english'))
def preprocess_naukri_job_data():
    job_data = OtherJobs.objects.filter(other_portal__id=1).values('id', 'title','company_name', 'location', 'description', 'skills_required')

    job_contents = []
    for job in job_data:
        content = job['title'] + " " + job['description'] + " " + ", ".join(job['skills_required'])
        content_without_stopwords = ' '.join([word for word in content.split() if word.lower() not in stop_words])
        job_contents.append(content_without_stopwords)
        # job_contents.append(content)
        Naukri_job_indices[job['id']] = len(job_contents) - 1

    vectorizer = CountVectorizer(stop_words=stop_words)
    job_matrix = vectorizer.fit_transform(job_contents)

    return job_matrix, vectorizer
def preprocess_naukri_job_data2():
    job_data = OtherJobs.objects.filter(other_portal__id=1).values('id', 'title','company_name', 'location', 'description', 'skills_required')

    job_contents = []
    for job in job_data:
        content = job['title'] + " " + job['description'] + " " + ", ".join(job['skills_required'])
        content_without_stopwords = ' '.join([word for word in content.split() if word.lower() not in stop_words])
        job_contents.append(content_without_stopwords)
        # job_contents.append(content)
        Naukri_job_indices[job['id']] = len(job_contents) - 1

    vectorizer2 = TfidfVectorizer(stop_words=stop_words)
    job_matrix2 = vectorizer2.fit_transform(job_contents)

    return job_matrix2, vectorizer2

def jaccard_similarity(X, Y):
    X_dense = X.toarray()
    Y_dense = Y.toarray()
    return 1 - pairwise_distances(X_dense, Y_dense, metric='jaccard')

def get_naukri_recommendations(request):
    user_id = request.GET.get('user_id')
    resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
    try:
        text = extract_text_from_pdf(resume_path)
        if not text:
            student = StudentsDetails.objects.get(user= user_id)
            text = str(student.skillset) + str(student.branch)
    except Exception as e:
        return JsonResponse({'error': str(e)})

    job_matrix, vectorizer = preprocess_naukri_job_data()
    job_matrix2, vectorizer2 = preprocess_naukri_job_data2()

    input_matrix = vectorizer.transform([text])
    input_matrix2 = vectorizer2.transform([text])
    cosine_similarity_scores = cosine_similarity(job_matrix, input_matrix).flatten()
    tfid_similarity_scores = linear_kernel(job_matrix2, input_matrix2).flatten()
    jaccard_similarity_scores = jaccard_similarity(job_matrix, input_matrix).flatten()

    similarity_scores_combined = (0.4 * cosine_similarity_scores) + (0.4* tfid_similarity_scores) + (0.2 * jaccard_similarity_scores)

    # similarity_scores_combined = (0.4 * cosine_similarity_scores) + (0.6 * tfid_similarity_scores)

    # nonzero_indices = similarity_scores.nonzero()[0]
    # nonzero_scores = similarity_scores[nonzero_indices]
    # top_indices = nonzero_indices[nonzero_scores.argsort()[::-1]]
    recommended_jobs = []
    for job_id, score in sorted(zip(Naukri_job_indices.keys(), similarity_scores_combined), key=lambda x: x[1], reverse=True):
        if score > 0.1:
            job = OtherJobs.objects.get(id=job_id)
            recommended_jobs.append({
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'skills_required': job.skills_required,
            'location': job.location,
            'company_name': job.company_name,
            'salary': job.salary,
            'link': job.link,
            'experience_needed': job.experience_needed
        })

    return JsonResponse(recommended_jobs, safe=False)

def get_location_suggestions(request):
    query = request.GET.get('query', '')

    cities = [
        'Chennai', 'Delhi', 'Mumbai', 'Kolkata', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Pune', 'Jaipur', 'Lucknow'
    ]
    
    suggestions = [city for city in cities if query.lower() in city.lower()]
    
    return JsonResponse(suggestions, safe=False)

def naukri_recommended_jobs(request, title, location):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)
    job_data = []
    formatted_title = title.replace(",", "-")
    url = f"https://www.naukri.com/{formatted_title.lower()}-jobs-in-{location.lower()}?k={title.lower()}&l={location.lower()}&experience={0}"
    driver.get(url)
    count = 10
    
    index, new_index, i = '0', 1, 0
    heading_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/div/a'
    link_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/a'
    subheading_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/div/a'
    experience_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[1]/span[1]'
    location_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[3]/span'
    salary_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[2]/span[1]'
    skills_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/ul/li'
    desc_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[2]'
    
    while i < count:
        for j in range(20):
            soup = BeautifulSoup(driver.page_source)
            ul_tags = soup.find_all("ul", {"class":"tags has-description"})
            
            temp_index = str(new_index).zfill(2)
            heading_xpath = heading_xpath.replace(index, temp_index)
            link_xpath = link_xpath.replace(index, temp_index)
            subheading_xpath = subheading_xpath.replace(index, temp_index)
            experience_xpath = experience_xpath.replace(index, temp_index)
            salary_xpath = salary_xpath.replace(index, temp_index)
            skills_xpath = skills_xpath.replace(index, temp_index)
            desc_xpath = desc_xpath.replace(index, temp_index)
            location_xpath = location_xpath.replace(index, temp_index)
            index = str(new_index).zfill(2)
            
            try:
                heading = wait.until(EC.presence_of_element_located((By.XPATH, heading_xpath))).text
            except:
                heading = "NULL"
            
            try:
                link = wait.until(EC.presence_of_element_located((By.XPATH, link_xpath))).get_attribute('href')
            except:
                link = "NULL"
            
            try:
                subheading = wait.until(EC.presence_of_element_located((By.XPATH, subheading_xpath))).text
            except:
                subheading = "NULL"
            
            try:
                desc = wait.until(EC.presence_of_element_located((By.XPATH, desc_xpath))).text
            except:
                desc = "NULL"
            
            try:
                location = wait.until(EC.presence_of_element_located((By.XPATH, location_xpath))).text
                city_list = location.split(',')
                location = city_list[0].strip()
            except:
                location = "NULL"
            
            try:
                experience = wait.until(EC.presence_of_element_located((By.XPATH, experience_xpath))).text
            except:
                experience = "NULL"
            
            try:
                salary = wait.until(EC.presence_of_element_located((By.XPATH, salary_xpath))).text
            except:
                salary = "Not Disclosed"
            
            try:
                li_tags = ul_tags[j].find_all("li")
                skills = [li.text for li in li_tags]
            except:
                skills = []
            
            job_dict = {
                'Heading': heading,
                'Company': subheading,
                'location': location,
                'description': desc,
                'Vacancy_Link': link,
                'Experience_Needed': experience,
                'Salary': salary,
                'skills': skills
            }
            job_data.append(job_dict)
    
            new_index += 1
            i += 1
    
            if i >= count:
                break
        if i >= count:
            break
        
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fright'))).click()
        new_index = 1
    
    driver.quit()
    return JsonResponse({'job_data':job_data}, safe=False)

# def naukri_jobs(request, title, location):
#     # options = Options()
#     # options.add_argument("--headless")
#     # options.add_argument("--no-sandbox")
#     # options.add_argument("--disable-gpu")
#     # driver = webdriver.Chrome(options=options)
#     driver = webdriver.Chrome()
#     wait = WebDriverWait(driver, 30)
#     job_data = []
#     url = f"https://www.naukri.com/{title.lower()}-jobs-in-{location.lower()}?k={title.lower()}&l={location.lower()}&experience={0}"
#     driver.get(url)
#     count = 60
    
#     index, new_index, i = '0', 1, 0
#     heading_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/div/a'
#     link_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/a'
#     subheading_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/div/a'
#     experience_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[1]/span[1]'
#     location_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[3]/span'
#     salary_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[2]/span[1]'
#     skills_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/ul/li'
#     desc_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[2]'
    
#     while i < count:
#         for j in range(20):
#             soup = BeautifulSoup(driver.page_source)
#             ul_tags = soup.find_all("ul", {"class":"tags has-description"})
            
#             temp_index = str(new_index).zfill(2)
#             heading_xpath = heading_xpath.replace(index, temp_index)
#             link_xpath = link_xpath.replace(index, temp_index)
#             subheading_xpath = subheading_xpath.replace(index, temp_index)
#             experience_xpath = experience_xpath.replace(index, temp_index)
#             salary_xpath = salary_xpath.replace(index, temp_index)
#             skills_xpath = skills_xpath.replace(index, temp_index)
#             desc_xpath = desc_xpath.replace(index, temp_index)
#             location_xpath = location_xpath.replace(index, temp_index)
#             index = str(new_index).zfill(2)
            
#             try:
#                 heading = wait.until(EC.presence_of_element_located((By.XPATH, heading_xpath))).text
#             except:
#                 heading = "NULL"
            
#             try:
#                 link = wait.until(EC.presence_of_element_located((By.XPATH, link_xpath))).get_attribute('href')
#             except:
#                 link = "NULL"
            
#             try:
#                 subheading = wait.until(EC.presence_of_element_located((By.XPATH, subheading_xpath))).text
#             except:
#                 subheading = "NULL"
            
#             try:
#                 desc = wait.until(EC.presence_of_element_located((By.XPATH, desc_xpath))).text
#             except:
#                 desc = "NULL"
            
#             try:
#                 location = wait.until(EC.presence_of_element_located((By.XPATH, location_xpath))).text
#                 city_list = location.split(',')
#                 location = city_list[0].strip()
#             except:
#                 location = "NULL"
            
#             try:
#                 experience = wait.until(EC.presence_of_element_located((By.XPATH, experience_xpath))).text
#             except:
#                 experience = "NULL"
            
#             try:
#                 salary = wait.until(EC.presence_of_element_located((By.XPATH, salary_xpath))).text
#             except:
#                 salary = "Not Disclosed"
            
#             try:
#                 li_tags = ul_tags[j].find_all("li")
#                 skills = [li.text for li in li_tags]
#             except:
#                 skills = []
            
#             job_dict = {
#                 'Heading': heading,
#                 'Company': subheading,
#                 'location': location,
#                 'description': desc,
#                 'Vacancy_Link': link,
#                 'Experience_Needed': experience,
#                 'Salary': salary,
#                 'skills': skills
#             }
#             job_data.append(job_dict)
    
#             new_index += 1
#             i += 1
    
#             if i >= count:
#                 break
#         if i >= count:
#             break
        
#         wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fright'))).click()
#         new_index = 1
    
#     driver.quit()
#     return JsonResponse({'job_data':job_data}, safe=False)

def linkedin_jobs(request):
    keywords = request.GET.get('keywords')
    location = request.GET.get('location')
    start = request.GET.get('start')
    url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&position=1&pageNum=0&start={start}'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_listings = soup.find_all('li')

    jobs = []
    for listing in job_listings:
        title = listing.find('h3', class_='base-search-card__title').text.strip()
        company = listing.find('h4', class_='base-search-card__subtitle').text.strip()
        location = listing.find('span', class_='job-search-card__location').text.strip()
        # link = listing.find('a', class_='base-card__full-link')['href']
        link_element = listing.find('a', class_='base-card__full-link')
        link = link_element['href'] if link_element else ''

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'link': link
        })

    return JsonResponse({'jobs': jobs})


@csrf_exempt
def apply_job(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_id = data.get('job')
            student_id = data.get('student')
            content = data.get('content')
            # experience = data.get('experience')

            if job_id and student_id:
                try:
                    job = Job.objects.get(id=job_id)
                    student = PortalUser.objects.get(id=student_id)
                    alumni = AlumniDetails.objects.get(user=job.posted_by)
                    stu = StudentsDetails.objects.get(user=student_id)
                    # Check if the student has already applied for the job
                    already_applied = Application.objects.filter(job=job, created_by=student).exists()
                    if already_applied:
                        return JsonResponse({'message': 'You have already applied for this job'})

                    # Create a new application
                    application = Application(job=job, created_by=student, content=content)
                    application.save()
                    send_mail(
                        subject=f"New Application for Job - {job.title}",
                        message=f"Hello {alumni.name},\n\n"
                                f"{stu.name}, {stu.branch}, has applied for the job '{job.title}' you have posted.\n\n"
                                f"Applicant's Skillset:{stu.skillset}\n"
                                f"Contact Information:\n"
                                f"  - Email: {stu.email}\n"
                                f"  - Phone Number: {stu.mobile_no}\n\n"
                                f"If hired, please delete the job posting.\n\n"
                                f"Here is a message from {stu.name}:\n"
                                f"{application.content}\n\n"
                                f"We hereby attach Applicant's resume link. Please check out.\n"
                                f"http://127.0.0.1:8000/resume_view/{stu.user_id}/ \n\n"
                                f"Thanks,\n"
                                f"IST ALUMNI_STUDENT Job Portal Team",
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[alumni.email],
                        fail_silently=False,
                    )

                    return JsonResponse({'message': 'Application submitted successfully'})

                except Job.DoesNotExist:
                    return JsonResponse({'error': 'Invalid job ID'}, status=400)

                except PortalUser.DoesNotExist:
                    return JsonResponse({'error': 'Invalid student ID'}, status=400)

            return JsonResponse({'error': 'Invalid parameters'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def preprocess_job_data():
    job_data = Job.objects.all().values('id', 'title','company_name', 'location', 'short_description', 'skills_required', 'job_offer_type', 'pay_offered')

    job_contents = []
    for job in job_data:
        content = job['title'] + " " + job['location'] + " " + job['short_description'] + " " + ", ".join(job['skills_required'])
        content_without_stopwords = ' '.join([word for word in content.split() if word.lower() not in stop_words])
        job_contents.append(content_without_stopwords)
        # job_contents.append(content)
        job_indices[job['id']] = len(job_contents) - 1

    vectorizer = CountVectorizer(stop_words=stop_words)
    job_matrix = vectorizer.fit_transform(job_contents)

    return job_matrix, vectorizer

def preprocess_job_data2():
    job_data = Job.objects.all().values('id', 'title','company_name', 'location', 'short_description', 'skills_required', 'job_offer_type', 'pay_offered')

    job_contents = []
    for job in job_data:
        content = job['title'] + " " + job['location'] + " " + job['short_description'] + " " + ", ".join(job['skills_required'])
        content_without_stopwords = ' '.join([word for word in content.split() if word.lower() not in stop_words])
        job_contents.append(content_without_stopwords)
        # job_contents.append(content)
        job_indices[job['id']] = len(job_contents) - 1

    vectorizer2 = TfidfVectorizer(stop_words=stop_words)
    job_matrix2 = vectorizer2.fit_transform(job_contents)

    return job_matrix2, vectorizer2

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)

            text = []
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text.append(page.extract_text())

            # Combine the extracted text from all pages
            text = ''.join(text)
        return text
    except Exception:
        # Handle the case if there is an error extracting text from the PDF
        return 

    

# def convert_pdf_to_images(pdf_path):
#     images = convert_from_path(pdf_path)
#     return images

def get_recommendations(request):
    user_id = request.GET.get('user_id')
    resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
    try:
        text = extract_text_from_pdf(resume_path)
        if not text:
            student = StudentsDetails.objects.get(user= user_id)
            text = str(student.skillset) + str(student.branch)
    except Exception as e:
        return JsonResponse({'error': str(e)})

    job_matrix, vectorizer = preprocess_job_data()

    input_matrix = vectorizer.transform([text])
    job_matrix2, vectorizer2 = preprocess_job_data2()
    input_matrix2 = vectorizer2.transform([text])
    cosine_similarity_scores = cosine_similarity(job_matrix, input_matrix).flatten()
    tfid_similarity_scores = linear_kernel(job_matrix2, input_matrix2).flatten()
    jaccard_similarity_scores = jaccard_similarity(job_matrix2, input_matrix2).flatten()

    # similarity_scores_combined = (0.4 * cosine_similarity_scores) + (0.6 * tfid_similarity_scores) 
    similarity_scores_combined = (0.3 * cosine_similarity_scores) + (0.5 * tfid_similarity_scores) + (0.2 * jaccard_similarity_scores)

    # nonzero_indices = similarity_scores.nonzero()[0]
    # nonzero_scores = similarity_scores[nonzero_indices]
    # top_indices = nonzero_indices[nonzero_scores.argsort()[::-1]]
    recommended_jobs = []
    
    # for job_id in top_indices:
    #     job = Job.objects.get(id=list(job_indices.keys())[list(job_indices.values()).index(job_id)])
    for job_id, score in sorted(zip(job_indices.keys(), similarity_scores_combined), key=lambda x: x[1], reverse=True):
        if score > 0.15:
            job = Job.objects.get(id=job_id)
            recommended_jobs.append({
            'id': job.id,
            'title': job.title,
            'short_description': job.short_description,
            'skills_required': job.skills_required,
            'job_offer_type': job.job_offer_type,
            'location': job.location,
            'company_name': job.company_name,
            'pay_offered': job.pay_offered,
            # 'text':text
        })

    return JsonResponse(recommended_jobs, safe=False)

def get_job_details(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        alumni = AlumniDetails.objects.get(user=job.posted_by)

        job_data = {
            'id': job.id,
            'title': job.title,
            'short_description': job.short_description,
            'job_offer_type': job.job_offer_type,
            'company_name': job.company_name,
            'location': job.location,
            'skills_required':job.skills_required,
            'pay_offered': str(job.pay_offered),
            'posted_by': {
                'user_id': alumni.user_id,
                'name': alumni.name,
                'email': alumni.email,
                'phone': alumni.mobile_no
            },
            'posted_on': job.posted_on
        }

        return JsonResponse(job_data)
    except (Job.DoesNotExist, AlumniDetails.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=404)

@require_GET
def filter_jobs(request):
    location = request.GET.get('location')
    company_name = request.GET.get('company_name')
    job_offer_type = request.GET.get('job_offer_type')
    title = request.GET.get('title')
    skills = request.GET.getlist('skills')
    sort_by = request.GET.get('sort_by')
    q = Q()

    if location:
         q &= Q(location=location)
    if company_name:
        q &= Q(company_name=company_name)
    if title:
        q &= Q(title=title)
    if job_offer_type:
        q &= Q(job_offer_type=job_offer_type)
    if skills:
        q &= Q(skills_required__overlap=skills)
    jobs = Job.objects.filter(q)
    if sort_by == 'latest':
        jobs = jobs.order_by('-posted_on')
    elif sort_by == 'oldest':
        jobs = jobs.order_by('posted_on')
    elif sort_by == 'high_pay':
        jobs = jobs.order_by('-pay_offered')

    data = {
        'jobs': [
            {
            'id': job.id,
            'title': job.title,
            'short_description': job.short_description,
            'location': job.location,
            'company_name': job.company_name,
            'pay_offered': job.pay_offered,
            'status': job.status,
            'skills_required': job.skills_required,
            'job_offer_type': job.job_offer_type,
            'posted_by': job.posted_by.id,
            'posted_on': job.posted_on.strftime('%Y-%m-%d %H:%M:%S')
            } for job in jobs
        ]
    }

    return JsonResponse(data)


@require_GET
def naukri_jobs(request):
    location = request.GET.get('location')
    company_name = request.GET.get('company_name')
    title = request.GET.get('title')
    skills = request.GET.getlist('skills')
    sort_by = request.GET.get('sort_by')
    q = Q()

    if location:
         q &= Q(location=location)
    if company_name:
        q &= Q(company_name=company_name)
    if title:
        q &= Q(title=title)
    if skills:
        q &= Q(skills_required__overlap=skills)
    jobs = OtherJobs.objects.filter(q)
    if sort_by == 'latest':
        jobs = jobs.order_by('-posted_on')
    elif sort_by == 'oldest':
        jobs = jobs.order_by('posted_on')

    data = {
        'jobs': [
            {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'location': job.location,
            'company_name': job.company_name,
            'pay_offered': job.salary,
            'experience_needed':job.experience_needed,
            'link': job.link,
            'skills_required': job.skills_required,
            'other_portal': job.other_portal.id,
            } for job in jobs
        ]
    }

    return JsonResponse(data)

def nexperience_needed_list(request):
    experience_needed = OtherJobs.objects.values_list('experience_needed', flat=True).distinct()
    return JsonResponse({'nexperience_needed': list(experience_needed)})

def nsalary_list(request):
    salary = OtherJobs.objects.values_list('salary', flat=True).distinct()
    return JsonResponse({'nsalary': list(salary)})

def nlocation_list(request):
    locations = OtherJobs.objects.values_list('location', flat=True).distinct()
    return JsonResponse({'locations': list(locations)})

def ncompany_list(request):
    companies = OtherJobs.objects.values_list('company_name', flat=True).distinct()
    return JsonResponse({'companies': list(companies)})

def location_list(request):
    locations = Job.objects.values_list('location', flat=True).distinct()
    return JsonResponse({'locations': list(locations)})

def company_list(request):
    companies = Job.objects.values_list('company_name', flat=True).distinct()
    return JsonResponse({'companies': list(companies)})


@login_required
def add_job(request):
    if request.method == 'POST':
        form = AddJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.status = 'active'

            job.save()
            return redirect('http://127.0.0.1:8000/add/')
    else:
        form = AddJobForm()
    
    return render(request, 'add_job.html', {'form': form})

def frontpage(request):
    jobs = Job.objects.filter(status='active').order_by('-posted_on')[0:3]

    return render(request, 'viewjobs.html', {'jobs': jobs})

class CountsView(APIView):
    def get(self, request):
        jobs_count = Job.objects.count()
        students_count = StudentsDetails.objects.count()
        employees_count = AlumniDetails.objects.count()
        data = {
            'jobs_count': jobs_count,
            'students_count': students_count,
            'employees_count': employees_count,
        }
        return Response(data)
class TotalCountsView(APIView):
    def get(self, request):
        jobs_count = Job.objects.count()

        data = {
            'jobs_count': jobs_count,
        }
        return Response(data)
@require_GET
def get_applied_counts(request, user_id):
    try:
        user = PortalUser.objects.get(id=user_id)
    except PortalUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid user ID'})
    
    applied_count = Application.objects.filter(created_by=user).count()
    
    return JsonResponse({
        'applied_count': applied_count,
    })
@require_GET
def get_job_counts(request, user_id):
    try:
        user = PortalUser.objects.get(id=user_id)
    except PortalUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid user ID'})
    
    active_count = Job.objects.filter(posted_by=user, status='active').count()
    employed_count = Job.objects.filter(posted_by=user, status='employed').count()
    total_count = Job.objects.filter(posted_by=user).count()
    
    return JsonResponse({
        'active_count': active_count,
        'employed_count': employed_count,
        'total_count': total_count
    })

def get_jobs_by_user(request, user_id):
    jobs = Job.objects.filter(posted_by=user_id)
    job_list = []
    for job in jobs:
        applications = Application.objects.filter(job=job)
        appl_list=[]
        for application in applications:
            stu =StudentsDetails.objects.get(user=application.created_by)
            appl ={
                'student_id': application.created_by.id,
                'student_name': stu.name,
                'branch': stu.branch,
                'created_at': application.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'message': application.content,
                'current_sem': stu.current_sem,
                'current_cgpa': stu.current_cgpa,
                'standing_arrears': stu.standing_arrears,
                'skillset': stu.skillset,
                'email': stu.email,
                'phone': stu.mobile_no,
            }
            appl_list.append(appl)
        job_dict = {
            'id': job.id,
            'title': job.title,
            'short_description': job.short_description,
            'location': job.location,
            'company_name': job.company_name,
            'pay_offered': job.pay_offered,
            'status': job.status,
            'skills_required': job.skills_required,
            'job_offer_type': job.job_offer_type,
            'posted_on': job.posted_on.strftime('%Y-%m-%d'),
            'applicants': appl_list
        }
        job_list.append(job_dict)
    return JsonResponse(job_list, safe=False)

class JobViewSet(generics.RetrieveUpdateDestroyAPIView):
    http_method_names = ['get', 'patch', 'delete']
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

class CreateJobView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        job = serializer.save()
        matching_students = StudentsDetails.objects.filter(skillset__overlap=job.skills_required)
        for student in matching_students:
            send_mail(
                subject=f"New Job Posting: {job.title}",
                message=f"Hello {student.name},\n\nA new job ({job.title}) has been posted on our job portal that matches your skillset. Please login to the portal to view the details http://localhost:8081/students .\n\nThanks,\nIST ALUMNI_STUDENT Job Portal Team",
                from_email=EMAIL_HOST_USER,
                recipient_list=[student.email],
                fail_silently=False,
            )

    
'''@login_required
def add_job(request):
    if request.method == 'POST':
        form = AddJobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.status = 'active'

            # Add skills_required field
            skills_required = request.POST.get('skills_required', '')
            skills = [s.strip() for s in skills_required.split(',')]
            job.skills_required = skills

            job.save()
            return redirect('http://127.0.0.1:8000/add/')
    else:
        form = AddJobForm()
    
    return render(request, 'add_job.html', {'form': form}) '''
