Customer Support Ticket Analysis and Issue Prevention System(Infosys Springboard Internship)
This repository contains the implementation of a Customer Support Ticket Analysis and Prevention System developed as part of my Infosys Springboard Internship. The project is designed to enhance the efficiency of customer support by leveraging sentiment analysis, automated response generation, and issue escalation handling, integrated seamlessly using FastAPI and Zapier.

Importance of Customer Support Ticket Analysis
In today's fast-paced world, customer satisfaction is pivotal for any organization. Analyzing customer support tickets helps identify recurring issues, gauge customer sentiment, and streamline response mechanisms. This not only enhances the customer experience but also reduces the workload on support teams, allowing them to focus on critical tasks.

Project Structure
Initial Data Analysis
The project begins with an exploratory data analysis conducted on two datasets located in the analysis folder under the rough directory. This step was crucial to:

Understand the structure and quality of the data.
Identify patterns and trends that inform the subsequent machine learning models.
Sentiment Analysis
This module determines the sentiment of the user based on their ticket. By classifying tickets into positive, neutral, or negative sentiments, the system:

Prioritizes tickets requiring immediate attention.
Provides insights into the overall customer satisfaction levels.
Key steps:

Preprocessing ticket data.
Training and testing a sentiment classification model.
Outputting the sentiment score for each ticket.
Some Results (screenshots)
This is an image of how the data is spread for different issues using heatmap image

Test Cases with sentiment prediction and thought image

This is a confusion matrix of seeing how the predicted labels (done by gemini is actually matching the true labels or not(100 data points)) and then we add examples in the prompt for sentiment analysis image

F1 scores found, as you can see there are multiple f1 scores calculated and based on the scores we are improving the model by analysisng the data more and adding more examples or better examples image

Issue Escalation
This module identifies tickets requiring escalation based on specific keywords and patterns. If an issue is marked for escalation:

The ticket is forwarded to a human agent for review.
Automated responses are bypassed to ensure personalized handling.
Key steps:

Keyword-based filtering and rule-based classification.
Forwarding flagged tickets for manual intervention.
Response Automation
This module generates automated responses for tickets using two distinct approaches:

Classical Machine Learning and Transformer-based Classification:
Products are classified based on ticket content.
Predefined templates generate responses tailored to the classified product category.
Some results (screenshots)

This is a cluster visdualisation of products image

Some top issues on each cluster image

automated response on a prompt image

Pipeline Using Gemini and Vector Search:
Embeddings are created using the ticket content.
Vector search retrieves the most relevant response.
A personalized response is generated based on context and user history.
Integration with FastAPI and Zapier
The entire system is integrated using FastAPI to expose API endpoints for each module. These endpoints are connected through Zapier to:

Automate workflows and email responses.
Seamlessly handle escalations and response generation.
Zapier integration screenshot (trigger and action)
This is zapier interface to set webhook as trigger and send email as action- image

Trigger fields for send email (api configured hence options show up) image

This integration ensures:

Scalability of the system.
A unified platform for executing all functionalities.
Sent email response (not formatted properly) image
Requirements
Data
The data folder contains all datasets used in this project. Ensure to download the data for running the modules.

Keys and Dependencies
To run the system, the following keys and dependencies are required:

JSON Key for Google Sheets

Generate a Google Sheets API Key
Gemini API Key

Sign up for Gemini API Key
Pinecone API DOCS

Get a Pinecone API Key
Dataset

Download from the data folder in this repository.
FastAPI and Uvicorn

Install using:
pip install fastapi uvicorn
Conclusion
This Customer Support Ticket Analysis and Prevention System is a comprehensive solution for modern customer support challenges. By combining sentiment analysis, issue escalation, and automated responses, the system optimizes ticket handling and ensures customer satisfaction. The seamless integration with FastAPI and Zapier makes it scalable and adaptable to diverse business needs.
