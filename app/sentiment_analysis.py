import os
import json
import google.generativeai as genai
import re

genai.configure(api_key="AIzaSyDS5qxGT3N2XbqibpY8PyFbomKpe0SCkLE")

def clean_text(text: str) -> str:
    """
    Clean the input text by:
    1. Converting to lowercase
    2. Removing special characters (keeping numbers)
    3. Removing extra whitespace
    """
    # Convert to lowercase
    text = text.lower()
    text = text.replace('\n', ' ')
    # Remove special characters but keep numbers and letters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def analyze_sentiment_gemini(text, api_key="AIzaSyDS5qxGT3N2XbqibpY8PyFbomKpe0SCkLE"):
    """
    Analyzes the sentiment of a given text using the Gemini API with function calling simulation.

    Args:
        text: The text to analyze.
        api_key: Your Gemini API key.

    Returns:
        A dictionary containing the sentiment analysis results, or None if an error occurs.
    """
    # Configure Gemini API
    # genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    # Define the function schema
    function_schema = {
        "name": "analyze_sentiment",
        "description": "Analyzes the sentiment of a given text.",
        "parameters": {
            "type": "object",
            "properties": {
                "sentence": {
                    "type": "string",
                    "description": "The original sentence provided for sentiment analysis."
                },
                "sentiment": {
                    "type": "string",
                    "description": "The sentiment of the text (e.g., Positive, Negative, Neutral, Frustrated)."
                },
                "explanation": {
                    "type": "string",
                    "description": "A brief explanation justifying the sentiment analysis result."
                },
                "confidence": {
                    "type": "number",
                    "description": "The confidence score of the sentiment analysis (0-1)."
                }
            },
            "required": ["sentiment"]
        }
    }

    try:
        # Simulating function calling by asking Gemini to follow the schema
        prompt = f"""
        You are an assistant that uses the function {function_schema['name']} to analyze text.
        Follow this JSON schema strictly:
        {json.dumps(function_schema['parameters'],indent=3)}

        Analyze the following text:
        "{text}"
        """

        response = model.generate_content(prompt)

        # Parse JSON response from the model
        sentiment_data = json.loads(response.text)
        return sentiment_data

    except json.JSONDecodeError:
        print("Failed to decode JSON from the model's response.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# result = analyze_sentiment_gemini("This movie was absolutely fantastic! I loved every minute of it.", API_KEY)
# # print(result['explanation'])
# print(result)
