import json
import requests
from flask import Flask, jsonify, request
from util import (
    calculate_aggregate_score,
    system_prompt_sentiment,
    predictprice,
    system_predict,
    extract_json_from_string,
)

app = Flask(__name__)
BASE_URL = "https://defai-3lma.onrender.com"

def post_tweet(tweet_text: str):
    payload = {
        "connection": "twitter",
        "action": "post-tweet",
        "params": [tweet_text],
    }
    url = f"{BASE_URL}/agent/action"
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json()
        if "status" in data and data["status"] == "success":
            return {"message": "Tweet posted successfully."}
        return {"error": "Failed to post tweet."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@app.route("/tweet", methods=["POST"])
def tweet():
    try:
        data = request.get_json()
        if not data or "tweet_text" not in data:
            return jsonify({"error": "Missing tweet_text parameter"}), 400
        result = post_tweet(data["tweet_text"])
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

