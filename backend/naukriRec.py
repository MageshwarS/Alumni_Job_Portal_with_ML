import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import sys
import django
from django.http import JsonResponse
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from apis.models import StudentsDetails, PortalUser
from jobs.models import OtherJobs, OtherPortals, Job

# def naukri_recommended_jobs():
#     job_data = []
#     count = 20
#     cities = ['Chennai', 'Delhi', 'Mumbai', 'Kolkata', 'Bangalore', 'Hyderabad']
#     students = StudentsDetails.objects.all()
#     other_portal = OtherPortals.objects.get(id=1)

#     for student in students:
#         driver = webdriver.Chrome()
#         wait = WebDriverWait(driver, 30)
#         skills = list(student.skillset)
#         random.shuffle(skills)
#         selected_skills = skills[:3]  
#         fskill = selected_skills[0].replace(" ","")
#         formatted_title = fskill.replace("-", "") + "-" + "-".join(selected_skills[1:]).replace(" ","")
#         fformatted_title = formatted_title.replace("+","-plus")
#         formatted_title2 = formatted_title.replace("-",",")
#         cities = ['Chennai', 'Delhi', 'Mumbai', 'Kolkata', 'Bangalore', 'Hyderabad']
#         location = random.choice(cities).lower()
#         url = f"https://www.naukri.com/{fformatted_title.lower()}-jobs-in-{location.lower()}?k={formatted_title2.lower()}&l={location}&experience={0}"
#         driver.get(url)

#         index, new_index, i = '0', 1, 0
#         heading_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/div/a'
#         link_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/a'
#         subheading_xpath = '(//*[@class="jobTuple"])['+index+']/div/div/div/a'
#         experience_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[1]/span[1]'
#         location_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[3]/span'
#         salary_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/div[1]/ul/li[2]/span[1]'
#         skills_xpath = '/html/body/div/div[4]/div/div/section[2]/div[2]/article['+index+']/ul/li'
#         desc_xpath = '/html/body/div[1]/div[4]/div/div/section[2]/div[2]/article['+index+']/div[2]'

#         while i < count:
#             for j in range(20):
#                 soup = BeautifulSoup(driver.page_source)
#                 ul_tags = soup.find_all("ul", {"class":"tags has-description"})

#                 temp_index = str(new_index).zfill(2)
#                 heading_xpath = heading_xpath.replace(index, temp_index)
#                 link_xpath = link_xpath.replace(index, temp_index)
#                 subheading_xpath = subheading_xpath.replace(index, temp_index)
#                 experience_xpath = experience_xpath.replace(index, temp_index)
#                 salary_xpath = salary_xpath.replace(index, temp_index)
#                 skills_xpath = skills_xpath.replace(index, temp_index)
#                 desc_xpath = desc_xpath.replace(index, temp_index)
#                 location_xpath = location_xpath.replace(index, temp_index)
#                 index = str(new_index).zfill(2)

#                 try:
#                     heading = wait.until(EC.presence_of_element_located((By.XPATH, heading_xpath))).text
#                 except:
#                     heading = "NULL"

#                 try:
#                     link = wait.until(EC.presence_of_element_located((By.XPATH, link_xpath))).get_attribute('href')
#                 except:
#                     link = "NULL"
                

#                 try:
#                     subheading = wait.until(EC.presence_of_element_located((By.XPATH, subheading_xpath))).text
#                 except:
#                     subheading = "NULL"

#                 try:
#                     desc = wait.until(EC.presence_of_element_located((By.XPATH, desc_xpath))).text
#                 except:
#                     desc = "NULL"

#                 try:
#                     location = wait.until(EC.presence_of_element_located((By.XPATH, location_xpath))).text
#                     city_list = location.split(',')
#                     location = city_list[0].strip()
#                 except:
#                     location = "NULL"

#                 try:
#                     experience = wait.until(EC.presence_of_element_located((By.XPATH, experience_xpath))).text
#                 except:
#                     experience = "NULL"

#                 try:
#                     salary = wait.until(EC.presence_of_element_located((By.XPATH, salary_xpath))).text
#                 except:
#                     salary = "Not Disclosed"

#                 try:
#                     li_tags = ul_tags[j].find_all("li")
#                     skills = [li.text for li in li_tags]
#                 except:
#                     skills = None
#                 if skills:
#                     job = OtherJobs(
#                         title=heading,
#                         company_name=subheading,
#                         location=location,
#                         description=desc,
#                         link=link,
#                         experience_needed=experience,
#                         salary=salary,
#                         skills_required=skills,
#                         other_portal=other_portal
#                     )
#                     check = OtherJobs.objects.filter(link=link).first()
#                     if not check:
#                         job.save()
#                         job_data.append(job)
#                     else:
#                         print("Already scrapped")
#                     new_index += 1
#                     i += 1

#                 if i >= count:
#                     break
#             if i >= count:
#                 break

#         driver.quit()

#     return job_data

# jobss = naukri_recommended_jobs()

#linkedin to other_jobs
# import random
# from django.utils import timezone
# def linkedin_jobs():
#     keywords = ''
#     location = ''
#     start = 0
#     cities = ['Chennai', 'Delhi', 'Mumbai', 'Kolkata', 'Bangalore', 'Hyderabad']
#     students = StudentsDetails.objects.all()
#     # other_portal = OtherPortals.objects.get(id=2)
#     portal_user_ids = [33, 34, 35, 39]
#     count = 0

