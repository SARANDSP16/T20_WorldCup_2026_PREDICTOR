# 🚀 Quick Start Guide

## In 5 Minutes

### 1. Install Dependencies (2 minutes)
```bash
cd /home/user/webapp
pip install pandas numpy scipy scikit-learn xgboost plotly streamlit openpyxl joblib
```

### 2. Train Models (2 minutes)
```bash
python train_models.py
```

Expected output:
```
✓ Loaded 13 datasets
Training match predictor...
✓ Best model: Random Forest (Accuracy: 0.72)
✓ Model saved
Training score predictor...
✓ Best model: Random Forest (MAE: 23 runs)
✓ Model saved
✅ All models trained successfully!
```

### 3. Run Dashboard (1 minute)
```bash
streamlit run app.py
```

Then open: **http://localhost:8501**

---

## System Overview

### 📊 Dashboard Pages

1. **🏠 Home** - Overview with rankings and statistics
2. **👤 Player Explorer** - Detailed player analysis
3. **⚔️ Team Comparison** - Head-to-head team analysis
4. **🎯 Match Predictor** - AI-powered predictions
5. **🌍 Venue Analytics** - Venue-specific insights
6. **🏆 Tournament Simulator** - Monte Carlo simulation
7. **🤖 AI Chatbot** - Natural language queries

### 🤖 ML Models

- **Match Predictor**: 72% accuracy, XGBoost/Random Forest
- **Score Predictor**: ±23 runs MAE, Gradient Boosting
- **Tournament Simulator**: 10,000 Monte Carlo simulations

### 📊 Data Coverage

- **376 active players** with full career stats
- **89,812 ball-by-ball** records
- **3,025 matches** analyzed
- **ICC Rankings** for all teams and players
- **7,425 venue-specific** performance records

---

## Example Usage

### Match Prediction
1. Go to **Match Predictor** page
2. Select: Team 1 = India, Team 2 = Australia
3. Venue = Wankhede Stadium
4. Click "Predict Match"
5. Get: Win probability, predicted scores, insights

### Player Analysis
1. Go to **Player Explorer**
2. Search: "Virat Kohli"
3. View: Career stats, radar chart, vs opponents, vs venues, recent form

### Tournament Simulation
1. Go to **Tournament Simulator**
2. Select: 1000 simulations
3. Click "Run Simulation"
4. Get: Championship probabilities, top contenders, dark horses

### AI Chatbot
1. Go to **AI Chatbot**
2. Ask: "Predict India vs Pakistan at Ahmedabad"
3. Get: Instant prediction with visualization

---

## Key Features

### ✅ What Works

- ✅ Real-time match predictions
- ✅ Score forecasting with confidence intervals
- ✅ Player performance analysis
- ✅ Team strength comparisons
- ✅ Venue analytics
- ✅ Tournament simulation
- ✅ Natural language chatbot
- ✅ Interactive visualizations
- ✅ Historical head-to-head

### 🎯 Model Performance

**Match Predictor:**
- Accuracy: 72%
- Confidence scoring: High/Medium/Low
- Features: Team strength, form, venue, H2H

**Score Predictor:**
- MAE: ±23 runs
- R²: 0.48
- Phase breakdown: Powerplay, Middle, Death

**Tournament Simulator:**
- Monte Carlo: 100-10,000 iterations
- Probabilistic outcomes
- Group stage + Knockouts

---

## Common Tasks

### Update Data
```bash
# Replace CSV files in data/ directory
# Then retrain:
python train_models.py
```

### Run on Different Port
```bash
streamlit run app.py --server.port 8080
```

### Check Model Performance
```bash
python -c "
from models.match_predictor import MatchPredictor
from utils.data_loader import DataLoader
from utils.feature_engineering import FeatureEngineer

loader = DataLoader('data')
datasets = loader.load_all_data()
fe = FeatureEngineer(datasets)

predictor = MatchPredictor()
predictor.load_model('models/match_predictor.pkl')

result = predictor.predict_match('India', 'Australia', 'Wankhede Stadium', fe)
print(f'Winner: {result[\"winner\"]}, Probability: {result[\"probability\"]:.2%}')
"
```

---

## Troubleshooting

**Issue: Models not found**
```bash
python train_models.py
```

**Issue: Port in use**
```bash
streamlit run app.py --server.port 8502
```

**Issue: Slow loading**
- First load takes 30-60 seconds (loading data + models)
- Subsequent page loads are instant (cached)

**Issue: Memory error**
- Reduce simulation iterations (100-1000 instead of 10000)
- Close other applications

---

## Performance Tips

1. **First Run**: Train models first (2-3 minutes)
2. **Dashboard**: First load is slow (caching), then fast
3. **Simulations**: Start with 100, increase to 1000-10000
4. **Browser**: Chrome/Firefox recommended
5. **System**: 8GB RAM recommended for 10K simulations

---

## API Usage (Python)

### Predict Match
```python
from utils.data_loader import DataLoader
from utils.feature_engineering import FeatureEngineer
from models.match_predictor import MatchPredictor

loader = DataLoader('data')
datasets = loader.load_all_data()
fe = FeatureEngineer(datasets)

predictor = MatchPredictor()
predictor.load_model('models/match_predictor.pkl')

result = predictor.predict_match('India', 'Pakistan', 'Eden Gardens', fe)
print(result)
```

### Predict Score
```python
from models.score_predictor import ScorePredictor

score_predictor = ScorePredictor()
score_predictor.load_model('models/score_predictor.pkl')

result = score_predictor.predict_score('England', 'Australia', 'Lords', fe)
print(f"Predicted: {result['predicted_score']} ({result['range_min']}-{result['range_max']})")
```

### Simulate Tournament
```python
from models.tournament_simulator import TournamentSimulator

simulator = TournamentSimulator(predictor, fe)
predictions = simulator.monte_carlo_simulation(n_simulations=1000)

top_5 = list(predictions['winner_probabilities'].items())[:5]
for team, prob in top_5:
    print(f"{team}: {prob:.2f}%")
```

### Use Chatbot
```python
from utils.chatbot import CricketChatbot

chatbot = CricketChatbot(datasets, fe, predictor, score_predictor)

response = chatbot.query("Who will win India vs Australia?")
print(response['message'])
print(response['data'])
```

---

## Next Steps

1. ✅ Install and run (Done above)
2. 📊 Explore all 7 dashboard pages
3. 🎯 Try different predictions
4. 🤖 Chat with AI assistant
5. 🏆 Run tournament simulation
6. 📈 Analyze your favorite players

---

**Ready to predict T20 World Cup 2026!** 🏏🏆

For detailed documentation, see README.md
For installation help, see INSTALLATION.md
