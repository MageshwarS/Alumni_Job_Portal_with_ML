"""from bs4 import BeautifulSoup
import csv

# Read the HTML file
with open('sample.html', 'r') as f:
    html = f.read()

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find all job postings
job_postings = soup.find_all('div', {'class': 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card'})

# Define the CSV file name and headers
csv_file = 'job_postings.csv'
headers = ['Job Title', 'Company Name', 'Location', 'Posting Date']

# Open the CSV file for writing and write the headers
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    # Loop through each job posting and extract the data
    for job in job_postings:
        # Extract the job title
        title_elem = job.find('h3', class_='base-search-card__title')
        title = title_elem.text.strip() if title_elem else ''
    
        # Extract the company name
        company_elem = job.find('a', class_='hidden-nested-link')
        company = company_elem.text.strip() if company_elem else ''
    
        # Extract the location
        location_elem = job.find('span', class_='job-search-card__location')
        location = location_elem.text.strip() if location_elem else ''
    
        # Extract the posting date
        date_elem = job.find('time', class_='job-search-card__listdate')
        date = date_elem['datetime'].strip() if date_elem and 'datetime' in date_elem.attrs else ''

        # Write the data to the CSV file
        writer.writerow([title, company, location, date])

print(f"Data has been scraped and stored in {csv_file}")"""

"""
import csv
import requests
from bs4 import BeautifulSoup

file = open('linkedin-jobs.csv', 'a')
writer = csv.writer(file)
writer.writerow(['Title', 'Company', 'Location', 'Apply'])

def linkedin_scraper(webpage, page_number):
    next_page = webpage + str(page_number)
    print(str(next_page))
    response = requests.get(str(next_page))
    soup = BeautifulSoup(response.content,'html.parser')
    jobs = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')

    for job in jobs:
        job_title = job.find('h3', class_='base-search-card__title').text.strip()
        job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
        job_location = job.find('span', class_='job-search-card__location').text.strip()
        job_link = job.find('a', class_='base-card__full-link')['href']
        writer.writerow([job_title.encode('utf-8'),job_company.encode('utf-8'),job_location.encode('utf-8'),job_link.encode('utf-8')])

    print('Data updated')

    if page_number < 25:
        page_number = page_number + 25
        linkedin_scraper(webpage, page_number)
    else:
        file.close()
        print('File closed')
linkedin_scraper('https://in.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location=India&locationId=&geoId=102713980&f_TPR=&f_C=91921%2C3642141%2C8710%2C9215331%2C1033%2C1090%2C3586%2C1283%2C157240%2C1441%2C38373%2C22328119%2C407872&position=1&pageNum=0&start=', 0)
"""


import csv
import requests
from bs4 import BeautifulSoup

with open('naukrjobs.csv', 'a') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Company', 'Location', 'Apply'])
"""
    def linkedin_scraper(webpage, page_number):
        next_page = webpage + str(page_number)
        print(str(next_page))
        response = requests.get(str(next_page))
        soup = BeautifulSoup(response.content,'html.parser')
        jobs = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')

        for job in jobs:
            job_title = job.find('h3', class_='base-search-card__title').text.strip()
            job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
            job_location = job.find('span', class_='job-search-card__location').text.strip().split(',')[0].strip()
            job_link = job.find('a', class_='base-card__full-link')['href']
            writer.writerow([job_title, job_company, job_location, job_link])

        print('Data updated')

        if page_number < 25:
            page_number = page_number + 25
            linkedin_scraper(webpage, page_number)
        else:
            print('File closed')

    linkedin_scraper('https://in.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location=India&locationId=&geoId=102713980&f_TPR=&f_C=91921%2C3642141%2C8710%2C9215331%2C1033%2C1090%2C3586%2C1283%2C157240%2C1441%2C38373%2C22328119%2C407872&position=1&pageNum=0&start=', 0)
"""

def linkedin_scraper(webpage, page_number, writer):
    next_page = webpage + str(page_number)
    print(str(next_page))
    response = requests.get(str(next_page))
    soup = BeautifulSoup(response.content,'html.parser')
    jobs = soup.find_all('article', class_='jobTuple')

    for job in jobs:
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

        # writer.writerow([job_title, company_name, city, skills, pay, job_description])

    print('Data updated')

    if page_number < 25:
        page_number = page_number + 25
        linkedin_scraper(webpage, page_number, writer)
    else:
        print('Scraping complete')


file = open('linkedin_jobs.csv', 'w', newline='', encoding='utf-8')
writer = csv.writer(file)
writer.writerow(['Job Title', 'Company', 'Location', 'Primary Skills', 'Job Link'])

linkedin_scraper('https://www.naukri.com/jobs-in-india-2?clusters=functionalAreaGid&functionAreaIdGid=3&functionAreaIdGid=5&functionAreaIdGid=8&experience=', 0, writer)

file.close()
print('File closed')
