"""
Feature Engineering for T20 Cricket Analytics
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    """Create features for ML models"""
    
    def __init__(self, datasets):
        self.datasets = datasets
        self.scalers = {}
        self.encoders = {}
        
    def create_player_strength_vector(self, player_name, role='All-rounder'):
        """Create a strength vector for a player"""
        career = self.datasets['player_career']
        player = career[career['player_full_name'] == player_name]
        
        if player.empty:
            return np.zeros(10)
        
        player = player.iloc[0]
        
        # Batting features
        bat_avg = player.get('batting_average', 0) or 0
        strike_rate = player.get('strike_rate', 0) or 0
        sixes = player.get('sixes', 0) or 0
        fifties = player.get('fifties', 0) or 0
        hundreds = player.get('hundreds', 0) or 0
        
        # Bowling features
        wickets = player.get('wickets', 0) or 0
        economy = player.get('economy', 0) or 0
        bowling_avg = player.get('bowling_average', 0) or 0
        five_wkt = player.get('five_wicket_hauls', 0) or 0
        
        # Fielding
        catches = player.get('catches', 0) or 0
        
        # Normalize features
        vector = np.array([
            min(bat_avg / 50, 1.0),  # Normalize to 0-1
            min(strike_rate / 200, 1.0),
            min(sixes / 100, 1.0),
            fifties / 10,
            hundreds / 5,
            min(wickets / 100, 1.0),
            max(0, 1 - (economy / 12)),  # Lower is better
            max(0, 1 - (bowling_avg / 30)),
            five_wkt / 5,
            min(catches / 50, 1.0)
        ])
        
        return vector
    
    def create_team_strength_vector(self, team_name):
        """Create team strength vector based on squad"""
        career = self.datasets['player_career']
        rankings = self.datasets['team_rankings']
        
        # Get team ranking
        team_rank = rankings[rankings['Team'] == team_name]
        if not team_rank.empty:
            rating = team_rank.iloc[0]['rating']
            rank_score = rating / 300  # Normalize
        else:
            rank_score = 0.5
        
        # Get squad
        squad = career[career['team'] == team_name]
        
        if squad.empty:
            return np.zeros(15)
        
        # Aggregate squad strengths
        total_bat_avg = squad['batting_average'].fillna(0).mean()
        total_strike_rate = squad['strike_rate'].fillna(0).mean()
        total_wickets = squad['wickets'].fillna(0).sum()
        avg_economy = squad['economy'].fillna(10).mean()
        total_catches = squad['catches'].fillna(0).sum()
        
        # Count role distribution
        batters = len(squad[squad['role'] == 'Batter'])
        bowlers = len(squad[squad['role'] == 'Bowler'])
        allrounders = len(squad[squad['role'] == 'All-rounder'])
        
        # Power hitters (SR > 140)
        power_hitters = len(squad[squad['strike_rate'] > 140])
        
        # Death bowlers (economy < 8)
        death_bowlers = len(squad[squad['economy'] < 8])
        
        vector = np.array([
            rank_score,
            min(total_bat_avg / 40, 1.0),
            min(total_strike_rate / 140, 1.0),
            min(total_wickets / 500, 1.0),
            max(0, 1 - (avg_economy / 10)),
            min(total_catches / 200, 1.0),
            batters / 15,
            bowlers / 15,
            allrounders / 15,
            power_hitters / 15,
            death_bowlers / 15,
            len(squad) / 15,  # Squad depth
            rank_score,  # Duplicate for importance
            rank_score,
            rank_score
        ])
        
        return vector
    
    def create_venue_features(self, venue_name):
        """Create venue characteristic features"""
        vs_venue = self.datasets['player_vs_venue']
        venue_data = vs_venue[vs_venue['venue'] == venue_name]
        
        if venue_data.empty:
            return np.array([0.5, 0.5, 150, 7.5, 0.5])
        
        # Average stats at venue
        avg_strike_rate = venue_data['strike_rate'].fillna(130).mean()
        avg_economy = venue_data['economy'].fillna(8).mean()
        avg_runs = venue_data['runs'].fillna(25).mean()
        avg_wickets = venue_data['wickets'].fillna(1).mean()
        
        # Estimate average score (rough approximation)
        total_runs = venue_data['runs'].fillna(0).sum()
        total_matches = venue_data['matches_x'].fillna(1).sum()
        avg_score = (total_runs / max(total_matches, 1)) * 20  # Extrapolate to 20 overs
        
        # Spin vs pace favorability
        # Higher economy for bowlers suggests batting-friendly
        batting_friendly = min(avg_economy / 10, 1.0)
        
        # Pace favorability (if SR high and economy high)
        pace_friendly = min(avg_strike_rate / 150, 1.0)
        
        vector = np.array([
            batting_friendly,
            pace_friendly,
            min(avg_score / 200, 1.0) if avg_score > 0 else 0.75,
            avg_economy / 12,
            min(avg_wickets / 3, 1.0)
        ])
        
        return vector
    
    def calculate_form_score(self, team_name, n_matches=5):
        """Calculate recent form score for a team"""
        form = self.datasets['team_form']
        team_form = form[form['team'] == team_name].sort_values(
            'match_id', ascending=False
        ).head(n_matches)
        
        if team_form.empty:
            return 0.5
        
        # Calculate win ratio
        wins = team_form['won'].sum()
        total = len(team_form)
        win_ratio = wins / total if total > 0 else 0.5
        
        # Recent performance
        recent_runs = team_form['form_runs'].fillna(0).mean()
        recent_wickets = team_form['form_wickets'].fillna(0).mean()
        
        # Normalize
        form_score = (
            0.6 * win_ratio +
            0.2 * min(recent_runs / 150, 1.0) +
            0.2 * min(recent_wickets / 5, 1.0)
        )
        
        return form_score
    
    def calculate_player_form_score(self, player_name, n_matches=5):
        """Calculate recent form score for a player"""
        form = self.datasets['player_form']
        player_form = form[form['player_name'] == player_name].sort_values(
            'date', ascending=False
        ).head(n_matches)
        
        if player_form.empty:
            return 0.5
        
        # Batting form
        avg_runs = player_form['runs'].fillna(0).mean()
        avg_sr = player_form['strike_rate'].fillna(100).mean()
        
        # Bowling form
        avg_wickets = player_form['wickets'].fillna(0).mean()
        avg_economy = player_form['economy'].fillna(8).mean()
        
        # Combined score
        bat_score = (avg_runs / 50) * 0.5 + (avg_sr / 150) * 0.5
        bowl_score = (avg_wickets / 3) * 0.5 + max(0, 1 - avg_economy / 10) * 0.5
        
        form_score = min((bat_score + bowl_score) / 2, 1.0)
        
        return form_score
    
    def get_h2h_win_rate(self, team1, team2):
        """Get head-to-head win rate"""
        matches = self.datasets['match_summary']
        
        h2h = matches[
            ((matches['team1'] == team1) & (matches['team2'] == team2)) |
            ((matches['team1'] == team2) & (matches['team2'] == team1))
        ]
        
        if h2h.empty:
            return 0.5
        
        team1_wins = len(h2h[h2h['winner'] == team1])
        total = len(h2h)
        
        return team1_wins / total if total > 0 else 0.5
    
    def create_match_features(self, team1, team2, venue, toss_winner=None, batting_first=None):
        """Create complete feature vector for match prediction"""
        
        # Team strengths
        team1_strength = self.create_team_strength_vector(team1)
        team2_strength = self.create_team_strength_vector(team2)
        
        # Venue features
        venue_features = self.create_venue_features(venue)
        
        # Form scores
        team1_form = self.calculate_form_score(team1)
        team2_form = self.calculate_form_score(team2)
        
        # H2H
        h2h = self.get_h2h_win_rate(team1, team2)
        
        # Toss impact (if available)
        toss_impact = 0
        if toss_winner and batting_first is not None:
            if toss_winner == team1:
                toss_impact = 0.05 if batting_first else -0.05
            else:
                toss_impact = -0.05 if batting_first else 0.05
        
        # Combine all features
        features = np.concatenate([
            team1_strength,
            team2_strength,
            venue_features,
            [team1_form, team2_form, h2h, toss_impact]
        ])
        
        return features


if __name__ == "__main__":
    from data_loader import DataLoader
    
    # Test feature engineering
    loader = DataLoader()
    datasets = loader.load_all_data()
    
    fe = FeatureEngineer(datasets)
    
    # Test team strength
    india_strength = fe.create_team_strength_vector('India')
    print(f"India strength vector: {india_strength}")
    print(f"India form score: {fe.calculate_form_score('India')}")
