# Customer Support Ticket Analysis and Issue Prevention System(Infosys Springboard Internship)

This repository contains the implementation of a **Customer Support Ticket Analysis and Prevention System** developed as part of my Infosys Springboard Internship. The project is designed to enhance the efficiency of customer support by leveraging sentiment analysis, automated response generation, and issue escalation handling, integrated seamlessly using FastAPI and Zapier.

## Importance of Customer Support Ticket Analysis
In today's fast-paced world, customer satisfaction is pivotal for any organization. Analyzing customer support tickets helps identify recurring issues, gauge customer sentiment, and streamline response mechanisms. This not only enhances the customer experience but also reduces the workload on support teams, allowing them to focus on critical tasks.

---

## Project Structure

### Initial Data Analysis
The project begins with an exploratory **data analysis** conducted on two datasets located in the `analysis` folder under the `rough` directory. This step was crucial to:
1. Understand the structure and quality of the data.
2. Identify patterns and trends that inform the subsequent machine learning models.

---

### Sentiment Analysis 
This module determines the sentiment of the user based on their ticket. By classifying tickets into positive, neutral, or negative sentiments, the system:
- Prioritizes tickets requiring immediate attention.
- Provides insights into the overall customer satisfaction levels.

Key steps:
1. Preprocessing ticket data.
2. Training and testing a sentiment classification model.
3. Outputting the sentiment score for each ticket.

## Some Results (screenshots)
**This is an image of how the data is spread for different issues using heatmap**
![image](https://github.com/user-attachments/assets/dc7e5fa5-90c9-4c56-aab0-80318e5bcf5d)

**Test Cases with sentiment prediction and thought**
<img width="918" alt="image" src="https://github.com/user-attachments/assets/3ee9c095-0fcd-463c-87cb-8140a55f6966" />

**This is a confusion matrix of seeing how the predicted labels (done by gemini is actually matching the true labels or not(100 data points)) and then we add examples in the prompt for sentiment analysis**
![image](https://github.com/user-attachments/assets/1a8dee8b-0570-44c6-933b-9869f63906fc)

**F1 scores found, as you can see there are multiple f1 scores calculated and based on the scores we are improving the model by analysisng the data more and adding more examples or better examples**
<img width="314" alt="image" src="https://github.com/user-attachments/assets/98b36e3e-0192-42a3-b34b-c83f512beda0" />

---

### Issue Escalation
This module identifies tickets requiring escalation based on specific keywords and patterns. If an issue is marked for escalation:
- The ticket is forwarded to a human agent for review.
- Automated responses are bypassed to ensure personalized handling.

Key steps:
1. Keyword-based filtering and rule-based classification.
2. Forwarding flagged tickets for manual intervention.

---

### Response Automation
This module generates automated responses for tickets using two distinct approaches:

1. **Classical Machine Learning and Transformer-based Classification**:
   - Products are classified based on ticket content.
   - Predefined templates generate responses tailored to the classified product category.


**Some results (screenshots)**

- This is a cluster visdualisation of products
   <img width="452" alt="image" src="https://github.com/user-attachments/assets/7dae6bfb-f393-460a-835b-1e35acdb60bc" />


- Some top issues on each cluster
  <img width="422" alt="image" src="https://github.com/user-attachments/assets/39a09618-2ee1-4975-9ead-a4c9a35fd2ed" />

  
- automated response on a prompt
  <img width="695" alt="image" src="https://github.com/user-attachments/assets/f66730b6-e1c4-4499-b547-747b44b43398" />

2. **Pipeline Using Gemini and Vector Search**:
   - Embeddings are created using the ticket content.
   - Vector search retrieves the most relevant response.
   - A personalized response is generated based on context and user history.

---

### Integration with FastAPI and Zapier
The entire system is integrated using FastAPI to expose API endpoints for each module. These endpoints are connected through Zapier to:
- Automate workflows and email responses.
- Seamlessly handle escalations and response generation.

## Zapier integration screenshot (trigger and action)

- This is zapier interface to set webhook as trigger and send email as action-
   <img width="323" alt="image" src="https://github.com/user-attachments/assets/477de23a-82fa-43a9-a0c5-2e780bbb9449" />

- Trigger fields for send email (api configured hence options show up)
  <img width="377" alt="image" src="https://github.com/user-attachments/assets/2ac6650e-a010-466c-8789-f105bc2cd638" />

This integration ensures:
- Scalability of the system.
- A unified platform for executing all functionalities.
- Sent email response (not formatted properly)
  ![image](https://github.com/user-attachments/assets/688db775-dec4-40ea-90cc-f944de481ece)

---

## Requirements
### Data
The `data` folder contains all datasets used in this project. Ensure to download the data for running the modules.

### Keys and Dependencies
To run the system, the following keys and dependencies are required:

1. **JSON Key for Google Sheets**
   - [Generate a Google Sheets API Key](https://developers.google.com/sheets/api/quickstart/python)

2. **Gemini API Key**
   - [Sign up for Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)

3. **Pinecone API DOCS**
   - [Get a Pinecone API Key](https://docs.pinecone.io/reference/api/introduction)

4. **Dataset**
   - Download from the `data` folder in this repository.

5. **FastAPI and Uvicorn**
   - Install using:
     ```bash
     pip install fastapi uvicorn
     ```

---

## Conclusion
This Customer Support Ticket Analysis and Prevention System is a comprehensive solution for modern customer support challenges. By combining sentiment analysis, issue escalation, and automated responses, the system optimizes ticket handling and ensures customer satisfaction. The seamless integration with FastAPI and Zapier makes it scalable and adaptable to diverse business needs.
