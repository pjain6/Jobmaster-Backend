# scraper.py
# This file now contains client functions for multiple job APIs.

import requests
import json
import os

# --- API CREDENTIALS ---
# These will be stored as Environment Variables on Render
JOBSPIKR_CLIENT_ID = os.environ.get("JOBSPIKR_CLIENT_ID", "jobma_jp_fcc0819ad1")
JOBSPIKR_AUTH_KEY = os.environ.get("JOBSPIKR_AUTH_KEY", "uF43fN8RnG_3zmGiMOtiwfk24DaickrENAYjuRZ2OTc")
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "96373f58")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "63d4d6ca5bf5353fcaf2398c68bd8433")


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

    if not role:
        return []

    must_clauses = [{"query_string": {"query": f'"{role}"', "fields": ["job_title", "inferred_job_title"]}}]
    if location:
        must_clauses.append({"query_string": {"query": f'"{location}"', "fields": ["city", "inferred_city", "state", "inferred_state"]}})

    payload = {
        "search_query_json": {"bool": {"must": must_clauses}},
        "size": 100
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        api_results = response.json().get('job_data', [])

        jobs_list = []
        for job_data in api_results:
            job = {
                "id": job_data.get('uniq_id'),
                "title": job_data.get('job_title'),
                "company": job_data.get('company_name', 'N/A'),
                "location": f"{job_data.get('inferred_city', '')}, {job_data.get('inferred_state', '')}",
                "description": job_data.get('html_job_description', 'See original posting.'),
                "link": job_data.get('url')
            }
            jobs_list.append(job)
        return jobs_list
    except Exception as e:
        print(f"  -> JobsPikr API error: {e}")
        return []


def fetch_adzuna_jobs(query_data):
    """
    Fetches job listings from the Adzuna API.
    """
    role = query_data.get("role")
    location = query_data.get("location")
    salary_min = query_data.get("salary_min")
    
    if not role:
        return []
        
    print(f"  -> Querying Adzuna API for: {query_data}")
    url_endpoint = "http://api.adzuna.com/v1/api/jobs/us/search/1"
    
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'what': role,
        'results_per_page': 50,
        'content-type': 'application/json'
    }
    if location:
        params['where'] = location
    if salary_min:
        params['salary_min'] = salary_min

    try:
        response = requests.get(url_endpoint, params=params)
        response.raise_for_status()
        api_results = response.json().get('results', [])

        jobs_list = []
        for job_data in api_results:
            job = {
                "id": job_data.get('id'),
                "title": job_data.get('title'),
                "company": job_data.get('company', {}).get('display_name', 'N/A'),
                "location": job_data.get('location', {}).get('display_name', 'N/A'),
                "description": job_data.get('description', 'See original posting.'),
                "link": job_data.get('redirect_url')
            }
            jobs_list.append(job)
        return jobs_list
    except Exception as e:
        print(f"  -> Adzuna API error: {e}")
        return []
