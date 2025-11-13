"""
Match Outcome Prediction Model
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import joblib
import warnings
warnings.filterwarnings('ignore')

class MatchPredictor:
    """Predict match outcomes"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_training_data(self, datasets, feature_engineer):
        """Prepare training data from historical matches"""
        matches = datasets['match_summary']
        
        X = []
        y = []
        match_info = []
        
        print("Preparing training data...")
        
        for idx, match in matches.iterrows():
            if pd.isna(match['winner']) or match['winner'] == '':
                continue
                
            team1 = match['team1']
            team2 = match['team2']
            venue = match.get('venue', '')
            winner = match['winner']
            
            if not team1 or not team2 or not winner:
                continue
            
            try:
                # Create features
                features = feature_engineer.create_match_features(
                    team1, team2, venue
                )
                
                # Label: 1 if team1 wins, 0 if team2 wins
                label = 1 if winner == team1 else 0
                
                X.append(features)
                y.append(label)
                match_info.append({
                    'team1': team1,
                    'team2': team2,
                    'venue': venue,
                    'winner': winner
                })
                
            except Exception as e:
                continue
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"✓ Prepared {len(X)} training samples")
        
        return X, y, match_info
    
    def train(self, X, y):
        """Train the match prediction model"""
        print("Training match predictor...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Try multiple models
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=10,
                random_state=42
            ),
            'XGBoost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        best_score = 0
        best_model_name = None
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            score = model.score(X_test_scaled, y_test)
            print(f"{name}: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_model_name = name
                self.model = model
        
        print(f"\n✓ Best model: {best_model_name} (Accuracy: {best_score:.4f})")
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Team 2', 'Team 1']))
        
        self.is_trained = True
        
        return best_score
    
    def predict_match(self, team1, team2, venue, feature_engineer, 
                     toss_winner=None, batting_first=None):
        """Predict match outcome with probability"""
        if not self.is_trained:
            print("⚠ Model not trained yet!")
            return {
                'winner': team1,
                'probability': 0.5,
                'team1_prob': 0.5,
                'team2_prob': 0.5,
                'confidence': 'Low'
            }
        
        # Create features
        features = feature_engineer.create_match_features(
            team1, team2, venue, toss_winner, batting_first
        )
        
        # Scale
        features_scaled = self.scaler.transform([features])
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        team1_prob = probabilities[1]
        team2_prob = probabilities[0]
        
        winner = team1 if prediction == 1 else team2
        confidence = 'High' if max(team1_prob, team2_prob) > 0.65 else 'Medium' if max(team1_prob, team2_prob) > 0.55 else 'Low'
        
        return {
            'winner': winner,
            'probability': max(team1_prob, team2_prob),
            'team1_prob': team1_prob,
            'team2_prob': team2_prob,
            'confidence': confidence,
            'margin_estimate': abs(team1_prob - team2_prob) * 50  # Rough margin estimate
        }
    
    def save_model(self, filepath='models/match_predictor.pkl'):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }, filepath)
        print(f"✓ Model saved to {filepath}")
    
    def load_model(self, filepath='models/match_predictor.pkl'):
        """Load trained model"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
            print(f"✓ Model loaded from {filepath}")
        except Exception as e:
            print(f"⚠ Could not load model: {e}")


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from utils.data_loader import DataLoader
    from utils.feature_engineering import FeatureEngineer
    
    # Load data
    loader = DataLoader('../data')
    datasets = loader.load_all_data()
    
    # Feature engineering
    fe = FeatureEngineer(datasets)
    
    # Initialize predictor
    predictor = MatchPredictor()
    
    # Prepare and train
    X, y, match_info = predictor.prepare_training_data(datasets, fe)
    predictor.train(X, y)
    
    # Test prediction
    result = predictor.predict_match('India', 'Australia', 'Wankhede Stadium', fe)
    print(f"\nTest Prediction:")
    print(f"India vs Australia at Wankhede")
    print(f"Winner: {result['winner']}")
    print(f"Probability: {result['probability']:.2%}")
    print(f"Confidence: {result['confidence']}")
