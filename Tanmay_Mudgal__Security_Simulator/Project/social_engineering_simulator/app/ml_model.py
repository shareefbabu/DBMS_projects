import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
import pickle
import os

class PersonalizationEngine:
    def __init__(self):
        self.model = KNeighborsClassifier(n_neighbors=3)
        self.is_trained = False
        self.model_path = 'ml_model.pkl'
        self.kmeans = None
        
    def calculate_user_features(self, responses_by_type, impute_missing=False):
        """
        Calculate enhanced user feature vector from their response history
        responses_by_type: dict with keys 'Phishing', 'Baiting', 'Pretexting'
        Each contains list of response objects
        
        Returns: list of features for ML model
        """
        features = []
        
        # Feature 1-3: Accuracy rates per scenario type
        for scenario_type in ['Phishing', 'Baiting', 'Pretexting']:
            type_responses = responses_by_type.get(scenario_type, [])
            if type_responses:
                accuracy = sum(1 for r in type_responses if r.is_correct) / len(type_responses)
            else:
                accuracy = 0.5 if impute_missing else 0.0  # Default 0.0 for display, 0.5 for ML training
            features.append(accuracy)
        
        # Feature 4: Average response time (normalized)
        all_responses = [r for responses in responses_by_type.values() for r in responses]
        if all_responses and any(r.response_time for r in all_responses):
            valid_times = [r.response_time for r in all_responses if r.response_time]
            avg_time = np.mean(valid_times) if valid_times else 60
            # Normalize time to 0-1 range (assuming max 120 seconds)
            normalized_time = min(avg_time / 120.0, 1.0)
        else:
            normalized_time = 0.5
        features.append(normalized_time)
        
        # Feature 5: Total attempts (normalized, indicates engagement)
        total_attempts = len(all_responses)
        normalized_attempts = min(total_attempts / 50.0, 1.0)  # Normalize to 50 attempts
        features.append(normalized_attempts)
        
        # Feature 6: Recent performance trend (last 5 vs previous)
        if len(all_responses) >= 10:
            recent_accuracy = sum(1 for r in all_responses[-5:] if r.is_correct) / 5
            previous_accuracy = sum(1 for r in all_responses[-10:-5] if r.is_correct) / 5
            trend = recent_accuracy - previous_accuracy  # Positive = improving
        else:
            trend = 0
        features.append(trend)
        
        # Feature 7: Consistency score (std deviation of accuracy)
        if len(all_responses) >= 5:
            # Calculate rolling accuracy
            accuracies = [r.is_correct for r in all_responses]
            if len(accuracies) >= 5:
                consistency = 1 - np.std(accuracies)  # Higher = more consistent
            else:
                consistency = 0.5
        else:
            consistency = 0.5
        features.append(consistency)
        
        return features
    
    def get_difficulty_level(self, user_features):
        """
        Determine appropriate difficulty level based on user performance
        
        Args:
            user_features: Feature vector from calculate_user_features
            
        Returns:
            'Easy', 'Medium', or 'Hard'
        """
        if len(user_features) < 3:
            return 'Easy'
        
        # Average accuracy across all scenario types
        avg_accuracy = np.mean(user_features[:3])
        total_attempts = user_features[4] * 50  # Denormalize
        
        # Beginners start with Easy
        if total_attempts < 5:
            return 'Easy'
        
        # Adjust based on accuracy
        if avg_accuracy >= 0.8:
            return 'Hard'
        elif avg_accuracy >= 0.6:
            return 'Medium'
        else:
            return 'Easy'
    
    def prepare_training_data(self, all_user_responses):
        """
        Prepare training data from all users
        all_user_responses: dict of {user_id: responses_by_type}
        
        Returns:
            X: feature matrix
            y: target labels (scenario type indices)
        """
        X = []
        y = []
        
        for user_id, responses_by_type in all_user_responses.items():
            features = self.calculate_user_features(responses_by_type, impute_missing=True)
            
            # Target: recommend scenario type where user is weakest 
            # (0=Phishing, 1=Baiting, 2=Pretexting)
            weakest_idx = np.argmin(features[:3])  # First 3 features are accuracy rates
            
            X.append(features)
            y.append(weakest_idx)
        
        return np.array(X), np.array(y)
    
    def train(self, X, y):
        """Train the KNN model"""
        if len(X) >= 3:  # Need at least 3 samples for k=3
            self.model.fit(X, y)
            self.is_trained = True
            
            # Also train clustering model for user segmentation
            if len(X) >= 3:
                n_clusters = min(3, len(X))
                self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                self.kmeans.fit(X)
            
            return True
        return False
    
    def recommend_scenario_type(self, user_features):
        """
        Recommend scenario type based on user features
        Returns: 'Phishing', 'Baiting', or 'Pretexting'
        """
        scenario_types = ['Phishing', 'Baiting', 'Pretexting']
        
        if not self.is_trained or len(user_features) != 7:
            # If not trained, focus on weakest area or random
            if len(user_features) >= 3:
                weakest_idx = np.argmin(user_features[:3])
                return scenario_types[weakest_idx]
            return np.random.choice(scenario_types)
        
        try:
            # Use ML model prediction
            prediction = self.model.predict([user_features])[0]
            return scenario_types[prediction]
        except:
            # Fallback to weakest area
            weakest_idx = np.argmin(user_features[:3])
            return scenario_types[weakest_idx]
    
    def get_user_vulnerability_profile(self, user_features):
        """
        Analyze user's vulnerability profile
        
        Returns:
            dict with vulnerability assessment
        """
        if len(user_features) < 7:
            return {
                'level': 'Unknown',
                'weakest_area': 'Unknown',
                'strongest_area': 'Unknown',
                'recommendation': 'Complete more scenarios for accurate assessment'
            }
        
        scenario_types = ['Phishing', 'Baiting', 'Pretexting']
        accuracies = user_features[:3]
        
        weakest_idx = np.argmin(accuracies)
        strongest_idx = np.argmax(accuracies)
        avg_accuracy = np.mean(accuracies)
        
        # Determine overall vulnerability level
        if avg_accuracy >= 0.8:
            level = 'Low'
        elif avg_accuracy >= 0.6:
            level = 'Medium'
        else:
            level = 'High'
        
        return {
            'level': level,
            'weakest_area': scenario_types[weakest_idx],
            'strongest_area': scenario_types[strongest_idx],
            'phishing_accuracy': round(accuracies[0] * 100, 1),
            'baiting_accuracy': round(accuracies[1] * 100, 1),
            'pretexting_accuracy': round(accuracies[2] * 100, 1),
            'average_accuracy': round(avg_accuracy * 100, 1),
            'recommendation': f'Focus on {scenario_types[weakest_idx]} scenarios to improve'
        }
    
    def save_model(self):
        """Save trained model to disk"""
        if self.is_trained:
            model_data = {
                'model': self.model,
                'kmeans': self.kmeans,
                'is_trained': self.is_trained
            }
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            return True
        return False
    
    def load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data.get('model', self.model)
                    self.kmeans = model_data.get('kmeans', None)
                    self.is_trained = model_data.get('is_trained', False)
                return True
            except:
                return False
        return False

# Global instance
ml_engine = PersonalizationEngine()
ml_engine.load_model()
