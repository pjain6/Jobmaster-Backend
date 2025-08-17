# app.py
# UPDATED: Reads pre-scraped data from jobs.json instead of running the scraper live.

from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

def load_jobs_from_file():
    """Loads job data from the jobs.json file."""
    try:
        with open("jobs.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty list if the file doesn't exist or is invalid
        return []

@app.route('/api/search', methods=['GET'])
def search_jobs():
    """
    Handles a search request by filtering the jobs loaded from the JSON file.
    """
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    print(f"Received search query: '{query}'. Searching local file...")
    
    all_jobs = load_jobs_from_file()
    
    # Simple search logic: filter jobs where the query appears in the title or description
    search_terms = query.split()
    results = [
        job for job in all_jobs 
        if all(term in (job.get('title', '') + job.get('description', '')).lower() for term in search_terms)
    ]
    
    print(f"Found {len(results)} matching jobs in local file.")
    return jsonify(results)

if __name__ == '__main__':
    # No longer need threaded=False, as the server isn't doing heavy work.
    app.run(host='0.0.0.0', port=5001, debug=True)
