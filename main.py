import subprocess
import requests
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Your resume content
resume_text = """
Name: Jason Dank
Contact Information:
  - Phone: 631-603-8283
  - Location: Boston, MA
  - Email: dankj@wit.edu
  - LinkedIn: www.linkedin.com/in/jason-dank

Education:
  - Institution: Wentworth Institute of Technology, Boston, MA
  - Degree: Bachelor of Science in Computer Science
  - Graduation Date: Expected August 2026
  - GPA: 3.638
  - Honors: Dean's List (Fall 2022, Spring 2023, Fall 2023)
  - Minors: Business Analytics, Applied Mathematics, Data Science, Computer Networking
  - Relevant Courses:
    * Algorithms
    * Data Structures
    * Databases
    * Probability and Statistics for Engineers
    * Decision Analysis for Business
    * Network Programming (Python)
    * Computer Organization (LC-3 Assembly)
    * Linear Algebra and Matrix Theory
    * Macroeconomics

Skills:
  - Programming Languages: Java, Python, C++, SQLite, MySQL, LC-3 Assembly
  - Software and Tools: GitHub, GitBash, JetBrains IDEs, VS Code, Cisco CLI, Linux, Wireshark, Logisim, Oracle VM VirtualBox, VMware, Socket Programming
  - Operating Systems: Apple (iOS, WatchOS, MacOS, iPadOS, TvOS), Windows
  - IT Systems: SNOW, SCCM, Jamf, Asset Track

Projects:
  - Project Name: Stock Price Prediction System
    * Description: Developed an ensemble model combining LSTM, CNN, Conditional VAE, Random Forest, and XGBoost.
    * Features: Engineered features like RSI, MACD, and Bollinger Bands using yfinance data.
    * Evaluation: Utilized early stopping for training and evaluated with MSE and MAE.
    * Implementation: Implemented logging, model management, and visualization for actual vs. predicted prices.
    * Technologies: Python, TensorFlow, Scikit-Learn, XGBoost, Pandas, NumPy, Matplotlib.

Certifications & Memberships:
  - Captain of Wentworth Sailing Team (NEISA Conference) – Spring 2023 - Present
    * Responsibilities: Managed a 25-member team, ensured medical clearance, maintained equipment, coordinated with the director of Club Sports and coach, and oversaw compliance.
  - Certification: US Sailing Level 1 Certification

Work Experience:
  - Position: Technical Support Engineer Intern
    * Organization: Harvard University Information Technology
    * Duration: 04/2024 - 08/2024
    * Responsibilities: Field support for Harvard Engineering School and other Allston schools, deployed and maintained devices per Harvard Security Standards.

  - Position: Computer Science Tutor
    * Organization: Wentworth Institute of Technology, Boston, MA
    * Duration: 01/2024 - Present
    * Responsibilities: Provided one-on-one tutoring for computer science courses, developed personalized plans for students.

  - Position: Owner/Operator
    * Organization: JD’s Woodturning Company, Stony Brook, NY
    * Duration: 10/2018 - Present
    * Responsibilities: Managed all aspects of the handmade wooden goods business, including restocking, transactions, manufacturing, record keeping, and marketing.

  - Position: Sailing Instructor
    * Organization: Port Jefferson Yacht Club, Port Jefferson, NY
    * Duration: 05/2019 - 08/2023
    * Responsibilities: Taught sailing to students aged 6-75, maintained US Sailing Level 1 certification, provided safe and reliable instruction, certified in CPR/AED/BLS and basic concussion diagnosis.
"""



def extract_keywords(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]


def match_jobs_with_resume(job_descriptions, resume_text):
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


def search_internships(api_key, cse_id, query, resume_text):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('items', [])
        job_descriptions = [{'title': item['title'], 'link': item['link'], 'description': item['snippet']} for item in
                            results]

        matched_jobs = match_jobs_with_resume(job_descriptions, resume_text)

        for score, job in matched_jobs:
            print(
                f"Relevance: {score:.2f}\nTitle: {job['title']}\nLink: {job['link']}\nDescription: {job['description']}\n")
    else:
        print(f"Error: {response.status_code} - {response.text}")



api_key = "AIzaSyCmDTs2lWUqNrQqRCEorKI1umwTdRpcAqM"
cse_id = "61fcd2bdd7a354817"  # This should be just the CSE ID, not the full URL
query = "software engineering internship Spring 2025"

search_internships(api_key, cse_id, query, resume_text)
