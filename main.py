import subprocess
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure the spaCy model is downloaded
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
    print("Error: 'resume.txt' not found.")
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


def search_internships(api_key, cse_id, query, location, resume_text):
    query_with_location = f"{query} in {location}"
    url = f"https://www.googleapis.com/customsearch/v1?q={query_with_location}&key={api_key}&cx={cse_id}"
    response = requests.get(url)

    if response.status_code == 200:
        results = response.json().get('items', [])
        if not results:
            print("No job descriptions found.")
            return

        job_descriptions = [{'title': item['title'], 'link': item['link'], 'description': item['snippet']} for item in
                            results]

        matched_jobs = match_jobs_with_resume(job_descriptions, resume_text)

        for score, job in matched_jobs:
            print(
                f"Relevance: {score:.2f}\nTitle: {job['title']}\nLink: {job['link']}\nDescription: {job['description']}\n")
    else:
        print(f"Error: {response.status_code} - {response.text}")


# Configuration
api_key = "AIzaSyCmDTs2lWUqNrQqRCEorKI1umwTdRpcAqM"
cse_id = "61fcd2bdd7a354817"
query = "software engineering internship Spring 2025"
location = "Boston, MA"

search_internships(api_key, cse_id, query, location, resume_text)
