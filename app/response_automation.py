# from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import pickle
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

# tokenizer = AutoTokenizer.from_pretrained("dslim/bert-large-NER")
# model = AutoModelForTokenClassification.from_pretrained("dslim/bert-large-NER")

nlp = pipeline("ner", model="dslim/bert-large-NER", tokenizer="dslim/bert-large-NER")

# prompt: how to give input to this kemans saved model 

# Load the saved KMeans model
# filename = 'kmeans_model.pkl'
# loaded_model = pickle.load(open(filename, 'rb'))


# type_model = pickle.load(open('best_model.pkl','rb'))


# # Load necessary artifacts (vectorizer, pca) -  You'll need to save these as well during model training
# vectorizer = pickle.load(open('vectorizer.pkl', 'rb')) #Replace with actual filename
# pca = pickle.load(open('pca_model.pkl', 'rb')) #Replace with actual filename


# def preprocess_text(text):
#     # Tokenize the text
#     tokens = nltk.word_tokenize(text.lower())
#     nltk.download('punkt_tab')
#     nltk.download('punkt', quiet=True)
#     nltk.download('stopwords', quiet=True)
#     nltk.download('wordnet', quiet=True)
#     # Remove stop words
#     stop_words = set(stopwords.words('english'))
#     stop_words.remove("not")
#     stop_words.remove("don't")
#     tokens = [token for token in tokens if token not in stop_words]

#     # Lemmatize the tokens
#     lemmatizer = WordNetLemmatizer()
#     tokens = [lemmatizer.lemmatize(token) for token in tokens]

#     return " ".join(tokens)


# def predict_cluster(new_data):
#     """Predicts the cluster for new data.

#     Args:
#         new_data (str or list): New text data (e.g., a single ticket or a list of tickets).

#     Returns:
#         numpy.ndarray: Predicted cluster labels.
#     """
#     if isinstance(new_data, str):
#         new_data = [new_data]  # Convert single string input to a list

#     preprocessed_new_data = [preprocess_text(text) for text in new_data]
#     new_tfidf = vectorizer.transform(preprocessed_new_data)
#     new_pca_result = pca.transform(new_tfidf.toarray())
#     predicted_cluster = loaded_model.predict(new_pca_result)

#     return predicted_cluster


# Example usage for a single new ticket:
# new_ticket = "Subject: Network issue \n\n\n Body: My internet is down"
# predicted_cluster = predict_cluster(new_ticket)
# print(f"Predicted cluster for new ticket: {predicted_cluster[0]}")

# Example usage for multiple new tickets:
# new_tickets = [
#     "Subject: Printer not working\n\n\nBody: I can't print any documents",
#     "Subject: Software Problem\n\n\nBody: The application is crashing frequently",
# ]
# predicted_clusters = predict_cluster(new_tickets)
# print(f"Predicted clusters for new tickets: {predicted_clusters}")

def get_product_subject(subject):
    bert_token = nlp(subject)   
    product = " ".join([el["word"] for el in bert_token]).replace(" ##", "")
    if len(product) > 1:
        return product
    else:
        return False
    
def get_product_body(body):
    bert_token = nlp(body)
    product = " ".join([el["word"] for el in bert_token]).replace(" ##", "")
    if len(product) > 1:
        return product
    else:
        return False

    
# def predict_type(text):
#     ans = type_model.predict(text)
#     return ans
