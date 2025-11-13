"""
Score Prediction Model
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import warnings
warnings.filterwarnings('ignore')

class ScorePredictor:
    """Predict team scores"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_training_data(self, datasets, feature_engineer):
        """Prepare training data from historical matches"""
        matches = datasets['match_summary']
        
        X = []
        y = []
        
        print("Preparing score prediction training data...")
        
        for idx, match in matches.iterrows():
            if pd.isna(match.get('team_runs1')):
                continue
            
            team = match.get('batting_team1', match.get('team1'))
            opponent = match.get('batting_team2', match.get('team2'))
            venue = match.get('venue', '')
            score = match.get('team_runs1', 0)
            
            if not team or not opponent or score == 0:
                continue
            
            try:
                # Create features for batting team
                team_strength = feature_engineer.create_team_strength_vector(team)
                opp_strength = feature_engineer.create_team_strength_vector(opponent)
                venue_features = feature_engineer.create_venue_features(venue)
                team_form = feature_engineer.calculate_form_score(team)
                
                # Combine features
                features = np.concatenate([
                    team_strength,
                    opp_strength[:5],  # Opponent bowling strength
                    venue_features,
                    [team_form]
                ])
                
                X.append(features)
                y.append(score)
                
            except Exception as e:
                continue
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"✓ Prepared {len(X)} score training samples")
        
        return X, y
    
    def train(self, X, y):
        """Train score prediction model"""
        print("Training score predictor...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Try multiple models
        models = {
            'Random Forest': RandomForestRegressor(
                n_estimators=200,
                max_depth=12,
                min_samples_split=5,
                random_state=42
            ),
            'XGBoost': xgb.XGBRegressor(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=150,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        best_mae = float('inf')
        best_model_name = None
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"{name}: MAE={mae:.2f}, R²={r2:.4f}")
            
            if mae < best_mae:
                best_mae = mae
                best_model_name = name
                self.model = model
        
        print(f"\n✓ Best model: {best_model_name} (MAE: {best_mae:.2f})")
        
        self.is_trained = True
        
        return best_mae
    
    def predict_score(self, team, opponent, venue, feature_engineer):
        """Predict total score"""
        if not self.is_trained:
            print("⚠ Model not trained yet!")
            return {
                'predicted_score': 150,
                'range_min': 130,
                'range_max': 170,
                'confidence': 'Low'
            }
        
        # Create features
        team_strength = feature_engineer.create_team_strength_vector(team)
        opp_strength = feature_engineer.create_team_strength_vector(opponent)
        venue_features = feature_engineer.create_venue_features(venue)
        team_form = feature_engineer.calculate_form_score(team)
        
        features = np.concatenate([
            team_strength,
            opp_strength[:5],
            venue_features,
            [team_form]
        ])
        
        # Scale
        features_scaled = self.scaler.transform([features])
        
        # Predict
        predicted_score = self.model.predict(features_scaled)[0]
        
        # Estimate confidence interval (±10%)
        range_min = int(predicted_score * 0.9)
        range_max = int(predicted_score * 1.1)
        
        # Calculate confidence based on form and strength
        confidence_score = (team_form + np.mean(team_strength)) / 2
        if confidence_score > 0.6:
            confidence = 'High'
        elif confidence_score > 0.4:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        return {
            'predicted_score': int(predicted_score),
            'range_min': range_min,
            'range_max': range_max,
            'confidence': confidence,
            'powerplay_score': int(predicted_score * 0.3),  # ~30% in powerplay
            'middle_overs_score': int(predicted_score * 0.4),  # ~40% in middle
            'death_overs_score': int(predicted_score * 0.3)  # ~30% in death
        }
    
    def predict_over_by_over(self, team, opponent, venue, feature_engineer, total_overs=20):
        """Predict over-by-over score progression"""
        score_pred = self.predict_score(team, opponent, venue, feature_engineer)
        total_score = score_pred['predicted_score']
        
        # Use typical T20 scoring pattern
        over_scores = []
        cumulative = 0
        
        for over in range(1, total_overs + 1):
            if over <= 6:  # Powerplay
                run_rate = 7.5
            elif over <= 15:  # Middle overs
                run_rate = 7.0
            else:  # Death overs
                run_rate = 9.5
            
            # Add randomness
            runs_in_over = int(run_rate + np.random.normal(0, 1.5))
            runs_in_over = max(0, min(runs_in_over, 20))  # Clamp
            
            cumulative += runs_in_over
            over_scores.append({
                'over': over,
                'runs': runs_in_over,
                'cumulative': cumulative,
                'projected': int((cumulative / over) * total_overs)
            })
        
        # Adjust to match total
        adjustment_factor = total_score / cumulative if cumulative > 0 else 1
        for score in over_scores:
            score['cumulative'] = int(score['cumulative'] * adjustment_factor)
            score['projected'] = int(score['projected'] * adjustment_factor)
        
        return over_scores
    
    def save_model(self, filepath='models/score_predictor.pkl'):
        """Save trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }, filepath)
        print(f"✓ Score model saved to {filepath}")
    
    def load_model(self, filepath='models/score_predictor.pkl'):
        """Load trained model"""
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
            print(f"✓ Score model loaded from {filepath}")
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
    predictor = ScorePredictor()
    
    # Prepare and train
    X, y = predictor.prepare_training_data(datasets, fe)
    predictor.train(X, y)
    
    # Test prediction
    result = predictor.predict_score('India', 'Australia', 'Wankhede Stadium', fe)
    print(f"\nTest Prediction:")
    print(f"India vs Australia at Wankhede")
    print(f"Predicted Score: {result['predicted_score']}")
    print(f"Range: {result['range_min']} - {result['range_max']}")
