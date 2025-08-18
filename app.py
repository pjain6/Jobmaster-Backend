# app.py
# GEMINI AI-POWERED VERSION V3
# This server now fetches multiple pages from Adzuna and sorts by relevance.

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import json
import os
import time

from scraper import fetch_jobs_from_api, ADZUNA_APP_ID, ADZUNA_APP_KEY

app = Flask(__name__)
CORS(app)

# --- CONFIGURE GEMINI API ---
GEMINI_API_KEY = "AIzaSyBbJrZZa7LFRyLdDYcn0d2mDVgLY1i8XB4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def parse_query_with_ai(query):
    """
    Uses the Gemini API to structure a user's query into a JSON object.
    """
    print(f"  -> Sending query to Gemini AI: '{query}'")
    
    prompt = f"""
    Analyze the following job search query and extract up to four pieces of information:
    1. The job role.
    2. The location.
    3. The minimum salary (as an integer, do not include characters like $ or ,).
    4. The experience level (e.g., "entry-level", "senior", "manager").

    Return the result as a clean JSON object with four keys: "role", "location", "salary_min", and "experience_level".
    If a key is not mentioned, its value should be null.

    Query: "{query}"

    JSON Output:
    """

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        structured_query = json.loads(json_text)
        print(f"  -> Gemini AI structured result: {structured_query}")
        return structured_query
        
    except Exception as e:
        print(f"  -> Gemini API error or JSON parsing failed: {e}")
        return {"role": query, "location": None, "salary_min": None, "experience_level": None}


@app.route('/api/search', methods=['GET'])
def search_jobs():
    """
    Handles a search request by analyzing the query with AI, fetching multiple pages
    of results, and returning them sorted by relevance.
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    print(f"Received live search query: '{query}'.")
    ai_structured_query = parse_query_with_ai(query)
    
    role_query = ai_structured_query.get("role")
    location_query = ai_structured_query.get("location")
    salary_query = ai_structured_query.get("salary_min")
    experience_query = ai_structured_query.get("experience_level")
    
    if not role_query:
        role_query = query
        
    all_jobs = []
    # --- PAGINATION LOGIC ---
    # Fetch up to 5 pages of results to get a large pool of jobs.
    for page_num in range(1, 6):
        print(f"Fetching page {page_num}...")
        jobs_on_page = fetch_jobs_from_api(
            role_query, 
            location=location_query, 
            salary_min=salary_query,
            experience=experience_query,
            page=page_num
        )
        if jobs_on_page:
            all_jobs.extend(jobs_on_page)
        else:
            # Stop if a page returns no results
            break
        time.sleep(0.5) # Be polite to the API

    # Remove duplicates
    unique_jobs = list({job['id']: job for job in all_jobs}.values())
    
    print(f"Found {len(unique_jobs)} unique jobs from Adzuna API.")
    return jsonify(unique_jobs)


# --- NEW AI ENDPOINT FOR EXPANDING DESCRIPTIONS ---
@app.route('/api/job/expand', methods=['POST'])
def expand_job_description():
    """
    Receives a job snippet and uses Gemini to expand it into a full description.
    """
    data = request.get_json()
    snippet = data.get('description')

    if not snippet:
        return jsonify({"error": "Description snippet is required."}), 400

    print(f"  -> Received snippet to expand. Sending to Gemini...")

    prompt = f"""
    Based on the following job description snippet, please expand it into a plausible, well-formatted, and detailed job description of about 3-4 paragraphs.
    Elaborate on the likely duties, qualifications, and company culture implied by the snippet.
    Do not invent wildly different responsibilities. The tone should be professional.
    Do not include a title or company name in your response, only the expanded description text.

    Snippet: "{snippet}"

    Expanded Description:
    """

    try:
        response = model.generate_content(prompt)
        expanded_description = response.text.strip()
        print("  -> Successfully expanded description with AI.")
        return jsonify({"full_description": expanded_description})
    except Exception as e:
        print(f"  -> Gemini API error during expansion: {e}")
        return jsonify({"full_description": snippet})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
