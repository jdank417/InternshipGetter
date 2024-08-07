import subprocess
import requests
import spacy
import logging
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Sheets setup
SERVICE_ACCOUNT_FILE = 'internshipgettersheets-eb1c49f87f8e.json'
SPREADSHEET_ID = '1dM45MfAPinEGYJlFy-UwXqrZ7GtSdvIl2z2YGxAcF_E'
SHEET_NAME = 'Sheet1'

# Setup Google Sheets API credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)


def initialize_google_sheet(spreadsheet_id, sheet_name):
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')

    sheet_exists = any(sheet['properties']['title'] == sheet_name for sheet in sheets)
    if not sheet_exists:
        # Add the new sheet
        body = {'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]}
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        # Add headers
        header_values = [['Title', 'Link']]
        body = {'values': header_values}
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=sheet_name + '!A1',
                                               valueInputOption='RAW', body=body).execute()
        logging.info(f"Created new sheet with headers.")


def get_existing_jobs(spreadsheet_id, sheet_name):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:A').execute()
    values = result.get('values', [])
    return [row[0] for row in values if row]


def add_job_to_google_sheet(spreadsheet_id, sheet_name, job_title, job_link):
    new_row = [[job_title, job_link]]
    body = {'values': new_row}
    service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:B',
                                           valueInputOption='RAW', body=body).execute()
    logging.info(f"Added job to Google Sheet: {job_title}")


# spaCy model setup
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Read resume content from file
try:
    with open('resume.txt', 'r') as file:
        resume_text = file.read()
except FileNotFoundError:
    logging.error("Error: 'resume.txt' not found.")
    resume_text = ""


def extract_keywords(text):
    doc = nlp(text.lower())  # Lowercase text to improve matching accuracy
    return [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]


def match_jobs_with_resume(job_descriptions, resume_text):
    if not resume_text:
        return []

    resume_keywords = extract_keywords(resume_text)
    job_matches = []

    for job in job_descriptions:
        job_text = job['title'] + " " + job['description']
        job_keywords = extract_keywords(job_text)
        combined_text = [" ".join(resume_keywords), " ".join(job_keywords)]

        vectorizer = TfidfVectorizer().fit_transform(combined_text)
        similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2]).flatten()[0]

        job_matches.append((similarity, job))

    # Sort by similarity score
    job_matches.sort(reverse=True, key=lambda x: x[0])
    return job_matches


def search_internships(api_key, cse_id, query, location, resume_text, spreadsheet_id, sheet_name, num_results=10):
    query_with_location = f"{query} in {location}"
    start_index = 1
    all_job_descriptions = []

    while len(all_job_descriptions) < num_results:
        url = f"https://www.googleapis.com/customsearch/v1?q={query_with_location}&key={api_key}&cx={cse_id}&start={start_index}"
        response = requests.get(url)

        if response.status_code == 200:
            results = response.json().get('items', [])
            if not results:
                logging.info("No more job descriptions found.")
                break

            job_descriptions = [{'title': item['title'], 'link': item['link'], 'description': item['snippet']} for item
                                in results]
            all_job_descriptions.extend(job_descriptions)

            start_index += 10  # Move to the next page
        else:
            logging.error(f"Error: {response.status_code} - {response.text}")
            break

    # Limit the number of job descriptions to the specified number of results
    all_job_descriptions = all_job_descriptions[:num_results]

    if not all_job_descriptions:
        logging.info("No job descriptions found.")
        return

    existing_jobs = get_existing_jobs(spreadsheet_id, sheet_name)
    matched_jobs = match_jobs_with_resume(all_job_descriptions, resume_text)

    for score, job in matched_jobs:
        if job['title'] not in existing_jobs:
            add_job_to_google_sheet(spreadsheet_id, sheet_name, job['title'], job['link'])
            print(
                f"Relevance: {score:.2f}\nTitle: {job['title']}\nLink: {job['link']}\nDescription: {job['description']}\n")
        else:
            logging.info(f"Job already listed: {job['title']}")


# Configuration
api_key = "AIzaSyBhMAy_EtBGOaTcVFi7pj1ad37pKjEGDqI"
cse_id = "61fcd2bdd7a354817"
query = "software engineering internship Spring 2025"
location = "Boston, MA"
spreadsheet_id = SPREADSHEET_ID
sheet_name = SHEET_NAME

# Initialize Google Sheet if necessary
initialize_google_sheet(spreadsheet_id, sheet_name)

search_internships(api_key, cse_id, query, location, resume_text, spreadsheet_id, sheet_name, num_results=50)
