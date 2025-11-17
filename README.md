# 🏏 T20 World Cup 2026 Analytics & Prediction System

A comprehensive end-to-end analytics and prediction platform for T20 World Cup 2026, featuring advanced ML models, interactive dashboards, and an AI-powered chatbot.

## 🎯 Features

### 1. Interactive Dashboard (Streamlit)
- **Home Page**: Overview with key statistics and rankings
- **Player Explorer**: Detailed player analysis with performance metrics
- **Team Comparison**: Head-to-head team comparisons with strength analysis
- **Match Predictor**: AI-powered match outcome and score predictions
- **Venue Analytics**: Venue-specific performance insights
- **Tournament Simulator**: Monte Carlo simulation for World Cup predictions
- **AI Chatbot**: Natural language query interface

### 2. Machine Learning Models
- **Match Outcome Predictor**: XGBoost/Random Forest for win probability
- **Score Predictor**: Regression models for score forecasting
- **Player Performance Model**: Form-based player predictions
- **Tournament Simulator**: Monte Carlo simulation with 10,000+ iterations

### 3. AI Chatbot
- Natural language understanding
- Player queries and comparisons
- Match predictions
- Team and venue analytics
- Statistical insights

### 4. Data Engineering Pipeline
- Automated data loading and preprocessing
- Feature engineering for 385+ players
- Team strength vectors
- Venue difficulty scores
- Player form tracking

## 📊 Datasets

### Available Data
- `table1_player_career.csv` - Career stats for 385 active players
- `table2_match_by_match.csv` - Ball-by-ball match data
- `table3_player_vs_opponent.csv` - Player vs opponent stats
- `table4_player_vs_venue.csv` - Player performance at venues
- `table5_match_summary.csv` - Match summaries
- `table6_over_and_partnership.csv` - Over-by-over data
- `table7_player_form.csv` - Recent player form
- `table8_team_form.csv` - Team form and trends
- ICC Rankings (Team, Batting, Bowling, All-rounder)
- T20 World Cup historical data

### Data Coverage
- **Players**: 385+ active players
- **Teams**: 20 teams
- **Matches**: Thousands of historical T20 matches
- **Time Period**: 2016-2025

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd webapp
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Train ML models** (first time only)
```bash
python train_models.py
```

4. **Run the dashboard**
```bash
streamlit run app.py
```

5. **Access the application**
Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
webapp/
├── data/                           # All CSV and data files
│   ├── table1_player_career.csv
│   ├── table2_match_by_match.csv
│   ├── ...
│   └── icc_mens_t20i_team_rankings_2025.csv
├── models/                         # ML models
│   ├── match_predictor.py         # Match outcome prediction
│   ├── score_predictor.py         # Score prediction
│   ├── tournament_simulator.py    # Tournament simulation
│   ├── match_predictor.pkl        # Trained model (generated)
│   └── score_predictor.pkl        # Trained model (generated)
├── utils/                          # Utility modules
│   ├── data_loader.py             # Data loading utilities
│   ├── feature_engineering.py     # Feature creation
│   └── chatbot.py                 # AI chatbot engine
├── pages/                          # Streamlit pages
│   ├── home.py                    # Home dashboard
│   ├── player_explorer.py         # Player analysis
│   ├── team_comparison.py         # Team comparison
│   ├── match_predictor_page.py    # Match predictions
│   ├── venue_analytics.py         # Venue analysis
│   ├── tournament_page.py         # Tournament simulator
│   └── chatbot_page.py            # Chatbot interface
├── app.py                          # Main Streamlit app
├── train_models.py                 # Model training script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🎮 Usage Guide

### 1. Player Explorer
- Search for any player by name
- View comprehensive statistics
- Analyze performance vs opponents
- Check venue-specific performance
- Track recent form

### 2. Team Comparison
- Select two teams to compare
- View ICC rankings and ratings
- Compare squad strengths
- Analyze head-to-head records
- Visualize team strength vectors

### 3. Match Predictor
- Select two teams and a venue
- Configure toss and batting order (optional)
- Get AI-powered win probability
- View predicted scores for both teams
- See phase-wise score breakdown

### 4. Venue Analytics
- Select a venue
- View batting and bowling statistics
- Identify top performers at the venue
- Understand venue characteristics

### 5. Tournament Simulator
- Run Monte Carlo simulations (100-10,000 iterations)
- View championship probabilities
- Analyze semi-final qualification chances
- Identify favorites and dark horses

### 6. AI Chatbot
- Ask questions in natural language
- Get player statistics
- Compare players and teams
- Request match predictions
- Query tournament information

## 🤖 Example Chatbot Queries

```
"Predict India vs Australia at Wankhede"
"Compare Virat Kohli and Babar Azam"
"Show me top batters"
"What's the squad for England?"
"Who will win India vs Pakistan?"
"Predict score for South Africa vs New Zealand"
"Best bowlers in the tournament"
"Show performance of Rohit Sharma vs Pakistan"
```

## 📈 Model Performance

### Match Predictor
- **Algorithm**: XGBoost / Random Forest
- **Accuracy**: ~70-75%
- **Features**: 38 features including team strength, form, venue, H2H

### Score Predictor
- **Algorithm**: Gradient Boosting Regressor
- **MAE**: ~15-20 runs
- **R² Score**: ~0.65-0.75
- **Features**: Team batting/bowling strength, venue, opponent

### Tournament Simulator
- **Method**: Monte Carlo simulation
- **Iterations**: 10,000 (configurable)
- **Output**: Win probabilities for all teams

## 🛠️ Technical Stack

- **Backend**: Python 3.8+
- **ML Libraries**: scikit-learn, XGBoost, LightGBM
- **Dashboard**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Data**: Pandas, NumPy
- **NLP**: Basic rule-based entity extraction

## 🔧 Configuration

### Model Parameters
Edit model hyperparameters in:
- `models/match_predictor.py`
- `models/score_predictor.py`

### Tournament Groups
Edit tournament structure in:
- `models/tournament_simulator.py`

### Features
Add new features in:
- `utils/feature_engineering.py`

## 📊 Data Updates

To update with new data:
1. Replace CSV files in `data/` directory
2. Retrain models: `python train_models.py`
3. Restart the dashboard

## 🎯 Future Enhancements

- [ ] Player image integration
- [ ] Real-time data updates
- [ ] Advanced NLP with LLMs
- [ ] Deep learning models
- [ ] Mobile app version
- [ ] API endpoints
- [ ] Database integration
- [ ] User authentication

## 📝 Notes

- **Data Quality**: Models depend on historical data quality
- **Predictions**: AI predictions are probabilistic, not guarantees
- **Updates**: Retrain models regularly with new data
- **Performance**: First load may be slow due to model initialization

## 👥 Credits

Built with ❤️ for T20 World Cup 2026 analytics


