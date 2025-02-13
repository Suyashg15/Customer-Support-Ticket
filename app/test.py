import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import nltk
from textblob import TextBlob
from sentiment_analysis import analyze_sentiment_gemini, clean_text
from issue_escalation import required_issue_escalation, issue_escalation
from response_automation import get_product_body, get_product_subject
from pinecone_embedding import rag_pipeline
from webhook import send_email
import re
import traceback
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
# import subprocess
# import threading
import google.generativeai as genai
import certifi
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
# from app import sentiment
# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def perform_sentiment_analysis(body):
    try:
        # Clean the input text first
        cleaned_text = clean_text(body)
        
        # Use the cleaned text for sentiment analysis
        result = analyze_sentiment_gemini(cleaned_text)
        
        # Return only sentiment and explanation
        sentiment_result =  {
            "text": body,
            "sentiment": result["sentiment"],
            "explanation": result["explanation"]
        }
        return sentiment_result['sentiment'], sentiment_result['explanation']
    
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

        

def predict_escalation(subject, text):
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
        
        result =  {
            "subject": subject,
            "text": text,
            "escalation_required": final_check_escalation
        }
        
        return result['escalation_required']
        
    except Exception as e:
        # Print full error traceback for debugging
        print("Error occurred:")
        print(traceback.format_exc())
        
        # Use Streamlit's error display instead of HTTPException
        st.error(f"Issue escalation analysis failed: {str(e)}")
        return None  # or return a default value depending on your needs

# def generate_automated_response(title, body):
#     sentiment, polarity, subjectivity = perform_sentiment_analysis(title, body)
#     priority, reasons = predict_escalation(title, body)
    
#     # More contextual responses
#     responses = {
#         "Very Positive": "Thank you for your wonderful feedback! We're thrilled to hear about your positive experience.",
#         "Slightly Positive": "Thank you for your feedback! We're glad to hear about your experience.",
#         "Neutral": "Thank you for reaching out. We'll review your message and get back to you soon.",
#         "Slightly Negative": "We apologize for any inconvenience you've experienced. Our team will look into this matter.",
#         "Very Negative": "We sincerely apologize for your negative experience. This will be escalated to our team immediately for urgent attention."
#     }
    
#     response = responses.get(sentiment, responses["Neutral"])
    
#     # Add priority-based additional message
#     if priority != "Normal Priority":
#         response += f"\n\nThis has been marked as {priority} and will be handled accordingly."
    
#     return response, priority

load_dotenv()

# MongoDB Atlas connection setup
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    MONGODB_URI = "mongodb+srv://suyashg1975:MgDILwn3bI0vxAsU@cluster0.vmfci.mongodb.net/?retryWrites=true&w=majority&ssl=true"

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

def save_issue(email, subject, text):
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
        
        
        issue_result = {
            "subject":subject,
            "Response":response,
            "status": "success",
            "message": "Issue saved successfully and solution has been Send to you Email to MongoDB Atlas",
            "issue_id": str(result.inserted_id)
        }
        return issue_result
    
    except Exception as e:
        print(f"MongoDB Error: {str(e)}")  # For debugging
        st.error(f"Failed to save issue: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to save issue: {str(e)}"
        }


