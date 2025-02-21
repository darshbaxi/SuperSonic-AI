import os
import pandas as pd
from prophet import Prophet
import json
import requests
import urllib.parse

BASE_URL = "https://defai-1.onrender.com"

def calculate_aggregate_score(sentiments):
    total_weighted_score = 0
    total_confidence = 0

    for sentiment_data in sentiments:
        sentiment = sentiment_data["sentiment"]
        confidence = sentiment_data["confidence"]

        if sentiment == "positive":
            score = 1
        elif sentiment == "negative":
            score = -1
        else:
            score = 0

        total_weighted_score += score * confidence
        total_confidence += confidence

    if total_confidence == 0:
        return 0  

    aggregate_score = total_weighted_score / total_confidence
    return round(aggregate_score, 4)


def system_prompt_sentiment(coin: str):
    coin_name = coin 
    system_prompt = f'''
            Task: 
                Analyze the sentiment of the following tweet about {coin_name}.
                Classify it as positive, negative, or neutral and provide a confidence score (0-100%).

            Rules:
                If the tweet expresses excitement, growth, or optimism about {coin_name}, mark it positive.
                If it contains doubt, loss, or negativity, mark it negative.
                If it’s neutral or factual, mark it neutral.
                The confidence score reflects the strength of sentiment.
        '''
    return system_prompt
    

def system_predict(coin: str, score: int):
    system_prompt = f'''
            You are an advanced financial AI assisting in cryptocurrency price forecasting.
            You will analyze current and predicted prices (predicted using Prophet Model) and the sentiment score for {coin} is {score} to improve price predictions.
            Higher positive sentiment may increase the price, while negative sentiment may decrease it.
            Ensure that the effect is realistic and aligns with past market behavior.
            Return the adjusted price forecast in a structured JSON format.
            
        '''
    return system_prompt


def predictprice(coin: str, t: int):
    results = {}
    for dex in range(1, 4):
        file_path = os.path.join("Data", f"{coin}_dex_{dex}.csv")
        df = pd.read_csv(file_path)
        df['snapped_at'] = pd.to_datetime(df['snapped_at']).dt.tz_localize(None)
        df = df.rename(columns={'snapped_at': 'ds', 'price': 'y'})
        m = Prophet()
        m.fit(df)
        horizon = int(t)
        future = m.make_future_dataframe(periods=horizon, freq='D')
        forecast = m.predict(future)
        print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(horizon))
        
        current_price = df.iloc[-1]['y']
        predicted_price = forecast.iloc[-1][['ds', 'yhat']].to_dict()
        results[f'dex_{dex}'] = {
            "current_price": current_price,
            "predicted_price": predicted_price
        }

    return results


def extract_json_from_string(s):
    start = s.find('{')  
    end = s.rfind('}')   
    return s[start:end+1] if start != -1 and end != -1 else None 


def load_agent(name):
    try:
        encoded_name = urllib.parse.quote(name)
        response = requests.post(f'{BASE_URL}/agents/{encoded_name}/load')
        response.raise_for_status()
        result = response.json()
        print(f'Agent "{name}" loaded:', result)
    except requests.exceptions.RequestException as e:
        print(f'Error loading agent "{name}":', e)