#     for student in students:
#         skills = list(student.skillset)
#         random.shuffle(skills)
#         selected_skills = skills[:3]  
#         fskill = selected_skills[0].replace(" ","").lower()
#         formatted_title = fskill.replace("-", "") + "-" + "-".join(selected_skills[1:]).replace(" ","")
#         fformatted_title = formatted_title.replace("+","-plus")
#         keywords = formatted_title.replace("-",",").lower()
#         cities = ['Chennai', 'Bangalore']
#         location = random.choice(cities).lower()
#         url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={keywords}&location={location}&position=1&pageNum=0&start={start}'
#         response = requests.get(url)
#         print(url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         job_listings = soup.find_all('li')

#         jobs = []
#         for listing in job_listings:
#             pay_offered = random.randint(500000 // 1000, 1000000 // 1000) * 1000
#             title = listing.find('h3', class_='base-search-card__title').text.strip()
#             company = listing.find('h4', class_='base-search-card__subtitle').text.strip()
#             location = listing.find('span', class_='job-search-card__location').text.strip()
#             # link = listing.find('a', class_='base-card__full-link')['href']
#             link_element = listing.find('a', class_='base-card__full-link')
#             link = link_element['href'] if link_element else ''
#             count=count +3
#             if count % 9 == 0:
#                 job_type = 'intern'
#             else:
#                 job_type='fulltime'
#             portal_user_id = random.choice(portal_user_ids)
#             posted_by_user = PortalUser.objects.get(id=portal_user_id)

#             jobs.append({
#                 'title': title,
#                 'company': company,
#                 'location': location,
#                 'link': link
#             })
#             job = Job(
#                 title=title,
#                 short_description=link,
#                 long_description=link,
#                 location=location,
#                 company_name=company,
#                 posted_by=posted_by_user,
#                 pay_offered=pay_offered,
#                 status='active',
#                 skills_required=keywords.split(","),
#                 job_offer_type= job_type,
#                 posted_on=timezone.now()
#             )
#             check = Job.objects.filter(short_description=link).first()
#             if not check:
#                 job.save()
#                 # jobs.append(job)
#             else:
#                 print("Already scrapped")
#             print(title)
#     return JsonResponse({'jobs': jobs})
# linkedin_jobs()


from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from django.http import JsonResponse
from apis.models import StudentsDetails
from jobs.models import Application, Job, Clicked, OtherJobs
from django.conf import settings

def get_collaborative_recommendations(user_id):
    # user_id = request.GET.get('user_id')
    # print(user_id)
    try:
        # Check if resume exists for the given user_id
        resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
        if os.path.exists(resume_path):
            user_has_resume = True
            print("exists")
        else:
            user_has_resume = False
            # print("nope")
    except Exception as e:
        return JsonResponse({'error': str(e)})

 
    student = StudentsDetails.objects.get(user__id=user_id)

    similar_students = StudentsDetails.objects.exclude(user__id=user_id)

    recommended_students = []
    
    for similar_student in similar_students:
        print(similar_student.user_id)
        similarity_score = tfidf_similarity_student(student, similar_student, user_has_resume)
        recommended_students.append((similar_student, similarity_score))

    recommended_students.sort(key=lambda x: x[1], reverse=True)
    recommended_students = recommended_students[:10]  
    user_applied_job_ids = set(Application.objects.filter(created_by=user_id).values_list('job_id', flat=True))
    top_similar_students = []
    for similar_student, _ in recommended_students:
        student_applied_job_ids = set(Application.objects.filter(created_by=similar_student.user_id).values_list('job_id', flat=True))
        common_job_ids = user_applied_job_ids.intersection(student_applied_job_ids)
        if len(common_job_ids) >0:
            top_similar_students.append((similar_student, len(common_job_ids)))


    top_similar_students.sort(key=lambda x: x[1], reverse=True)


    top_similar_students = top_similar_students[:5]
    print("top:",top_similar_students)

    recommended_students_names = [ student.user_id for student, _ in top_similar_students]
    print(recommended_students_names)
    colrecommended_jobs = []
    

    for uid in recommended_students_names:
        appl = Application.objects.filter(created_by = uid)
        for ap in appl:
            job_id = ap.job_id
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
        ' '.join(student1.skillset),  
    ]
    
    feature_vector2 = [
        ' '.join(student2.skillset), 
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
        student1_resume = os.path.join(settings.MEDIA_ROOT, f'{student1.user_id}.pdf')
        user_resume = extract_text_from_pdf(student1_resume)
        student2_resume = os.path.join(settings.MEDIA_ROOT, f'{student2.user_id}.pdf')
        if os.path.exists(student2_resume):
            similar_student_resume = extract_text_from_pdf(student2_resume)
        
            similarity_score = compute_tfidf_similarity(user_resume, similar_student_resume)
        else:
            similarity_score = cosine_similarity_student(student1, student2)
    else:
        similarity_score = cosine_similarity_student(student1, student2)
    print(similarity_score)
    return similarity_score

import PyPDF2
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)

            text = []
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text.append(page.extract_text())

            text = ''.join(text)
        return text
    except Exception:
        return 


# def compute_tfidf_similarity(text1, text2):
#     vectorizer = TfidfVectorizer()
#     matrix1 = vectorizer.fit_transform([text1])
#     matrix2 = vectorizer.fit_transform([text2])

#     similarity_score = linear_kernel(matrix1,matrix2).flatten()
#     return similarity_score

def compute_tfidf_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    matrix1 = vectorizer.fit_transform([text1])
    matrix2 = vectorizer.transform([text2])

    similarity_score = cosine_similarity(matrix1, matrix2).flatten()
    return similarity_score




a= get_collaborative_recommendations(19)
print(a.content)