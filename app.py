from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
import requests

# Constants
job_posting = 'New Grad'
event_name = 'new_grad'
sms_trigger_url = 'https://maker.ifttt.com/trigger/new_grad/with/key/biRPCs-8xjD_sq_NAlcN0dynwzvl1ALKIGB7kxX4F2A'
posting_url = "https://childrensmn.taleo.net/careersection/chc_nursing/jobsearch.ftl?lang=en&radiusType=M&searchExpanded=true&radius=1&jobfield=200126570"

def trigger_success_phone_call(url):
    params = {"value1": url}
    req = requests.post(url=sms_trigger_url, params=params)

def check_for_position(job_posts=[], url=posting_url):
    found = False
    num_jobs = len(job_posts)

    for job_post in job_posts:
        if job_posting.lower() in job_post.text.lower():
            found = True

    if found:
        print(job_posting + ' job was found!')
        trigger_success_phone_call(url)
        return int(num_jobs / 3)

    else:
        return int(num_jobs / 3)

def run_scrape():
    print('Scraping Childrens Minnesota job listings page.')
    print('====================================================')

    chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
    executable_path = str(os.environ.get('CHROMEDRIVER_PATH'))
    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--remote-debugging-port=9222')
    driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    driver.implicitly_wait(3000)
    driver.get(posting_url)

    num_jobs = 0

    # Wait for job postings to lazy load
    time.sleep(2)

    first_page = BeautifulSoup(driver.page_source, features="html.parser")
    job_posts = first_page.find_all('div', {"class": "absolute"})

    next_button = driver.find_element_by_id('next')
    next_button.click() 

    # Wait for job postings to lazy load
    time.sleep(2)
    jobs_scraped = check_for_position(job_posts=job_posts, url=driver.current_url)
    num_jobs += jobs_scraped

    second_page = BeautifulSoup(driver.page_source, features="html.parser")
    job_posts = second_page.find_all('div', {"class": "absolute"})

    jobs_scraped = check_for_position(job_posts=job_posts, url=driver.current_url)
    num_jobs += jobs_scraped

    print('Scraping ' + str(num_jobs) + ' nursing jobs')

    print('Job not found :(')

run_scrape()