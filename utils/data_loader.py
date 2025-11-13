"""
Data Loading and Preprocessing Utilities
"""
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class DataLoader:
    """Load and preprocess all cricket datasets"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.datasets = {}
        
    def load_all_data(self):
        """Load all CSV files"""
        print("Loading datasets...")
        
        # Player data
        self.datasets['player_career'] = pd.read_csv(
            self.data_dir / 'table1_player_career.csv'
        )
        
        # Match ball-by-ball data
        self.datasets['match_by_match'] = pd.read_csv(
            self.data_dir / 'table2_match_by_match.csv'
        )
        
        # Player vs opponent
        self.datasets['player_vs_opponent'] = pd.read_csv(
            self.data_dir / 'table3_player_vs_opponent.csv'
        )
        
        # Player vs venue
        self.datasets['player_vs_venue'] = pd.read_csv(
            self.data_dir / 'table4_player_vs_venue.csv'
        )
        
        # Match summary
        self.datasets['match_summary'] = pd.read_csv(
            self.data_dir / 'table5_match_summary.csv'
        )
        
        # Over and partnership
        self.datasets['over_partnership'] = pd.read_csv(
            self.data_dir / 'table6_over_and_partnership.csv'
        )
        
        # Player form
        self.datasets['player_form'] = pd.read_csv(
            self.data_dir / 'table7_player_form.csv'
        )
        
        # Team form
        self.datasets['team_form'] = pd.read_csv(
            self.data_dir / 'table8_team_form.csv'
        )
        
        # ICC Rankings
        self.datasets['team_rankings'] = pd.read_csv(
            self.data_dir / 'icc_mens_t20i_team_rankings_2025.csv'
        )
        
        self.datasets['batting_rankings'] = pd.read_csv(
            self.data_dir / 'mens_t20i_batting_rankings_2025.csv'
        )
        
        self.datasets['bowling_rankings'] = pd.read_csv(
            self.data_dir / 'mens_t20i_bowling_rankings_2025.csv'
        )
        
        self.datasets['allrounder_rankings'] = pd.read_csv(
            self.data_dir / 'mens_t20i_allrounder_rankings_2025.csv'
        )
        
        # T20 WC data
        try:
            self.datasets['wc_data'] = pd.read_excel(
                self.data_dir / 'T20 worldcup overall.xlsx'
            )
        except:
            self.datasets['wc_data'] = None
            
        print(f"✓ Loaded {len(self.datasets)} datasets")
        return self.datasets
    
    def get_dataset(self, name):
        """Get a specific dataset"""
        return self.datasets.get(name)
    
    def get_player_data(self, player_name):
        """Get all data for a specific player"""
        player_data = {}
        
        # Career stats
        career = self.datasets['player_career']
        player_data['career'] = career[
            career['player_full_name'].str.contains(player_name, case=False, na=False)
        ]
        
        # vs Opponent
        vs_opp = self.datasets['player_vs_opponent']
        player_data['vs_opponent'] = vs_opp[
            vs_opp['player_name'].str.contains(player_name, case=False, na=False)
        ]
        
        # vs Venue
        vs_venue = self.datasets['player_vs_venue']
        player_data['vs_venue'] = vs_venue[
            vs_venue['player_name'].str.contains(player_name, case=False, na=False)
        ]
        
        # Recent form
        form = self.datasets['player_form']
        player_data['form'] = form[
            form['player_name'].str.contains(player_name, case=False, na=False)
        ].sort_values('date', ascending=False).head(10)
        
        return player_data
    
    def get_team_data(self, team_name):
        """Get all data for a specific team"""
        team_data = {}
        
        # Team ranking
        rankings = self.datasets['team_rankings']
        team_data['ranking'] = rankings[
            rankings['Team'].str.contains(team_name, case=False, na=False)
        ]
        
        # Team players
        career = self.datasets['player_career']
        team_data['squad'] = career[
            career['team'].str.contains(team_name, case=False, na=False)
        ]
        
        # Team form
        form = self.datasets['team_form']
        team_data['form'] = form[
            form['team'].str.contains(team_name, case=False, na=False)
        ].sort_values('match_id', ascending=False).head(10)
        
        return team_data
    
    def get_venue_data(self, venue_name):
        """Get all data for a specific venue"""
        vs_venue = self.datasets['player_vs_venue']
        venue_data = vs_venue[
            vs_venue['venue'].str.contains(venue_name, case=False, na=False)
        ]
        
        # Get match summary for venue
        matches = self.datasets['match_summary']
        venue_matches = matches[
            matches['venue'].str.contains(venue_name, case=False, na=False)
        ]
        
        return {
            'player_stats': venue_data,
            'matches': venue_matches
        }
    
    def get_head_to_head(self, team1, team2):
        """Get head-to-head stats between two teams"""
        matches = self.datasets['match_summary']
        
        h2h = matches[
            ((matches['team1'] == team1) & (matches['team2'] == team2)) |
            ((matches['team1'] == team2) & (matches['team2'] == team1))
        ]
        
        return h2h
    
    def get_match_data(self, match_id):
        """Get detailed data for a specific match"""
        ball_by_ball = self.datasets['match_by_match']
        match_data = ball_by_ball[ball_by_ball['match_id'] == match_id]
        
        return match_data


if __name__ == "__main__":
    # Test data loader
    loader = DataLoader()
    datasets = loader.load_all_data()
    
    print("\nDataset shapes:")
    for name, df in datasets.items():
        if df is not None:
            print(f"{name}: {df.shape}")
