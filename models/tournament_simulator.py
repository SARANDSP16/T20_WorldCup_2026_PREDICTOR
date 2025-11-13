"""
T20 World Cup Tournament Simulator with Monte Carlo
"""
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

class TournamentSimulator:
    """Simulate full T20 World Cup tournament"""
    
    def __init__(self, match_predictor, feature_engineer):
        self.match_predictor = match_predictor
        self.feature_engineer = feature_engineer
        
        # T20 WC 2026 teams (top 20)
        self.teams = [
            'India', 'Australia', 'England', 'New Zealand', 'South Africa',
            'West Indies', 'Pakistan', 'Sri Lanka', 'Bangladesh', 'Afghanistan',
            'Ireland', 'Zimbabwe', 'Netherlands', 'Scotland', 'Namibia',
            'UAE', 'Nepal', 'USA', 'Canada', 'Oman'
        ]
        
        # Group stage structure (4 groups of 5 teams)
        self.groups = {
            'Group A': ['India', 'Pakistan', 'Ireland', 'USA', 'Canada'],
            'Group B': ['Australia', 'England', 'Scotland', 'Oman', 'Namibia'],
            'Group C': ['South Africa', 'West Indies', 'Bangladesh', 'Nepal', 'UAE'],
            'Group D': ['New Zealand', 'Sri Lanka', 'Afghanistan', 'Zimbabwe', 'Netherlands']
        }
        
        # Venues
        self.venues = [
            'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
            'Ahmedabad', 'Hyderabad', 'Pune', 'Dharamshala', 'Mohali'
        ]
    
    def simulate_match(self, team1, team2, venue='Mumbai'):
        """Simulate a single match"""
        result = self.match_predictor.predict_match(
            team1, team2, venue, self.feature_engineer
        )
        
        # Use probability to determine winner
        if np.random.random() < result['team1_prob']:
            return team1, result['team1_prob']
        else:
            return team2, result['team2_prob']
    
    def simulate_group_stage(self):
        """Simulate group stage matches"""
        group_standings = {}
        
        for group_name, teams in self.groups.items():
            standings = defaultdict(lambda: {'wins': 0, 'matches': 0, 'nrr': 0})
            
            # Round-robin within group
            for i, team1 in enumerate(teams):
                for team2 in teams[i+1:]:
                    venue = np.random.choice(self.venues)
                    winner, prob = self.simulate_match(team1, team2, venue)
                    
                    standings[winner]['wins'] += 1
                    standings[team1]['matches'] += 1
                    standings[team2]['matches'] += 1
                    
                    # Simplified NRR
                    if winner == team1:
                        standings[team1]['nrr'] += prob * 0.5
                        standings[team2]['nrr'] -= prob * 0.5
                    else:
                        standings[team2]['nrr'] += prob * 0.5
                        standings[team1]['nrr'] -= prob * 0.5
            
            # Calculate points and sort
            for team in teams:
                standings[team]['points'] = standings[team]['wins'] * 2
            
            # Sort by points, then NRR
            sorted_teams = sorted(
                standings.items(),
                key=lambda x: (x[1]['points'], x[1]['nrr']),
                reverse=True
            )
            
            group_standings[group_name] = sorted_teams
        
        return group_standings
    
    def get_knockout_teams(self, group_standings):
        """Get top 8 teams for Super 8 / knockouts"""
        qualified = []
        
        for group_name, standings in group_standings.items():
            # Top 2 from each group
            qualified.extend([team for team, stats in standings[:2]])
        
        return qualified
    
    def simulate_knockout(self, teams):
        """Simulate knockout stage (quarterfinals, semis, final)"""
        np.random.shuffle(teams)
        
        # Quarterfinals (if 8 teams)
        if len(teams) == 8:
            qf_winners = []
            for i in range(0, 8, 2):
                winner, _ = self.simulate_match(teams[i], teams[i+1])
                qf_winners.append(winner)
            teams = qf_winners
        
        # Semifinals
        sf_winners = []
        for i in range(0, 4, 2):
            winner, _ = self.simulate_match(teams[i], teams[i+1])
            sf_winners.append(winner)
        
        # Final
        champion, prob = self.simulate_match(sf_winners[0], sf_winners[1])
        runner_up = sf_winners[1] if champion == sf_winners[0] else sf_winners[0]
        
        return {
            'champion': champion,
            'runner_up': runner_up,
            'semifinalists': sf_winners + [t for t in teams if t not in sf_winners][:2]
        }
    
    def run_simulation(self):
        """Run one complete tournament simulation"""
        # Group stage
        group_standings = self.simulate_group_stage()
        
        # Get qualified teams
        qualified = self.get_knockout_teams(group_standings)
        
        # Knockout stage
        results = self.simulate_knockout(qualified)
        results['qualified_teams'] = qualified
        results['group_standings'] = group_standings
        
        return results
    
    def monte_carlo_simulation(self, n_simulations=10000):
        """Run Monte Carlo simulation"""
        print(f"Running {n_simulations} tournament simulations...")
        
        champion_count = defaultdict(int)
        finalist_count = defaultdict(int)
        semifinal_count = defaultdict(int)
        qualification_count = defaultdict(int)
        
        for i in range(n_simulations):
            if (i + 1) % 1000 == 0:
                print(f"Completed {i + 1}/{n_simulations} simulations")
            
            result = self.run_simulation()
            
            champion_count[result['champion']] += 1
            finalist_count[result['runner_up']] += 1
            
            for team in result['semifinalists']:
                semifinal_count[team] += 1
            
            for team in result['qualified_teams']:
                qualification_count[team] += 1
        
        # Calculate probabilities
        predictions = {
            'winner_probabilities': {
                team: (count / n_simulations) * 100
                for team, count in sorted(
                    champion_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'finalist_probabilities': {
                team: (count / n_simulations) * 100
                for team, count in sorted(
                    finalist_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'semifinal_probabilities': {
                team: (count / n_simulations) * 100
                for team, count in sorted(
                    semifinal_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            'qualification_probabilities': {
                team: (count / n_simulations) * 100
                for team, count in sorted(
                    qualification_count.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            }
        }
        
        print("\n✓ Monte Carlo simulation complete!")
        
        return predictions
    
    def get_top_predictions(self, predictions, top_n=5):
        """Get top N predictions"""
        top_winners = list(predictions['winner_probabilities'].items())[:top_n]
        top_finalists = list(predictions['finalist_probabilities'].items())[:top_n]
        
        return {
            'most_likely_winner': top_winners[0] if top_winners else ('Unknown', 0),
            'top_5_winners': top_winners,
            'most_likely_finalists': top_finalists[:2],
            'top_5_finalists': top_finalists
        }


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from utils.data_loader import DataLoader
    from utils.feature_engineering import FeatureEngineer
    from match_predictor import MatchPredictor
    
    # Load data
    loader = DataLoader('../data')
    datasets = loader.load_all_data()
    
    # Feature engineering
    fe = FeatureEngineer(datasets)
    
    # Load match predictor
    predictor = MatchPredictor()
    # Note: Load pre-trained model or train first
    
    # Initialize simulator
    simulator = TournamentSimulator(predictor, fe)
    
    # Run simulation (smaller number for testing)
    predictions = simulator.monte_carlo_simulation(n_simulations=100)
    
    # Show top predictions
    top = simulator.get_top_predictions(predictions)
    print(f"\nMost Likely Winner: {top['most_likely_winner']}")
    print(f"\nTop 5 Contenders:")
    for team, prob in top['top_5_winners']:
        print(f"  {team}: {prob:.2f}%")
