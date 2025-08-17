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
# IMPORTANT: For production, use environment variables instead of hardcoding the key.
# For example: genai.configure(api_key=os.environ["GEMINI_API_KEY"])
GEMINI_API_KEY = "AIzaSyBbJrZZa7LFRyLdDYcn0d2mDVgLY1i8XB4"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def parse_query_with_ai(query):
    """
    Uses the Gemini API to structure a user's query into a JSON object.
    """
    print(f"  -> Sending query to Gemini AI: '{query}'")
    
    # This is the prompt we send to the AI. It's a "zero-shot" prompt,
    # asking the AI to perform a task with instructions but no prior examples.
    prompt = f"""
    Analyze the following job search query and extract the job role and the location.
    Return the result as a clean JSON object with two keys: "role" and "location".
    If a key is not mentioned, its value should be null.

    Query: "{query}"

    JSON Output:
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean up the response to get only the JSON part
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Parse the JSON string into a Python dictionary
        structured_query = json.loads(json_text)
        print(f"  -> Gemini AI structured result: {structured_query}")
        return structured_query
        
    except Exception as e:
        print(f"  -> Gemini API error or JSON parsing failed: {e}")
        # Fallback to a simple structure if the AI fails
        return {"role": query, "location": None}


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
    # We now pass the structured data to our API function.
    # Note: We'll need to update scraper.py to handle the location parameter.
    # For now, we'll just use the role.
    role_query = ai_structured_query.get("role")
    
    if not role_query:
        print(" -> AI could not determine a role, using full query.")
        role_query = query
        
    live_jobs = fetch_jobs_from_api(role_query, page=1)
    
    print(f"Found {len(live_jobs)} jobs from Adzuna API.")
    
    return jsonify(live_jobs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
