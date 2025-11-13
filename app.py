"""
T20 World Cup 2026 Analytics & Prediction System
Main Streamlit Application
"""
import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.data_loader import DataLoader
from utils.feature_engineering import FeatureEngineer
from models.match_predictor import MatchPredictor
from models.score_predictor import ScorePredictor
from models.tournament_simulator import TournamentSimulator
from utils.chatbot import CricketChatbot

# Page config
st.set_page_config(
    page_title="T20 WC 2026 Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
@st.cache_resource
def load_data_and_models():
    """Load data and initialize models"""
    with st.spinner("Loading datasets and models..."):
        # Load data
        loader = DataLoader('data')
        datasets = loader.load_all_data()
        
        # Feature engineering
        fe = FeatureEngineer(datasets)
        
        # Initialize predictors
        match_predictor = MatchPredictor()
        score_predictor = ScorePredictor()
        
        # Try to load pre-trained models
        try:
            match_predictor.load_model('models/match_predictor.pkl')
        except:
            st.warning("Match predictor not trained yet. Training now...")
            X, y, _ = match_predictor.prepare_training_data(datasets, fe)
            match_predictor.train(X, y)
            match_predictor.save_model('models/match_predictor.pkl')
        
        try:
            score_predictor.load_model('models/score_predictor.pkl')
        except:
            st.warning("Score predictor not trained yet. Training now...")
            X, y = score_predictor.prepare_training_data(datasets, fe)
            score_predictor.train(X, y)
            score_predictor.save_model('models/score_predictor.pkl')
        
        # Initialize chatbot
        chatbot = CricketChatbot(datasets, fe, match_predictor, score_predictor)
        
        # Initialize simulator
        simulator = TournamentSimulator(match_predictor, fe)
        
        return datasets, fe, match_predictor, score_predictor, chatbot, simulator

# Load everything
datasets, fe, match_predictor, score_predictor, chatbot, simulator = load_data_and_models()

# Sidebar navigation
st.sidebar.markdown("# 🏏 T20 WC 2026")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "👤 Player Explorer",
        "⚔️ Team Comparison", 
        "🎯 Match Predictor",
        "🌍 Venue Analytics",
        "🏆 Tournament Simulator",
        "🤖 AI Chatbot"
    ]
)

# Main content
if page == "🏠 Home":
    from pages import home
    home.show(datasets, fe)
    
elif page == "👤 Player Explorer":
    from pages import player_explorer
    player_explorer.show(datasets, fe)
    
elif page == "⚔️ Team Comparison":
    from pages import team_comparison
    team_comparison.show(datasets, fe, match_predictor)
    
elif page == "🎯 Match Predictor":
    from pages import match_predictor_page
    match_predictor_page.show(datasets, fe, match_predictor, score_predictor)
    
elif page == "🌍 Venue Analytics":
    from pages import venue_analytics
    venue_analytics.show(datasets, fe)
    
elif page == "🏆 Tournament Simulator":
    from pages import tournament_page
    tournament_page.show(datasets, fe, simulator)
    
elif page == "🤖 AI Chatbot":
    from pages import chatbot_page
    chatbot_page.show(chatbot)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
T20 World Cup 2026 Analytics & Prediction System

**Features:**
- Player Performance Analysis
- Team Strength Comparison
- ML-based Match Prediction
- Score Forecasting
- Tournament Simulation
- AI-powered Chatbot

**Data:**
- 385+ Active Players
- Historical Match Data
- ICC Rankings
- Venue Statistics

Built with ❤️ using Streamlit
""")
