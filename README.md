Google Sheet Link: https://docs.google.com/spreadsheets/d/1dM45MfAPinEGYJlFy-UwXqrZ7GtSdvIl2z2YGxAcF_E/edit?usp=sharing 

# Internship Search Automation

## Overview
This script automates the search for software engineering internships, matches the job postings with your resume, and updates a Google Sheet with the relevant job details.

## Components
1. **Google Sheets API Setup**: Initializes Google Sheets API, creates a sheet if it doesn’t exist, and updates it with new job postings.
2. **SpaCy for NLP**: Uses SpaCy for keyword extraction from job descriptions and your resume.
3. **TF-IDF and Cosine Similarity**: Matches job postings with your resume based on keyword similarity.
4. **Google Custom Search API**: Searches for internships using Google Custom Search.

## Setup
1. **Google Sheets API**:
   - Create a Google Sheets API project and obtain a service account JSON file.
   - Replace `SERVICE_ACCOUNT_FILE` with the path to your service account file.

2. **Google Custom Search API**:
   - Create a Custom Search Engine (CSE) and obtain an API key.
   - Replace `api_key` and `cse_id` with your API key and CSE ID.

3. **SpaCy Model**:
   - Ensure SpaCy is installed: `pip install spacy`.
   - Download the SpaCy model if not already installed: `python -m spacy download en_core_web_sm`.

4. **Resume File**:
   - Place your resume in a file named `resume.txt` in the same directory as the script.

## Usage
1. **Initialize Google Sheet**:
   - The script will check for the specified sheet and create it if necessary.

2. **Search for Internships**:
   - Customize the `query`, `location`, and `num_results` parameters in the script as needed.
   - Run the script: `python script_name.py`.

## Dependencies
- `requests`
- `spacy`
- `pandas`
- `sklearn`
- `google-auth`
- `google-api-python-client`


