from fastapi import FastAPI, HTTPException
import uvicorn
from pyngrok import ngrok
from pydantic import BaseModel, EmailStr
from sentiment_analysis import analyze_sentiment_gemini, clean_text
from issue_escalation import required_issue_escalation, issue_escalation
from response_automation import get_product_body, get_product_subject
import re
import traceback
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests


app = FastAPI()

# Load the K-means model, vectorizer, and PCA at startup
with open('kmeans_model.pkl', 'rb') as model_file:
    kmeans_model = pickle.load(model_file)

with open('vectorizer.pkl', 'rb') as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)

with open('pca_model.pkl', 'rb') as pca_file:
    pca_model = pickle.load(pca_file)

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
        
        product_subject = get_product_subject(str(subject))
        if not product_subject:
            product_body = get_product_body(str(text))
        
        ticket = subject 
        
        processed_ticket = preprocess_text(ticket)
        
        input_vector = vectorizer.fit_transform([processed_ticket])
    
        # Apply PCA transformations
        input_pca = pca_model.transform(input_vector.toarray())
        
        # Predict the cluster for the input PCA vector
        prediction = kmeans_model.predict(input_pca)
        
        return {
            "Email": email,
            "Subject":subject,
            "Body":text,
            "Product Name": product_subject or product_body,
            "Cluster-no":int(prediction[0]),
            # 'Type': Type
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# Replace this with your Zapier webhook URL
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/21326674/2k99gpi/"

@app.post("/webhook")
def send_email(from_email: str, to_email: str, subject: str, message: str):
    # Validate the input
    if not from_email or "@" not in from_email:
        raise HTTPException(status_code=400, detail="Invalid sender email address")
    if not to_email or "@" not in to_email:
        raise HTTPException(status_code=400, detail="Invalid recipient email address")

    # Prepare the payload for Zapier
    payload = {
        "from_email": from_email,
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
