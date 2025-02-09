from fastapi import FastAPI, HTTPException
import uvicorn
from pyngrok import ngrok
from pydantic import BaseModel, EmailStr
from sentiment_analysis import analyze_sentiment_gemini, clean_text
from issue_escalation import required_issue_escalation, issue_escalation
from response_automation import get_product_body, get_product_subject
from pinecone_embedding import rag_pipeline
from webhook import send_email
import re
import traceback
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

app = FastAPI()


class SentimentRequest(BaseModel):
    text: str
    
@app.post("/sentiment")
async def sentiment(text: str):
    try:
        # Clean the input text first
        cleaned_text = clean_text(text)
        
        # Use the cleaned text for sentiment analysis
        result = analyze_sentiment_gemini(cleaned_text)
        
        # Return only sentiment and explanation
        return {
            "text": text,
            "sentiment": result["sentiment"],
            "explanation": result["explanation"]
        }
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def clean_text(text: str) -> str:
    """
    Clean the input text by:
    1. Converting to lowercase
    2. Removing special characters (keeping numbers)
    3. Removing newlines
    4. Removing extra whitespace
    """
    try:
        # Convert to lowercase
        text = text.lower()
        
        # Remove newlines
        text = text.replace('\n', ' ')
        
        # Remove special characters but keep numbers and letters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    except Exception as e:
        print(f"Error in clean_text: {str(e)}")
        raise

@app.post("/issue-escalation")
async def issue_escalation_endpoint(subject:str, text:str):
    try:
        # Print incoming request for debugging
        # print(f"Received subject: {request.subject}")
        # print(f"Received text: {request.text}")
        
        # Clean both subject and text
        cleaned_subject = clean_text(str(subject))
        cleaned_text = clean_text(str(text))
        
        # print(f"Cleaned subject: {cleaned_subject}")
        # print(f"Cleaned text: {cleaned_text}")
        
        # Process body text
        priority_body = issue_escalation(cleaned_text)
        check_escalation_body = required_issue_escalation(priority_body)
        
        # Process subject
        priority_subject = issue_escalation(cleaned_subject)
        check_escalation_subject = required_issue_escalation(priority_subject)
        
        # Final escalation check
        final_check_escalation = check_escalation_body or check_escalation_subject
        
        return {
            "subject": subject,
            "text": text,
            "escalation_required": final_check_escalation
        }
        
    except Exception as e:
        # Print full error traceback for debugging
        print("Error occurred:")
        print(traceback.format_exc())
        
        # Return a proper error response
        raise HTTPException(
            status_code=500,
            detail=f"Issue escalation analysis failed: {str(e)}"
        )

def preprocess_text(text):
    # Tokenize the text
    
    
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')
    
    tokens = nltk.word_tokenize(text.lower())

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    stop_words.remove("not")
    stop_words.remove("don't")
    tokens = [token for token in tokens if token not in stop_words]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]

    return " ".join(tokens)




@app.post("/response-automation")
def response_automation(email: EmailStr, subject:str, text:str):
    try:
        
        # product_subject = get_product_subject(str(subject))
        # if not product_subject:
        #     product_body = get_product_body(str(text))
        
        response = rag_pipeline(subject +" "+ text)
        
        # ticket = subject 
        
        # processed_ticket = preprocess_text(ticket)
        
        # input_vector = vectorizer.fit_transform([processed_ticket])
    
        # # Apply PCA transformations
        # input_pca = pca_model.transform(input_vector.toarray())
        
        # # Predict the cluster for the input PCA vector
        # prediction = kmeans_model.predict(input_pca)
        
        return {
            "Email": email,
            "Subject":subject,
            "Body":text,
            "Response":response
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# Replace this with your Zapier webhook URL
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/21630305/2afz1n8/"

@app.post("/webhook")
def send_email(to_email: EmailStr, subject: str, message: str):
    # Validate the input

    if not to_email or "@" not in to_email:
        raise HTTPException(status_code=400, detail="Invalid recipient email address")

    # Prepare the payload for Zapier
    payload = {
        "to_email": to_email,
        "subject": subject,
        "message": message
    }

    try:
        # Send the data to Zapier webhook
        response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return {"status": "success", "detail": "Email sent successfully via Zapier"}
    except requests.exceptions.RequestException as e:
        # Handle any errors from the request
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

load_dotenv()

# MongoDB Atlas connection setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    MONGODB_URI = "mongodb+srv://suyashg1975:MgDILwn3bI0vxAsU@cluster0.vmfci.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(MONGODB_URI)
    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas")
    
    db = client['customer_support']
    issues_collection = db['issues']
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")
    raise


@app.post("/save-issue")
def save_issue(email: EmailStr, subject:str, text:str):
    try:
        # Create document to insert
        cleaned_subject = clean_text(str(subject))
        cleaned_text = clean_text(str(text))
        
        # print(f"Cleaned subject: {cleaned_subject}")
        # print(f"Cleaned text: {cleaned_text}")
        
        # Process body text
        priority_body = issue_escalation(cleaned_text)
        check_escalation_body = required_issue_escalation(priority_body)
        
        # Process subject
        priority_subject = issue_escalation(cleaned_subject)
        check_escalation_subject = required_issue_escalation(priority_subject)
        
        # Final escalation check
        final_check_escalation = check_escalation_body or check_escalation_subject
        
        response = rag_pipeline(subject +" "+ text)
        
        if final_check_escalation:
            issue_document = {
            "email": email,
            "subject": subject,
            "text": text,
            "escalation_required": final_check_escalation,
            "created_at": datetime.utcnow()
        }
        else:
            
            issue_document = {
                "email": email,
                "subject": subject,
                "text": text,
                "response":response,
                "created_at": datetime.utcnow()
            }
        
        send_email(email,subject,response)
        # Insert into MongoDB Atlas
        result = issues_collection.insert_one(issue_document)
        
        
        return {
            "status": "success",
            "message": "Issue saved successfully and solution has been Send to you Email to MongoDB Atlas",
            "issue_id": str(result.inserted_id)
        }
    except Exception as e:
        print(f"MongoDB Error: {str(e)}")  # For debugging
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save issue: {str(e)}"
        )

def main():
    try:
        # Start ngrok tunnel
        port = 8000
        public_url = ngrok.connect(port).public_url
        print(f'Public URL: {public_url}')
        
        # Start FastAPI
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Startup error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
