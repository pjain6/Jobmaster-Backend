# scraper.py
# This file now contains the client function for the JobsPikr API,
# updated according to the official documentation for complex queries.

import requests
import json
import os

# --- API CREDENTIALS ---
JOBSPIKR_CLIENT_ID = os.environ.get("JOBSPIKR_CLIENT_ID", "jobma_jp_fcc0819ad1")
JOBSPIKR_AUTH_KEY = os.environ.get("JOBSPIKR_AUTH_KEY", "uF43fN8RnG_3zmGiMOtiwfk24DaickrENAYjuRZ2OTc")


def fetch_jobspikr_jobs(query_data):
    """
    Fetches job listings from the JobsPikr API using the correct authentication and query structure.
    """
    print(f"  -> Querying JobsPikr API for: {query_data}")
    
    url = "https://api.jobspikr.com/v2/data"
    
    headers = {
        'client_id': JOBSPIKR_CLIENT_ID,
        'client_auth_key': JOBSPIKR_AUTH_KEY,
        'Content-Type': 'application/json'
    }
    
    role = query_data.get("role")
    location = query_data.get("location")

    # If there's no role (like in a 'wakeup' call), don't make an invalid API request.
    if not role:
        return []

    # --- THIS IS THE FIX ---
    # Build the complex Elasticsearch query that JobsPikr requires.
    must_clauses = [
        {
            "query_string": {
                "query": f'"{role}"', # Use quotes for phrase matching
                "fields": ["job_title", "inferred_job_title"]
            }
        }
    ]

    if location:
        must_clauses.append({
            "query_string": {
                "query": f'"{location}"',
                "fields": ["city", "inferred_city", "state", "inferred_state", "country", "inferred_country"]
            }
        })

    search_query = {
        "bool": {
            "must": must_clauses
        }
    }
    
    payload = {
        "search_query_json": search_query, # Pass the JSON object directly
        "size": 100
    }

    try:
        # The API expects the body to be a JSON string, so we dump it here.
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        api_results = response.json().get('job_data', [])

        jobs_list = []
        for job_data in api_results:
            job = {
                "id": job_data.get('uniq_id'),
                "title": job_data.get('job_title'),
                "company": job_data.get('company_name', 'N/A'),
                "location": job_data.get('inferred_city', 'N/A') + ", " + job_data.get('inferred_state', ''),
                "description": job_data.get('html_job_description', 'See original posting.'),
                "link": job_data.get('url')
            }
            jobs_list.append(job)
        return jobs_list
        
    except Exception as e:
        print(f"  -> JobsPikr API error: {e}")
        return []

