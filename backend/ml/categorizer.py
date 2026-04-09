import os
import re
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import mysql.connector

# Base directory for the ML module
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'model_store')
MODEL_PATH = os.path.join(MODEL_DIR, 'nb_model.pkl')
SEED_DATA_PATH = os.path.join(BASE_DIR, 'training_data.csv')

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

class RuleBasedCategorizer:
    """Fast regex/keyword based categorizer."""
    
    def __init__(self):
        # Dictionary mapping category names to regex patterns
        self.rules = {
            "Food": re.compile(r'\b(grocery|uber eats|zomato|restaurant|coffee|pizza|mcdonald|starbucks|burger|subway)\b', re.IGNORECASE),
            "Transport": re.compile(r'\b(uber|ola|metro|fuel|petrol|cab|flight|train|bus|gas station|lyft)\b', re.IGNORECASE),
            "Utilities": re.compile(r'\b(electric|water bill|electricity|internet|broadband|xfinity|at&t|wifi)\b', re.IGNORECASE),
            "Healthcare": re.compile(r'\b(pharmacy|hospital|doctor|medicine|clinic|dental|health)\b', re.IGNORECASE),
            "Entertainment": re.compile(r'\b(netflix|spotify|cinema|movie|game|steam|hulu|show|concert)\b', re.IGNORECASE),
            "Shopping": re.compile(r'\b(amazon|flipkart|clothes|shoes|mall|zara|h&m|nike|store)\b', re.IGNORECASE),
            "Salary": re.compile(r'\b(salary|payroll|wages|income|bonus)\b', re.IGNORECASE),
            "Rent": re.compile(r'\b(rent|lease|apartment|housing)\b', re.IGNORECASE),
            "Investments": re.compile(r'\b(mutual fund|stock|sip|deposit|crypto|coinbase|robinhood)\b', re.IGNORECASE),
            "Education": re.compile(r'\b(course|udemy|college|tuition|books|university|school)\b', re.IGNORECASE)
        }

    def predict(self, description: str):
        for category, pattern in self.rules.items():
            if pattern.search(description):
                return category
        return None

class NaiveBayesCategorizer:
    """Machine Learning categorizer using TF-IDF and Naive Bayes."""
    
    def __init__(self):
        self.model = None

    def load(self):
        """Load the model from disk if it exists."""
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            return True
        return False

    def train(self, X_train, y_train):
        """Train the TF-IDF + MultinomialNB pipeline and save to disk."""
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))),
            ('clf', MultinomialNB(alpha=0.1)) # alpha < 1 to handle sparse data better
        ])
        
        self.model.fit(X_train, y_train)
        joblib.dump(self.model, MODEL_PATH)

    def predict(self, description: str):
        """Predict the category and return confidence."""
        if not self.model:
            return None, 0.0

        probs = self.model.predict_proba([description])[0]
        max_prob_idx = probs.argmax()
        confidence = probs[max_prob_idx]
        category = self.model.classes_[max_prob_idx]

        return category, confidence

class CategoryEngine:
    """Facade for the dual-mode categorization system."""
    
    def __init__(self, db_config):
        self.rule_based = RuleBasedCategorizer()
        self.naive_bayes = NaiveBayesCategorizer()
        self.db_config = db_config
        self.confidence_threshold = 0.55
        
        # Load the ML model, train it if it doesn't exist
        if not self.naive_bayes.load():
            self.retrain_model()

    def retrain_model(self):
        """Retrain the Naive Bayes model using seed data + DB user corrections."""
        print("Training Naive Bayes Category Model...")
        
        # 1. Load seed data
        df_seed = pd.DataFrame(columns=['description', 'category'])
        if os.path.exists(SEED_DATA_PATH):
            df_seed = pd.read_csv(SEED_DATA_PATH)
            
        # 2. Augment seed data (duplicate it to give it more weight over sparse corrections during early stages)
        X_data = df_seed['description'].tolist() * 5
        y_data = df_seed['category'].tolist() * 5
        
        # 3. Load DB actual transactions + user corrections
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Get actual transactions that were manually categorized (auto_categorized = 0)
            cursor.execute("""
                SELECT t.description, c.category_name 
                FROM transactions t
                JOIN categories c ON t.category_id = c.category_id
                WHERE t.auto_categorized = 0 AND t.description IS NOT NULL AND t.description != ''
            """)
            for row in cursor.fetchall():
                X_data.append(row['description'])
                y_data.append(row['category_name'])
                
            # Get user corrections and give them high weight (x10)
            cursor.execute("""
                SELECT uc.original_description, c.category_name
                FROM user_corrections uc
                JOIN categories c ON uc.corrected_category_id = c.category_id
            """)
            for row in cursor.fetchall():
                X_data.extend([row['original_description']] * 10)
                y_data.extend([row['category_name']] * 10)
                
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error loading DB data for training: {err}")
            
        # 4. Train model if we have data
        if len(X_data) > 0:
            self.naive_bayes.train(X_data, y_data)
            print(f"Model trained successfully on {len(X_data)} samples.")
        else:
            print("No data available to train the model.")

    def predict(self, description: str):
        """
        Return {category, confidence, method}
        Runs rules first, falls back to Naive Bayes.
        """
        if not description or not str(description).strip():
            return "Miscellaneous", 0.0, "default"
            
        # 1. Rule-based
        rule_category = self.rule_based.predict(description)
        if rule_category:
            return rule_category, 1.0, "rule-based"
            
        # 2. Machine Learning
        ml_category, confidence = self.naive_bayes.predict(description)
        if ml_category and confidence >= self.confidence_threshold:
            return ml_category, float(confidence), "machine-learning"
            
        return "Miscellaneous", float(confidence) if ml_category else 0.0, "default"
