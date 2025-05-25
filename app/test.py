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
        
        if predict_escalation(issue_document['subject'],issue_document['text']):
            return {
                "subject":subject,
                'text':text,
                "status":"pending",
                "message":"Issue is Escalated the Customer Support will contact you soon"
            }
        else:
            send_email(email,subject,response)
            # Insert into MongoDB Atlas
            result = issues_collection.insert_one(issue_document)
            
            
            issue_result = {
                "subject":subject,
                "Response":response,
                "status": "success",
                "message": "Issue saved successfully and solution has been Send to your Email to MongoDB Atlas",
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
    st.set_page_config(page_title="AI Enhanced Customer Support System", layout="wide")
    
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
        st.title("AI-Enhanced Customer Support Ticket System")
        selected = option_menu(
            menu_title=None,
            options=["Visualization","Sentiment Analysis", "Issue Escalation", "Automated Response"],
            icons=["bar-chart","emoji-smile", "arrow-up-circle", "chat-dots"],
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
    
    if selected == "Visualization":
        st.header("Data Analysis Visualizations")   
        
        # Create tabs for different types of visualizations
        tab1, tab2, tab3 = st.tabs(["Sentiment Distribution", "Data Analysis", "Response Data Analysis"])
        
        with tab1:
            st.subheader("Sentiment Distribution")
            try:
                st.image("sentiment_analysis_improvement.png", caption="Distribution of Sentiment in Customer Issues", use_container_width=True)
                st.markdown("""
                **Analysis:** This chart shows the distribution of sentiment across customer issues, 
                helping identify overall customer satisfaction trends.
                """)
            except Exception as e:
                st.error("Sentiment distribution image not found. Please ensure the image file exists.")
        
        with tab2:
            st.subheader("Data Analysis of Historical Data")
            try:
                st.image("PCA_scatter_plot_cluster.png", caption="Data Analysis", width = 650)
                st.markdown("""
                **Analysis:** This visualization tracks the frequency and patterns of customer Data over time,
                helping identify potential systemic problems.
                """)
            except Exception as e:
                st.error("Escalation trends image not found. Please ensure the image file exists.")
        
        with tab3:
            st.subheader("Response Data Analysis")
            try:
                st.image("percentage_of_products.png", caption="Response Cluster Analysis", width = 550)
                st.markdown("""
                **Analysis:** This visualization shows the clustering of similar customer issues, helping identify patterns and common problems.
                """)
                
                st.image("percentage_of_issues.png", caption="Response Data Analysis", width = 650)
                st.markdown("""
                **Analysis:** This Analysis shows the cluster distribution of issues of each data or product names in the data trained and embedded.
                """)
                
            except Exception as e:
                st.error("Response time analysis image not found. Please ensure the image file exists.")
        
        # Add a section with catchy content about the project's visualizations
        st.markdown("---")
        st.subheader("📊 Why Our Visualizations Matter")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🔍 **Data-Driven Insights**
            
            Our visualizations transform complex customer support data into clear, actionable insights:
            
            - **Sentiment Analysis**: Understand customer emotions at a glance
            - **Data Clustering**: Identify patterns in customer issues
            - **Response Analysis**: Optimize support team performance
            
            These insights help you make informed decisions and improve customer satisfaction.
            """)
        
        with col2:
            st.markdown("""
            ### 🚀 **Business Impact**
            
            Leveraging these visualizations leads to:
            
            - **Faster Resolution Times**: Identify common issues quickly
            - **Improved Customer Experience**: Address pain points proactively
            - **Better Resource Allocation**: Focus support efforts where needed most
            
            Turn data into a competitive advantage for your support team!
            """)
        
        st.markdown("""
        ---
        **💡 Pro Tip**: The more tickets you process, the more accurate and insightful our visualizations become!
        """)
    
    elif selected == "Sentiment Analysis":
        st.header("Sentiment Analysis")
        
        # Add catchy content about sentiment analysis
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #1f77b4;">
            <h3 style="color: #1f77b4; margin-top: 0;">🔍 Understand Your Customers' Emotions</h3>
            <p style="color: #31333F; font-size: 16px;">Our advanced sentiment analysis technology uses state-of-the-art AI to detect the emotional tone in customer messages. 
            This helps you:</p>
            <ul style="color: #31333F; font-size: 16px;">
                <li>Identify frustrated customers before they escalate</li>
                <li>Recognize positive feedback to highlight success stories</li>
                <li>Understand the overall sentiment trends in your support tickets</li>
            </ul>
            <p style="color: #31333F; font-size: 16px;"><strong>💡 Pro Tip:</strong> Pay special attention to tickets with negative sentiment - they often represent opportunities for improvement!</p>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Add catchy content about issue escalation
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff7f0e;">
            <h3 style="color: #ff7f0e; margin-top: 0;">🚨 Prevent Escalations Before They Happen</h3>
            <p style="color: #31333F; font-size: 16px;">Our AI-powered escalation prediction system analyzes ticket content to identify issues that may require special attention. 
            This proactive approach helps you:</p>
            <ul style="color: #31333F; font-size: 16px;">
                <li>Reduce resolution times for critical issues</li>
                <li>Allocate resources more effectively</li>
                <li>Improve customer satisfaction by addressing problems early</li>
            </ul>
            <p style="color: #31333F; font-size: 16px;"><strong>💡 Pro Tip:</strong> Review the escalation reasons to identify patterns that might indicate systemic issues in your product or service.</p>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    elif selected == "Automated Response":
        st.header("Automated Response Generation")
        
        # Add catchy content about automated responses
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2ca02c;">
            <h3 style="color: #2ca02c; margin-top: 0;">🤖 AI-Powered Responses That Feel Human</h3>
            <p style="color: #31333F; font-size: 16px;">Our automated response system generates personalized, context-aware replies to customer issues. 
            This innovative technology helps you:</p>
            <ul style="color: #31333F; font-size: 16px;">
                <li>Respond to customers 24/7 without human intervention</li>
                <li>Maintain consistent tone and quality across all responses</li>
                <li>Free up your support team to focus on complex issues</li>
            </ul>
            <p style="color: #31333F; font-size: 16px;"><strong>💡 Pro Tip:</strong> While our AI generates excellent responses, always review them for accuracy before sending to ensure the best customer experience.</p>
        </div>
        """, unsafe_allow_html=True)
        
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
                if issue_result['status']=="success":
                    st.success(issue_result['status'])
                    # with col2:
                    st.text_area("Generated Response", issue_result['Response'], height=150)
                    # with col3:
                    st.text_area("Message", issue_result['message'])
                    # with col4:
                    st.metric("Issue ID", issue_result['issue_id'])
                else:
                    st.text_area("Subject", issue_result['subject'])
                    st.text_area("Text", issue_result['text'])
                    st.markdown("""
                        <div style='padding: 20px; background-color: rgba(255, 75, 75, 0.8); color: white; 
                        font-size: 24px; font-weight: bold; border-radius: 10px; 
                        text-align: center; margin: 10px 0px;'>
                        🚨 HIGH PRIORITY ISSUE! 🚨
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    st.success(issue_result['message'])
                
                
                # st.markdown(f"""
                #     <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;">
                #         <p style="margin-bottom: 0.5rem;"><strong>Quick Actions:</strong></p>
                #         <button onclick="navigator.clipboard.writeText('{issue_result['Response']}')" style="padding: 0.5rem 1rem;">
                #             Copy Response
                #         </button>
                #     </div>
                # """, unsafe_allow_html=True)
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
