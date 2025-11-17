Installation Guide

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for initial setup)

## Step-by-Step Installation

### 1. Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd webapp

# Or download and extract the ZIP file
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This will install:
# - pandas, numpy, scipy (data processing)
# - scikit-learn, xgboost, lightgbm (ML)
# - streamlit (dashboard)
# - plotly, matplotlib, seaborn (visualization)
# - And other dependencies
```

### 4. Verify Data Files

Ensure all data files are in the `data/` directory:

```bash
ls -lh data/

# You should see:
# - table1_player_career.csv
# - table2_match_by_match.csv
# - table3_player_vs_opponent.csv
# - table4_player_vs_venue.csv
# - table5_match_summary.csv
# - table6_over_and_partnership.csv
# - table7_player_form.csv
# - table8_team_form.csv
# - icc_mens_t20i_team_rankings_2025.csv
# - mens_t20i_batting_rankings_2025.csv
# - mens_t20i_bowling_rankings_2025.csv
# - mens_t20i_allrounder_rankings_2025.csv
# - T20 worldcup overall.xlsx
```

### 5. Train ML Models

```bash
# Train both match and score prediction models
python train_models.py

# This will:
# 1. Load all datasets
# 2. Prepare training data
# 3. Train match predictor
# 4. Train score predictor
# 5. Save models to models/ directory
# 6. Run test predictions

# Expected output:
# ✓ Loaded 12 datasets
# Training match predictor...
# Random Forest: 0.7234
# XGBoost: 0.7456
# Gradient Boosting: 0.7312
# ✓ Best model: XGBoost (Accuracy: 0.7456)
# Training score predictor...
# MAE: 16.45 runs
# ✓ All models trained successfully!
```

### 6. Run the Dashboard

#### Option A: Using the run script (Recommended)

```bash
./run.sh
```

#### Option B: Using Streamlit directly

```bash
streamlit run app.py
```

#### Option C: With custom port

```bash
streamlit run app.py --server.port 8080
```

### 7. Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:8501
```

Or if you used a custom port:
```
http://localhost:8080
```

## Troubleshooting

### Issue: Module not found errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Memory errors during model training

```bash
# Reduce data size or use a machine with more RAM
# Edit train_models.py to use smaller datasets
```

### Issue: Port already in use

```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run app.py --server.port 8502
```

### Issue: Models not loading

```bash
# Retrain models
rm -rf models/*.pkl
python train_models.py
```

### Issue: Slow dashboard loading

```bash
# First load is slower due to model initialization
# Subsequent navigation should be fast
# Consider caching (@st.cache_resource is already used)
```

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] All 13 data files present in data/ directory
- [ ] Models trained (match_predictor.pkl and score_predictor.pkl in models/)
- [ ] Dashboard launches without errors
- [ ] Can access dashboard at http://localhost:8501
- [ ] All 7 pages load correctly
- [ ] Predictions work
- [ ] Chatbot responds

## Next Steps

1. Explore the **Home** page for overview
2. Try the **Player Explorer** to analyze players
3. Use **Match Predictor** for predictions
4. Run **Tournament Simulator** (start with 100 simulations)
5. Chat with the **AI Assistant**

## Performance Tips

1. **First Load**: May take 30-60 seconds to load data and models
2. **Caching**: Data and models are cached for faster subsequent loads
3. **Simulations**: Start with 100-1000 simulations, increase if needed
4. **Browser**: Use Chrome or Firefox for best experience

## Updating Data

To update with new data:

1. Replace CSV files in `data/` directory
2. Retrain models:
   ```bash
   python train_models.py
   ```
3. Restart dashboard:
   ```bash
   streamlit run app.py
   ```

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review README.md for usage instructions
3. Verify all files are present
4. Check Python version: `python --version`
5. Check installed packages: `pip list`

## System Architecture

```
User Browser (http://localhost:8501)
    ↓
Streamlit Dashboard (app.py)
    ↓
├── Pages (pages/*.py)
├── ML Models (models/*.py)
├── Utilities (utils/*.py)
└── Data (data/*.csv)
```

---

**Ready to explore T20 World Cup 2026 analytics!** 🏏
