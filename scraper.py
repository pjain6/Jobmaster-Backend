# scraper.py
# This file now contains the client function for the JobsPikr API,
# updated according to the official documentation.

import requests
import json
import os

# --- API CREDENTIALS ---
# These will be stored as Environment Variables on Render
JOBSPIKR_CLIENT_ID = os.environ.get("JOBSPIKR_CLIENT_ID", "jobma_jp_fcc0819ad1")
JOBSPIKR_AUTH_KEY = os.environ.get("JOBSPIKR_AUTH_KEY", "uF43fN8RnG_3zmGiMOtiwfk24DaickrENAYjuRZ2OTc")


def fetch_jobspikr_jobs(query_data):
    """
    Fetches job listings from the JobsPikr API using the correct authentication and endpoints.
    """
    print(f"  -> Querying JobsPikr API for: {query_data}")
    
    # Use the correct endpoint for job data
    url = "https://api.jobspikr.com/v2/data"
    
    # --- CORRECT AUTHENTICATION METHOD ---
    # Provide credentials in the request headers
    headers = {
        'client_id': JOBSPIKR_CLIENT_ID,
        'client_auth_key': JOBSPIKR_AUTH_KEY,
        'Content-Type': 'application/json'
    }
    
    # --- CORRECT QUERY STRUCTURE ---
    # Build the specific search_query_json object that JobsPikr requires
    search_query = {
        "query_string": {
            "query": query_data.get("role", "")
        }
    }
    
    # Construct the full payload for the POST request
    payload = {
        "search_query_json": json.dumps(search_query), # The query must be a JSON string
        "size": 100
    }

    try:
        # --- USE POST REQUEST ---
        # Make the API call using POST as recommended
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        api_results = response.json().get('job_data', [])

        jobs_list = []
        for job_data in api_results:
            # Normalize the data to our app's format
            job = {
                "id": job_data.get('uniq_id'),
                "title": job_data.get('job_title'),
                "company": job_data.get('company_name', 'N/A'),
                "location": job_data.get('inferred_city', 'N/A') + ", " + job_data.get('inferred_state', ''),
                "description": job_data.get('html_job_description', 'See original posting.'), # Use the full HTML description
                "link": job_data.get('url')
            }
            jobs_list.append(job)
        return jobs_list
        
    except Exception as e:
        print(f"  -> JobsPikr API error: {e}")
        return []

