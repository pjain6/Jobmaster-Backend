# app.py
# FINAL VERSION
# This server is now cleaner, with the redundant /expand endpoint removed.

from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import json
import os

from scraper import fetch_jobspikr_jobs

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
    Handles a search request by analyzing the query with AI, then calling the 
    JobsPikr job aggregator to get comprehensive, live results.
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    if query == 'wakeup':
        print("Received wakeup call. Returning empty list.")
        return jsonify([])

    print(f"Received live search query: '{query}'.")
    ai_structured_query = parse_query_with_ai(query)
    
    live_jobs = fetch_jobspikr_jobs(ai_structured_query)
    
    print(f"Found {len(live_jobs)} jobs from JobsPikr.")
    return jsonify(live_jobs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
