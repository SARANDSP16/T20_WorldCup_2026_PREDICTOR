"""
Train all ML models
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from utils.data_loader import DataLoader
from utils.feature_engineering import FeatureEngineer
from models.match_predictor import MatchPredictor
from models.score_predictor import ScorePredictor

def main():
    print("=" * 60)
    print("T20 WC 2026 - Model Training Pipeline")
    print("=" * 60)
    
    # Load data
    print("\n1. Loading datasets...")
    loader = DataLoader('data')
    datasets = loader.load_all_data()
    
    # Feature engineering
    print("\n2. Setting up feature engineering...")
    fe = FeatureEngineer(datasets)
    
    # Train match predictor
    print("\n3. Training Match Predictor...")
    print("-" * 60)
    match_predictor = MatchPredictor()
    X, y, _ = match_predictor.prepare_training_data(datasets, fe)
    match_predictor.train(X, y)
    match_predictor.save_model('models/match_predictor.pkl')
    
    # Train score predictor
    print("\n4. Training Score Predictor...")
    print("-" * 60)
    score_predictor = ScorePredictor()
    X, y = score_predictor.prepare_training_data(datasets, fe)
    score_predictor.train(X, y)
    score_predictor.save_model('models/score_predictor.pkl')
    
    print("\n" + "=" * 60)
    print("✅ All models trained successfully!")
    print("=" * 60)
    
    # Test predictions
    print("\n5. Testing Models...")
    print("-" * 60)
    
    result = match_predictor.predict_match('India', 'Australia', 'Wankhede Stadium', fe)
    print(f"\nTest Match Prediction: India vs Australia")
    print(f"Winner: {result['winner']}")
    print(f"Probability: {result['probability']:.2%}")
    
    score_result = score_predictor.predict_score('India', 'Australia', 'Wankhede Stadium', fe)
    print(f"\nTest Score Prediction: India vs Australia")
    print(f"Predicted Score: {score_result['predicted_score']}")
    print(f"Range: {score_result['range_min']} - {score_result['range_max']}")
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
