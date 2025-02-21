import json
import requests
from flask import jsonify
from util import (
    calculate_aggregate_score,
    system_prompt_sentiment,
    predictprice,
    system_predict,
    extract_json_from_string,
)

BASE_URL = "https://defai-1.onrender.com"

class GroqChatbot:
    def __init__(self):
        pass

    def chat(self, query: str):
        payload = {
            "connection": "groq",
            "action": "generate-text",
            "params": [query, "system prompt"],
        }
        url = f"{BASE_URL}/agent/action"
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()
            if not data or "result" not in data:
                return {"error": "Failed to fetch response from Groq."}
            return data["result"]
        except Exception as e:
            print("Error executing chat action:", e)
            return {"error": "Failed to fetch response from Groq."}

    def trending_coins(self, tweets: list):
        system_prompt = '''
            Task:
            Extract cryptocurrency mentions from the tweet below./
            Identify both the full name and ticker symbol when available./
            If only ticker is present, infer the full part using common crypto knowledge./
            If a new or lesser-known cryptocurrency (e.g., "Sonic") is mentioned, recognize it accordingly.
            Rules:
            If only the ticker (e.g., "ETH") is mentioned, convert it into the full name (e.g., "Ethereum").
            Output:
                only full name of crypto currency in json format!!!
                example:
                    {"cryptocurrencies": ["Bitcoin","Sonic"]}
        '''
        query = " ".join(tweets)
        payload = {
            
            "connection": "groq",
            "action": "generate-text",
            "params": [query, system_prompt],
        }
        url = f"{BASE_URL}/agent/action"
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()
            print(data)
            if not data or "result" not in data:
                return {"error": "Failed to fetch response from Groq."}
            result = data["result"]
            if isinstance(result, str):
                try:
                    result = extract_json_from_string(result)
                    result = json.loads(result)
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response from bot.trending_coins"}
            return result
        except Exception as e:
            print("Error executing trending_coins action:", e)
            return {"error": "Failed to fetch response from Groq."}

    def sentiment_coins(self, coin: str, t: int, tweets: list):
        coin_name = coin
        system_prompt = system_prompt_sentiment(coin_name)
        system_prompt += '''Output:
                            Only sentiment and confidence in Json format nothing else.
                            example:
                                {"sentiment": "positive", "confidence": 80}
                    '''
        sentiments = []
        url = f"{BASE_URL}/agent/action"
        print(url)
        for i, tweet in enumerate(tweets, start=1):
            payload = {
                "connection": "groq",
                "action": "generate-text",
                "params": [tweet, system_prompt],
            }
            try:
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
                print(response)
                response.raise_for_status()
                data = response.json()
                if "result" in data:
                    res_text = data["result"]
                    print(f"Tweet {i} response: {res_text}")
                    try:
                        res_text=extract_json_from_string(res_text)
                        res_json = json.loads(res_text)
                        sentiments.append(res_json)
                    except json.JSONDecodeError:
                        print(f"INVALID JSON for tweet {i}")
            except Exception as e:
                print(f"Error processing tweet {i}: {e}")

        sentiment_score = calculate_aggregate_score(sentiments)
        predicted_price = predictprice(coin, t)
        print("Predicted Price:", predicted_price)
        prompt = system_predict(coin_name, sentiment_score)
        prompt += '''
            Output:
            output only adjusted_price,current_price,predicted_price in Json format, Nothing else.
            example:        
                        "dex_1": {
                            "adjusted_price": 105551.05190932725,
                            "current_price": 96561.6639990985,
                            "predicted_price": 104551.05190932725
                        }
        '''
        payload_price = {
            "connection": "groq",
            "action": "generate-text",
            "params": [json.dumps(predicted_price, indent=4, default=str), prompt],
        }
        result={}
        try:
            response_price = requests.post(url, json=payload_price, headers={"Content-Type": "application/json"})
            response_price.raise_for_status()
            price_data = response_price.json()
            try:
                json_str = extract_json_from_string(price_data["result"])
                print("Extracted JSON string:", json_str)
                response_data = json.loads(json_str)
                dex_prices = response_data
            except json.JSONDecodeError:
                dex_prices = predicted_price  
            
            buying_dex = min(dex_prices, key=lambda d: dex_prices[d]["current_price"])
            selling_dex = max(dex_prices, key=lambda d: dex_prices[d]["predicted_price"])
            change_val = dex_prices[selling_dex]["predicted_price"] - dex_prices[buying_dex]["current_price"]
            percentage_change = (change_val / dex_prices[buying_dex]["current_price"]) * 100
            result = {
                "score": (sentiment_score+1)/2,
                "dex": dex_prices,
                "buying_dex": buying_dex,
                "buy_price": dex_prices[buying_dex]["current_price"],
                "selling_dex": selling_dex,
                "sell_price": dex_prices[selling_dex]["predicted_price"],
                "change_val":change_val,
                "change_per":percentage_change
            }
        except Exception as e:
            print("Error processing predicting price:", e)
        return result
