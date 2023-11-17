import requests
from bs4 import BeautifulSoup

def scrape_job_details(url, keyword, location):
    # Add headers to mimic a legitimate user request
    headers = {
    "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Create a BeautifulSoup object with the response content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all job listings on the page
    job_listings = soup.find_all('div', class_='jobsearch-SerpJobCard')

    # Iterate over each job listing and extract relevant details
    for job in job_listings:
        job_title = job.find('a', class_='jobtitle').text.strip()
        job_location = job.find('div', class_='location').text.strip()
        job_description = job.find('div', class_='summary').text.strip()

        # Check if the keyword and location match the job listing
        if keyword.lower() in job_title.lower() and location.lower() in job_location.lower():
            print("Job Title:", job_title)
            print("Location:", job_location)
            print("Description:", job_description)

            # Check if pay information is available
            pay_element = job.find('span', class_='salaryText')
            if pay_element:
                pay_offered = pay_element.text.strip()
                print("Pay Offered:", pay_offered)

            print()

# User inputs
keyword = "python"
location = "Chennai"

# Construct the URL with the keyword and location
url = f"https://in.indeed.com/jobs?q={keyword}&l={location}"

# Call the function to scrape job details
scrape_job_details(url, keyword, location)
