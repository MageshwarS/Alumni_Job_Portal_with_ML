import requests
from bs4 import BeautifulSoup

url = 'https://www.naukri.com/jobs-in-india-2?clusters=functionalAreaGid&functionAreaIdGid=3&functionAreaIdGid=5&functionAreaIdGid=8&experience=0'

# send a GET request to the specified URL
response = requests.get(url)

# parse the HTML content of the response using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# find all job tuples in the HTML code
job_tuples = soup.find_all('article', class_='jobTuple')

# iterate through each job tuple and extract the required data
for job in job_tuples:
    # extract the job title
    job_title = job.find('a', class_='title').text.strip()

    # extract the company name
    company_name = job.find('a', class_='subTitle').text.strip()

    # extract the city
    city = job.find('li', class_='location').text.strip()

    # extract the skills
    skills = [skill.text.strip() for skill in job.find_all('li', class_='dot')]

    # extract the pay
    pay = job.find('li', class_='salary').text.strip()

    # extract the job description
    job_description = job.find('div', class_='job-description').text.strip()

    # print the extracted data
    print('Job Title:', job_title)
    print('Company Name:', company_name)
    print('City:', city)
    print('Skills:', skills)
    print('Pay:', pay)
    print('Job Description:', job_description)
    print('-----------------------')
