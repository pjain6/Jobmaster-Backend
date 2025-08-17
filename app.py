# app.py
# GEMINI AI-POWERED VERSION
# This server uses the Gemini API to understand user queries.

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import json
import os

# We now import the function that calls the Adzuna API
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
    
    # --- UPGRADED AI PROMPT ---
    # We now ask the AI to extract salary and experience level as well.
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
        # Fallback to a simple structure if the AI fails
        return {"role": query, "location": None, "salary_min": None, "experience_level": None}


@app.route('/api/search', methods=['GET'])
def search_jobs():
    """
    Handles a search request by first analyzing the query with Gemini,
    then calling the Adzuna API with the structured data.
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("ERROR: Gemini API key is not set.")
        return jsonify({"error": "Server is not configured with AI credentials."}), 500

    print(f"Received live search query: '{query}'.")
    
    # --- STEP 1: AI QUERY ANALYSIS ---
    ai_structured_query = parse_query_with_ai(query)
    
    # --- STEP 2: PRECISE API CALL ---
    role_query = ai_structured_query.get("role")
    location_query = ai_structured_query.get("location")
    salary_query = ai_structured_query.get("salary_min")
    experience_query = ai_structured_query.get("experience_level")
    
    if not role_query:
        print(" -> AI could not determine a role, using full query.")
        role_query = query
        
    # Pass all extracted data to the API function for a highly specific search
    live_jobs = fetch_jobs_from_api(
        role_query, 
        location=location_query, 
        salary_min=salary_query,
        experience=experience_query,
        page=1
    )
    
    print(f"Found {len(live_jobs)} jobs from Adzuna API.")
    
    return jsonify(live_jobs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
