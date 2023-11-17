# import random
# import os
# import sys
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# django.setup()

# from apis.models import StudentsDetails

# students = StudentsDetails.objects.all()
    
# for student in students:
#         skills = list(student.skillset)  # Convert skillset to a list
#         random.shuffle(skills)  # Shuffle the skills list
#         selected_skills = skills[:3]  # Select the first 3 skills
#         fskill = selected_skills[0].replace(" ","")
#         # Remove the "-" from the first skill (if present)
#         formatted_title = (fskill.replace("-", "") + "-" + "-".join(selected_skills[1:]).replace(" ",""))
#         fformatted_title = formatted_title.replace("+","-plus")
#         formatted_title2 = formatted_title.replace("-",",")
#         print(fformatted_title)
#         print(formatted_title2)
import os
import textract
from django.conf import settings
from pytesseract import image_to_string
from PIL import Image
from pdf2image import convert_from_path
import sys
import django
import PyPDF2
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

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
            print(text)
            print(len([text]))
    except Exception as e:
        # Handle the case if there is an error extracting text from the PDF
        print(str(e))

    

def convert_pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

user_id = 19
resume_path = os.path.join(settings.MEDIA_ROOT, f'{user_id}.pdf')
if not os.path.isfile(resume_path):
        print('Resume not found for the user')
extract_text_from_pdf(resume_path)
    




