import requests
import numpy as np
import logging
import requests
from config import OPENAI_API_KEY, OPENAI_API_URL

def generate_ai_analysis(prompt):
    """Generate summary using OpenAI."""
    headers = {"Content-Type": "application/json", "api-key": OPENAI_API_KEY}
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI assistant trained to extract key insights from data."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.7
    }
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, data=json.dumps(payload))
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "No summary found.")
    except Exception as e:
        return f"Error generating summary: {e}"