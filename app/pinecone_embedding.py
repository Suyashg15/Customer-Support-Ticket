import os
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec

genai.configure(api_key="AIzaSyDS5qxGT3N2XbqibpY8PyFbomKpe0SCkLE")
# Set the API key as an environment variable
os.environ["PINECONE_API_KEY"] = "pcsk_2bdKPV_UktpZEf2xjb96kU2FpdFDh4VJ3278CLWYAp3QkcmQsY5Nwaw2qqdV98gxWPLV27"  # Replace with your actual API key
pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)
index = pc.Index(host="https://customer-support-rag-fgsmox6.svc.aped-4627-b74a.pinecone.io") # Get the Pinecone index object and store it in `index`

def get_gemini_embedding(text):
    response = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response['embedding']

def retrieve_similar_issues(query, top_k=3):
    query_embedding = get_gemini_embedding(query)
    results = index.query(vector = query_embedding, top_k=top_k, include_metadata=True)

    similar_answers = [match["metadata"]["answer"] for match in results["matches"]]
    return similar_answers

# similar_issues = retrieve_similar_issues(query)
# print(similar_issues)

def generate_personalized_response(query, similar_answers):
    prompt = f"""
    Customer Query: {query}
    Similar Issues and Answers: {similar_answers}

    Generate a helpful and personalized solution response based on similar answers.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    return response.text

# personalized_response = generate_personalized_response(query, similar_issues)
# print(personalized_response)

def rag_pipeline(query):
    similar_issues = retrieve_similar_issues(query)
    response = generate_personalized_response(query, similar_issues)
    return response

# final_response = rag_pipeline(query)
# print(final_response)