def main():
    st.set_page_config(page_title="Issue Analysis Tool", layout="wide")
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stTextInput > div > div > input {
            padding: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        selected = option_menu(
            menu_title=None,
            options=["Sentiment Analysis", "Issue Escalation", "Automated Response"],
            icons=["emoji-smile", "arrow-up-circle", "chat-dots"],
            menu_icon="cast",
            default_index=0,
        )
        
        # Add some information in sidebar
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This tool helps analyze customer issues by:
        - Determining sentiment
        - Predicting escalation needs
        - Generating automated responses
        """)
    
    if selected == "Sentiment Analysis":
        st.header("Sentiment Analysis")
        
        # Create top-level buttons above inputs
        col1, col2 = st.columns(2)
        with col1:
            run_analysis = st.button("Run Analysis", type="primary", use_container_width=True)
        with col2:
            view_pipeline = st.button("View Pipeline", use_container_width=True)
        
        st.markdown("---")  # Add separator
        
        # Input fields
        title = st.text_input("Issue Title", value="Great customer service experience!")
        body = st.text_area("Issue Body", value="The support team was incredibly helpful and resolved my issue quickly. Really impressed with the service.", height=200)
        
        if run_analysis:
            if body:
                sentiment, explanation= perform_sentiment_analysis(body)
                
                # col1, col2= st.columns(2)
                # with col1:
                sentiment_emojis = {
                    "Positive": "🙂",
                    "Neutral": "😐",
                    "Negative": "🙁",
                    "Frustrated": "😠",
                }
                emoji = sentiment_emojis.get(sentiment, "❓")  # default to question mark if sentiment not found
                st.metric("Sentiment", f"{emoji} {sentiment}")
                # with col2:
                st.text_area('Explanation', explanation)
                # with col2:
                #     st.metric("Polarity Score", f"{polarity:.2f}")
                # with col3:
                #     st.metric("Subjectivity", f"{subjectivity:.2f}")
                
                # # Enhanced visualization
                # st.subheader("Sentiment Visualization")
                # fig_col1, fig_col2 = st.columns(2)
                
                # with fig_col1:
                #     st.markdown("**Polarity (-1 to 1)**")
                #     st.progress((polarity + 1) / 2)
                
                # with fig_col2:
                #     st.markdown("**Subjectivity (0 to 1)**")
                #     st.progress(subjectivity)
            else:
                st.warning("Please enter either a title or body text to analyze")
        
        if view_pipeline:
            st.subheader("Sentiment Analysis Pipeline")
            st.image("sentiment analysis pipeline.jpg",
                    caption="Sentiment Analysis Pipeline",
                    width=600)
            st.markdown("""
            **Pipeline Steps:**
            1. Text Input Processing
            2. LLM API Calling
            3. Sentiment Analysis
            4. Prompt Engineering
            5. Category Classification
            """)
    
    elif selected == "Issue Escalation":
        st.header("Issue Escalation Prediction")
        
        # Create top-level buttons above inputs
        col1, col2 = st.columns(2)
        with col1:
            run_prediction = st.button("Run Prediction", type="primary", use_container_width=True)
        with col2:
            view_pipeline = st.button("View Pipeline", use_container_width=True)
        
        st.markdown("---")  # Add separator
        
        # Input fields
        title = st.text_input("Issue Title", value="URGENT: System down - Cannot access database")
        body = st.text_area("Issue Body", value="Critical error occurred in production. The database is not responding and customers cannot access their accounts. Need immediate assistance!", height=200)
        
        if run_prediction:
            if title or body:
                priority = predict_escalation(title, body)
                
                if priority == True:
                    st.markdown("""
                        <div style='padding: 20px; background-color: rgba(255, 75, 75, 0.8); color: white; 
                        font-size: 24px; font-weight: bold; border-radius: 10px; 
                        text-align: center; margin: 10px 0px;'>
                        🚨 HIGH PRIORITY ISSUE! 🚨
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                else:
                    st.success("✓ Normal Priority Issue")
                
                st.subheader("Analysis Details")
                if priority == True:
                    st.write("**Priority Level:**", "High")
                # if reasons:
                #     st.write("**Reasons:**")
                #     for reason in reasons:
                #         st.write(f"- {reason}")
            else:
                st.warning("Please enter either a title or body text to analyze")
        
        if view_pipeline:
            st.subheader("Issue Escalation Pipeline")
            st.image("issue_escalation pipeline.png",
                    caption="Escalation Prediction Infrastructure",
                    use_container_width=True)
            st.markdown("""
            **Pipeline Steps:**
            1. Text Preprocessing
            2. Keyword Detection
            3. Priority Classification
            4. Reason Attribution
            """)
    
    else:  # Automated Response
        st.header("Automated Response Generation")
        
        # Create top-level buttons above inputs
        col1, col2 = st.columns(2)
        with col1:
            generate_response = st.button("Generate Response", type="primary", use_container_width=True)
        with col2:
            view_pipeline = st.button("View Pipeline", use_container_width=True)
        
        st.markdown("---")  # Add separator
        
        # Input fields
        email = st.text_input(
            "Customer Email",
            placeholder="Enter your email address",
            help="Please enter a valid email address"
        )
        
        # Email validation before proceeding
        if generate_response and email:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email address")
                return
            
        title = st.text_input("Issue Title", value="Bug in login page",key = "issue_subject_main")
        body = st.text_area("Issue Body", value="I'm having trouble logging into my account. The page keeps showing an error message when I enter my credentials.", height=200)
        
        if generate_response:
            if title or body:
                issue_result = save_issue(email,title, body)
                
                # if priority != "Normal Priority":
                #     st.warning(f"Priority: {priority}")
                # col1, col2, col3, col4 = st.columns(4)
                
                # with col1:
                st.metric("Status", issue_result['status'])
                # with col2:
                st.text_area("Generated Response", issue_result['Response'], height=150)
                # with col3:
                st.text_area("Message", issue_result['message'])
                # with col4:
                st.metric("Issue ID", issue_result['issue_id'])
                
                
                st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                        <p style="margin-bottom: 0.5rem;"><strong>Quick Actions:</strong></p>
                        <button onclick="navigator.clipboard.writeText('{issue_result['Response']}')" style="padding: 0.5rem 1rem;">
                            Copy Response
                        </button>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Please enter either a title or body text to generate a response")
        
        if view_pipeline:
            st.subheader("Response Generation Pipeline")
            st.image("response automation pipeline.jpg",
                    caption="Automated Response Infrastructure",
                    use_container_width=True)
            st.markdown("""
            **Pipeline Steps:**
            1. Text Analysis
            2. Sentiment Detection
            3. Priority Assessment
            4. Template Selection
            5. Response Generation
            """)

if __name__ == "__main__":
    main()
