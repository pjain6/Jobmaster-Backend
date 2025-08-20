# scraper.py
# This file now contains the client function for the JobsPikr API.

import requests
import json
import os

# --- API CREDENTIALS ---
# This will be stored as an Environment Variable on Render
JOBSPIKR_API_KEY = os.environ.get("JOBSPIKR_API_KEY", "uF43fN8RnG_3zmGiMOtiwfk24DaickrENAYjuRZ2OTc")


def fetch_jobspikr_jobs(query_data):
    """
    Fetches job listings from the JobsPikr Real-Time API.
    """
    print(f"  -> Querying JobsPikr API for: {query_data}")
    
    # This is a standard endpoint structure for a service like JobsPikr.
    # You may need to adjust it based on their specific documentation.
    url = "https://api.jobspikr.com/v2/jobs"
    
    # Construct the payload for the API based on our AI's analysis
    params = {
        "api_key": JOBSPIKR_API_KEY,
        "query": query_data.get("role", ""),
        "location": query_data.get("location", ""),
        "size": 100 # Fetch up to 100 results
    }

    try:
        # Make the API call
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        api_results = response.json().get('jobs', [])

        jobs_list = []
        for job_data in api_results:
            # Normalize the data to our app's format
            job = {
                "id": job_data.get('id'),
                "title": job_data.get('title'),
                "company": job_data.get('company_name', 'N/A'),
                "location": job_data.get('location_normalized', 'N/A'),
                "description": job_data.get('job_description_html', 'See original posting.'), # Use the full description
                "link": job_data.get('job_url')
            }
            jobs_list.append(job)
        return jobs_list
        
    except Exception as e:
        print(f"  -> JobsPikr API error: {e}")
        return []

