import re
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from pathlib import Path

# Download stopwords if not already downloaded
nltk.download('stopwords')

# Resolve paths to avoid issues with backslashes
base_path = Path("evaluation/SA_model")  # Base path for your model directory
model_path = base_path / "best_svm_classifier.pkl"  # Path to the trained model
tfidf_vectorizer_path = base_path / "c2_Tfidf_Sentiment_Model.pkl"  # Path to the TF-IDF vectorizer

# Load the saved model and vectorizer
try:
    model = joblib.load(model_path)
    tfidf_vectorizer = joblib.load(tfidf_vectorizer_path)
except FileNotFoundError as e:
    raise FileNotFoundError(f"Could not load required files: {e}")

# Initialize PorterStemmer and stopwords
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
stop_words.remove('not')  # Retain 'not' for sentiment context

def predict_sentiment(comment):
    """
    Predict the sentiment of a given comment.

    Parameters:
        comment (str): The input comment.

    Returns:
        str: Predicted sentiment label (e.g., 'Positive', 'Negative', or 'Neutral').
    """
    # Preprocess the comment
    comment = re.sub('[^a-zA-Z]', ' ', comment)  # Remove non-alphabetic characters
    comment = comment.lower()  # Convert text to lowercase
    comment = comment.split()  # Split text into words
    comment = [ps.stem(word) for word in comment if word not in stop_words]  # Stem and remove stopwords
    comment = ' '.join(comment)  # Join words back together into a single string

    # Transform the comment using the saved TF-IDF vectorizer
    transformed_comment = tfidf_vectorizer.transform([comment]).toarray()

    # Predict sentiment using the trained model
    sentiment = model.predict(transformed_comment)[0]

    return sentiment
