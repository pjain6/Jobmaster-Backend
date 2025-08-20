# app.py
# FINAL AGGREGATOR VERSION
# This server calls multiple job APIs in parallel and merges the results.

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import json
import os
import concurrent.futures

# We now import both API client functions
from scraper import fetch_adzuna_jobs, fetch_jobspikr_jobs

app = Flask(__name__)
CORS(app)

# --- CONFIGURE GEMINI API ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBbJrZZa7LFRyLdDYcn0d2mDVgLY1i8XB4")
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
    Handles a search request by analyzing the query, calling multiple job APIs
    in parallel, and returning a merged, deduplicated list of results.
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    if query == 'wakeup':
        print("Received wakeup call. Returning empty list.")
        return jsonify([])

    print(f"Received live search query: '{query}'.")
    ai_structured_query = parse_query_with_ai(query)
        
    all_jobs = []
    # --- PARALLEL API CALLS ---
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_jobspikr = executor.submit(fetch_jobspikr_jobs, ai_structured_query)
        future_adzuna = executor.submit(fetch_adzuna_jobs, ai_structured_query)

        if future_jobspikr.result():
            all_jobs.extend(future_jobspikr.result())
        if future_adzuna.result():
            all_jobs.extend(future_adzuna.result())

    # --- INTELLIGENT DEDUPLICATION ---
    # Create a unique "signature" for each job to remove true duplicates.
    unique_jobs = {}
    for job in all_jobs:
        # A signature is a combination of the core job details, lowercased.
        signature = (
            job.get('title', '').lower(),
            job.get('company', '').lower(),
            job.get('location', '').lower()
        )
        if signature not in unique_jobs:
            unique_jobs[signature] = job
    
    final_job_list = list(unique_jobs.values())
    
    print(f"Found {len(final_job_list)} unique jobs from all sources.")
    return jsonify(final_job_list)


# --- AI ENDPOINT FOR EXPANDING DESCRIPTIONS ---
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
