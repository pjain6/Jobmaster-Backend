# app.py
# LIVE SEARCH VERSION
# This server calls the Adzuna API in real-time for every search.

from flask import Flask, jsonify, request
from flask_cors import CORS

# We now import the function that calls the Adzuna API
from scraper import fetch_jobs_from_api, ADZUNA_APP_ID, ADZUNA_APP_KEY

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_jobs():
    """
    Handles a search request by calling the Adzuna API in real-time.
    """
    # Get the full query from the user's search
    query = request.args.get('q', '').lower()
    
    # Adzuna's API can also filter by location if we structure the query
    # For now, we'll pass the whole query string to the 'what' parameter
    
    if not query:
        return jsonify({"error": "A search query 'q' is required."}), 400

    # Check if API keys are set, which is crucial for a live server
    if ADZUNA_APP_ID == "YOUR_APP_ID_HERE" or ADZUNA_APP_KEY == "YOUR_APP_KEY_HERE":
        print("ERROR: Adzuna API credentials are not set in scraper.py")
        return jsonify({"error": "Server is not configured with API credentials."}), 500

    print(f"Received live search query: '{query}'. Calling Adzuna API...")
    
    # --- REAL-TIME API CALL ---
    # We call the function from scraper.py to get live results.
    # We are only fetching the first page for now to keep the response fast.
    live_jobs = fetch_jobs_from_api(query, page=1)
    
    print(f"Found {len(live_jobs)} jobs from Adzuna API.")
    
    # We no longer need to filter. We just return the live results.
    return jsonify(live_jobs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
