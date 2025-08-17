# scraper.py
# SOPHISTICATED VERSION
# Fetches multiple pages of results and prepares for AI analysis.

import requests
import json
import time

# --- YOUR ADZUNA API CREDENTIALS ---
ADZUNA_APP_ID = "96373f58"
ADZUNA_APP_KEY = "63d4d6ca5bf5353fcaf2398c68bd8433"

def fetch_jobs_from_api(query, page=1):
    """
    Fetches a single page of job listings from the Adzuna API.
    """
    print(f"  -> Sending request for '{query}' (Page {page}) to Adzuna API...")
    url_endpoint = f"http://api.adzuna.com/v1/api/jobs/us/search/{page}"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': query,
        'results_per_page': 50, # Ask for the max number of results per page
        'content-type': 'application/json'
    }

    try:
        response = requests.get(url_endpoint, params=params)
        response.raise_for_status()
        
        data = response.json()
        api_results = data.get('results', [])

        jobs_list = []
        for job_data in api_results:
            job = {
                "id": job_data.get('id'),
                "title": job_data.get('title'),
                "company": job_data.get('company', {}).get('display_name', 'N/A'),
                "location": job_data.get('location', {}).get('display_name', 'N/A'),
                "salary": "N/A",
                "description": job_data.get('description', 'See original posting for details.'),
                "link": job_data.get('redirect_url')
            }
            jobs_list.append(job)
        
        return jobs_list

    except requests.exceptions.HTTPError as http_err:
        print(f"  -> HTTP error occurred: {http_err}")
        return []
    except Exception as e:
        print(f"  -> An unexpected error occurred: {e}")
        return []

def analyze_job_with_ai(job_description):
    """
    *** AI INTEGRATION POINT (SIMULATED) ***
    In a real system, this function would send the job description to an AI model
    (like Gemini) to extract structured data. For now, we simulate this.
    """
    # Simulate extracting keywords. A real AI would be much more accurate.
    keywords = []
    description_lower = job_description.lower()
    if 'python' in description_lower: keywords.append('Python')
    if 'react' in description_lower: keywords.append('React')
    if 'sql' in description_lower: keywords.append('SQL')
    if 'agile' in description_lower: keywords.append('Agile')
    if 'aws' in description_lower: keywords.append('AWS')
    if 'sales' in description_lower: keywords.append('Sales')
    
    # Simulate identifying experience level
    level = 'Mid-Level'
    if 'senior' in description_lower or 'lead' in description_lower:
        level = 'Senior'
    elif 'junior' in description_lower or 'entry' in description_lower:
        level = 'Entry-Level'
        
    return {
        "skills": keywords,
        "level": level
    }

if __name__ == '__main__':
    print("Starting the advanced job data fetcher...")
    
    # Expand our queries to get a wider range of jobs
    queries = [
        "python developer", "sales manager", "react developer", "data analyst", 
        "project manager", "software engineer", "marketing manager", "devops engineer",
        "graphic designer", "customer support"
    ]
    all_jobs = []
    
    for query in queries:
        print(f"Fetching data for: '{query}'")
        # --- PAGINATION LOGIC ---
        # We'll fetch up to 5 pages of results for each query.
        for page_num in range(1, 6): 
            jobs = fetch_jobs_from_api(query, page=page_num)
            if jobs:
                all_jobs.extend(jobs)
                print(f"  -> Page {page_num}: Found {len(jobs)} jobs.")
            else:
                # If a page has no results, no need to check the next ones
                print(f"  -> Page {page_num}: No more results.")
                break
            time.sleep(1) # Be polite to the API and wait a second between requests
            
    print(f"\nTotal jobs fetched: {len(all_jobs)}. Now analyzing with AI...")
    
    # --- AI ANALYSIS STEP ---
    analyzed_jobs = []
    for job in all_jobs:
        ai_analysis = analyze_job_with_ai(job['title'] + ' ' + job['description'])
        job['ai_analysis'] = ai_analysis # Add the new AI data to our job object
        analyzed_jobs.append(job)
        
    unique_jobs = {job['id']: job for job in analyzed_jobs}
    
    with open("jobs.json", "w") as f:
        json.dump(list(unique_jobs.values()), f, indent=4)
        
    print(f"\nProcess complete. Saved {len(unique_jobs)} unique, AI-analyzed jobs to jobs.json")
