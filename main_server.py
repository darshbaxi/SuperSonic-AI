import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import GroqChatbot
from util import load_agent 
from twitter import post_tweet 

# BASE_URL is defined in groq.py; it's not used here directly.

def create_app():
    """Initialize and configure the Flask app."""
    app = Flask(__name__)
    CORS(app)
    
    bot = GroqChatbot()
    load_agent("starter")
    
    @app.route('/chat', methods=['POST'])
    def chatbot():
        json_data = request.get_json()
        if not json_data or 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        query = json_data['query']
        response = bot.chat(query)
        return jsonify({"result": response})
    
    @app.route('/trending_coin', methods=['POST'])
    def personalized_trending_coins():
        json_data = request.get_json()
        if not json_data or 'query' not in json_data:
            return jsonify({"error": "Missing 'query' parameter"}), 400
        tweets = json_data['query']
        response = bot.trending_coins(tweets)
        return jsonify({"result": response})
    
    @app.route('/sentiment', methods=['POST'])
    def sentiments():
        json_data = request.get_json()
        if not all(k in json_data for k in ("coin", "time", "query")):
            return jsonify({"error": "Missing one of 'coin', 'time', or 'query' parameters"}), 400
        coin = json_data["coin"]
        t = json_data["time"]
        tweets = json_data["query"]
        print(coin)
        response = bot.sentiment_coins(coin, t, tweets)
        return jsonify({"result": response})
    
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
       
    return app


def start_flask(port):
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Flask server with a specified port.")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    args = parser.parse_args()
    start_flask(args.port)
