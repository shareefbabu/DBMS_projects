import os
import json
import numpy as np
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class AIService:
    _instance = None
    
    def __init__(self):
        self.vectorizer = None
        self.vectors = None
        self.questions = []
        self.answers = []
        self._load_knowledge_base()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_knowledge_base(self):
        """Load Q&A pairs from JSON and train TF-IDF model"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, 'chatbot_knowledge.json')
            
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            self.questions = [item['question'] for item in data]
            self.answers = [item['answer'] for item in data]
            
            # Initialize and Fit TF-IDF Vectorizer
            print("DEBUG: Training Local NLP Model...")
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.vectors = self.vectorizer.fit_transform(self.questions)
            print(f"DEBUG: Trained on {len(self.questions)} knowledge pairs.")
            
        except Exception as e:
            print(f"ERROR: Failed to load chatbot knowledge base: {e}")
            self.questions = []
            self.answers = []

    def get_response(self, user_message, context=None):
        """
        Get semantically similar response from local knowledge base.
        """
        if not self.vectorizer or not self.questions:
            return "I'm having trouble accessing my knowledge base."

        try:
            # Vectorize user query
            user_vec = self.vectorizer.transform([user_message])
            
            # Calculate Cosine Similarity
            similarities = cosine_similarity(user_vec, self.vectors).flatten()
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            # Threshold for relevance (0.2 is usually a safe baseline for TF-IDF short text)
            if best_score < 0.2:
                # Handle greeting fallback manually if not in DB
                if any(word in user_message.lower() for word in ['hi', 'hello', 'hey']):
                     return f"Hello {context.get('username', 'there')}! I am your completely free, local AI assistant."
                return "I'm not sure about that. Try asking about 'phishing', 'baiting', or your 'score'."

            answer = self.answers[best_idx]
            
            # Dynamic Context Injection
            # If the answer refers to dynamic data (like scores), we construct it here.
            # Simple heuristic: The knowledge base has generic answers, but we override specific intents
            # OR we format the string if it contains placeholders (advanced).
            # For now, let's keep the specialized logic in routes OR simple injection here.
            
            return answer

        except Exception as e:
            print(f"ERROR: Local NLP generation failed: {e}")
            return "I encountered an error processing your request."
