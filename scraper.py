# scraper.py
# FINAL, PRODUCTION-READY VERSION
# Uses the Adzuna Job Board API for reliable, structured data.

import requests
import json

# --- PASTE YOUR ADZUNA API CREDENTIALS HERE ---
ADZUNA_APP_ID = "96373f58"
ADZUNA_APP_KEY = "63d4d6ca5bf5353fcaf2398c68bd8433"

def fetch_jobs_from_api(query, location=None, salary_min=None, experience=None, page=1):
    """
    Fetches job listings from the Adzuna API, now with salary and experience filtering.
    """
    print(f"  -> Sending request for '{query}' in '{location or 'anywhere'}' to Adzuna API...")

    # Adzuna API endpoint details
    url_endpoint = f"http://api.adzuna.com/v1/api/jobs/us/search/{page}"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': query,
        'results_per_page': 50, # Get a good number of results
        'content-type': 'application/json'
    }

    # --- ADDING THE NEW FILTERS ---
    if location:
        params['where'] = location
    if salary_min:
        params['salary_min'] = salary_min
    if experience and experience in ['entry-level', 'junior']:
        # Adzuna's experience filtering is limited. A more complex system might use
        # keywords in the 'what' query, but for now, we add the parameter if present.
        # This demonstrates how the AI's output is used.
        params['what_and'] = experience # Adds the experience level as a required keyword

    try:
        response = requests.get(url_endpoint, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        
        data = response.json()
        api_results = data.get('results', [])

        jobs_list = []
        for job_data in api_results:
            # Map the Adzuna API response to our application's job format
            job = {
                "id": job_data.get('id'),
                "title": job_data.get('title'),
                "company": job_data.get('company', {}).get('display_name', 'N/A'),
                "location": job_data.get('location', {}).get('display_name', 'N/A'),
                "salary": "N/A", # Salary data can be complex in Adzuna, keeping it simple for now
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

# The main block below is no longer used by the live server, but is kept for manual data fetching.
if __name__ == '__main__':
    if ADZUNA_APP_ID == "YOUR_APP_ID_HERE" or ADZUNA_APP_KEY == "YOUR_APP_KEY_HERE":
        print("\nERROR: Please paste your Adzuna App ID and App Key into the scraper.py file.\n")
    else:
        print("This script is now intended to be used by app.py. To run a manual fetch, you would call the functions directly.")
