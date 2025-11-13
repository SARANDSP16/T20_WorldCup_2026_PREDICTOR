"""
AI Cricket Chatbot with Natural Language Query
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CricketChatbot:
    """AI Assistant for cricket queries"""
    
    def __init__(self, datasets, feature_engineer, match_predictor, score_predictor):
        self.datasets = datasets
        self.fe = feature_engineer
        self.match_predictor = match_predictor
        self.score_predictor = score_predictor
        
        # Get all teams and players
        self.teams = datasets['team_rankings']['Team'].tolist()
        self.players = datasets['player_career']['player_full_name'].tolist()
        self.venues = datasets['player_vs_venue']['venue'].unique().tolist()
    
    def extract_entities(self, query):
        """Extract teams, players, venues from query"""
        query_lower = query.lower()
        
        entities = {
            'teams': [],
            'players': [],
            'venues': [],
            'intent': None
        }
        
        # Extract teams
        for team in self.teams:
            if team.lower() in query_lower:
                entities['teams'].append(team)
        
        # Extract players (check partial matches)
        for player in self.players:
            player_parts = player.lower().split()
            for part in player_parts:
                if len(part) > 3 and part in query_lower:
                    entities['players'].append(player)
                    break
        
        # Extract venues (partial match)
        for venue in self.venues:
            if venue and len(venue) > 5:
                venue_lower = venue.lower()
                if venue_lower in query_lower or any(
                    word in query_lower for word in venue_lower.split()[:3]
                ):
                    entities['venues'].append(venue)
        
        # Detect intent
        if any(word in query_lower for word in ['predict', 'who will win', 'winner', 'forecast']):
            entities['intent'] = 'predict_match'
        elif any(word in query_lower for word in ['score', 'runs', 'total']):
            entities['intent'] = 'predict_score'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            entities['intent'] = 'compare'
        elif any(word in query_lower for word in ['performance', 'stats', 'record']):
            entities['intent'] = 'player_stats'
        elif any(word in query_lower for word in ['squad', 'team', 'players', 'lineup']):
            entities['intent'] = 'team_info'
        elif any(word in query_lower for word in ['venue', 'ground', 'stadium']):
            entities['intent'] = 'venue_info'
        elif any(word in query_lower for word in ['best', 'top', 'highest']):
            entities['intent'] = 'best_performers'
        elif any(word in query_lower for word in ['world cup', 'tournament', 'champion']):
            entities['intent'] = 'tournament'
        else:
            entities['intent'] = 'general'
        
        return entities
    
    def query(self, user_query):
        """Process natural language query"""
        entities = self.extract_entities(user_query)
        intent = entities['intent']
        
        try:
            if intent == 'predict_match':
                return self.handle_match_prediction(entities, user_query)
            elif intent == 'predict_score':
                return self.handle_score_prediction(entities, user_query)
            elif intent == 'compare':
                return self.handle_comparison(entities, user_query)
            elif intent == 'player_stats':
                return self.handle_player_stats(entities, user_query)
            elif intent == 'team_info':
                return self.handle_team_info(entities, user_query)
            elif intent == 'venue_info':
                return self.handle_venue_info(entities, user_query)
            elif intent == 'best_performers':
                return self.handle_best_performers(entities, user_query)
            elif intent == 'tournament':
                return self.handle_tournament_query(entities, user_query)
            else:
                return self.handle_general_query(entities, user_query)
        except Exception as e:
            return {
                'success': False,
                'message': f"Sorry, I encountered an error: {str(e)}",
                'data': None
            }
    
    def handle_match_prediction(self, entities, query):
        """Handle match prediction queries"""
        teams = entities['teams']
        venues = entities['venues']
        
        if len(teams) < 2:
            return {
                'success': False,
                'message': "Please specify two teams for match prediction.",
                'suggestion': "Example: 'Predict India vs Australia at Wankhede'"
            }
        
        team1, team2 = teams[0], teams[1]
        venue = venues[0] if venues else 'Mumbai'
        
        result = self.match_predictor.predict_match(
            team1, team2, venue, self.fe
        )
        
        return {
            'success': True,
            'message': f"Match Prediction: {team1} vs {team2} at {venue}",
            'data': {
                'winner': result['winner'],
                'probability': f"{result['probability']:.1%}",
                'team1': team1,
                'team1_prob': f"{result['team1_prob']:.1%}",
                'team2': team2,
                'team2_prob': f"{result['team2_prob']:.1%}",
                'confidence': result['confidence'],
                'venue': venue
            },
            'visualization': 'bar_chart'
        }
    
    def handle_score_prediction(self, entities, query):
        """Handle score prediction queries"""
        teams = entities['teams']
        venues = entities['venues']
        
        if len(teams) < 1:
            return {
                'success': False,
                'message': "Please specify a team for score prediction."
            }
        
        team = teams[0]
        opponent = teams[1] if len(teams) > 1 else 'India'
        venue = venues[0] if venues else 'Mumbai'
        
        result = self.score_predictor.predict_score(
            team, opponent, venue, self.fe
        )
        
        return {
            'success': True,
            'message': f"Score Prediction: {team} vs {opponent} at {venue}",
            'data': {
                'predicted_score': result['predicted_score'],
                'range': f"{result['range_min']} - {result['range_max']}",
                'powerplay': result['powerplay_score'],
                'middle_overs': result['middle_overs_score'],
                'death_overs': result['death_overs_score'],
                'confidence': result['confidence']
            },
            'visualization': 'gauge_chart'
        }
    
    def handle_comparison(self, entities, query):
        """Handle player/team comparison queries"""
        if len(entities['players']) >= 2:
            return self._compare_players(entities['players'][:2])
        elif len(entities['teams']) >= 2:
            return self._compare_teams(entities['teams'][:2])
        else:
            return {
                'success': False,
                'message': "Please specify two players or teams to compare."
            }
    
    def _compare_players(self, players):
        """Compare two players"""
        career = self.datasets['player_career']
        
        player_data = []
        for player_name in players:
            player = career[career['player_full_name'] == player_name]
            if not player.empty:
                player_data.append(player.iloc[0])
        
        if len(player_data) < 2:
            return {
                'success': False,
                'message': f"Could not find data for players: {players}"
            }
        
        comparison = {
            'player1': {
                'name': players[0],
                'batting_avg': player_data[0].get('batting_average', 0),
                'strike_rate': player_data[0].get('strike_rate', 0),
                'wickets': player_data[0].get('wickets', 0),
                'economy': player_data[0].get('economy', 0),
                'matches': player_data[0].get('matches_played', 0)
            },
            'player2': {
                'name': players[1],
                'batting_avg': player_data[1].get('batting_average', 0),
                'strike_rate': player_data[1].get('strike_rate', 0),
                'wickets': player_data[1].get('wickets', 0),
                'economy': player_data[1].get('economy', 0),
                'matches': player_data[1].get('matches_played', 0)
            }
        }
        
        return {
            'success': True,
            'message': f"Comparison: {players[0]} vs {players[1]}",
            'data': comparison,
            'visualization': 'radar_chart'
        }
    
    def _compare_teams(self, teams):
        """Compare two teams"""
        h2h = self.fe.get_h2h_win_rate(teams[0], teams[1])
        
        team1_strength = self.fe.create_team_strength_vector(teams[0])
        team2_strength = self.fe.create_team_strength_vector(teams[1])
        
        return {
            'success': True,
            'message': f"Team Comparison: {teams[0]} vs {teams[1]}",
            'data': {
                'team1': teams[0],
                'team2': teams[1],
                'h2h_win_rate': f"{h2h:.1%}",
                'team1_strength': float(np.mean(team1_strength)),
                'team2_strength': float(np.mean(team2_strength))
            },
            'visualization': 'comparison_bar'
        }
    
    def handle_player_stats(self, entities, query):
        """Handle player statistics queries"""
        if not entities['players']:
            return {
                'success': False,
                'message': "Please specify a player name."
            }
        
        player = entities['players'][0]
        career = self.datasets['player_career']
        player_data = career[career['player_full_name'] == player]
        
        if player_data.empty:
            return {
                'success': False,
                'message': f"Could not find data for {player}"
            }
        
        player_row = player_data.iloc[0]
        
        return {
            'success': True,
            'message': f"Career Statistics: {player}",
            'data': {
                'name': player,
                'team': player_row.get('team', 'Unknown'),
                'role': player_row.get('role', 'Unknown'),
                'matches': player_row.get('matches_played', 0),
                'runs': player_row.get('runs', 0),
                'batting_avg': player_row.get('batting_average', 0),
                'strike_rate': player_row.get('strike_rate', 0),
                'fifties': player_row.get('fifties', 0),
                'hundreds': player_row.get('hundreds', 0),
                'wickets': player_row.get('wickets', 0),
                'economy': player_row.get('economy', 0),
                'catches': player_row.get('catches', 0)
            },
            'visualization': 'stat_card'
        }
    
    def handle_team_info(self, entities, query):
        """Handle team information queries"""
        if not entities['teams']:
            return {
                'success': False,
                'message': "Please specify a team name."
            }
        
        team = entities['teams'][0]
        career = self.datasets['player_career']
        rankings = self.datasets['team_rankings']
        
        squad = career[career['team'] == team]
        team_rank = rankings[rankings['Team'] == team]
        
        return {
            'success': True,
            'message': f"Team Information: {team}",
            'data': {
                'team': team,
                'ranking': team_rank.iloc[0]['pos'] if not team_rank.empty else 'N/A',
                'rating': team_rank.iloc[0]['rating'] if not team_rank.empty else 'N/A',
                'squad_size': len(squad),
                'top_batters': squad.nlargest(3, 'runs')['player_full_name'].tolist(),
                'top_bowlers': squad.nlargest(3, 'wickets')['player_full_name'].tolist()
            },
            'visualization': 'team_overview'
        }
    
    def handle_venue_info(self, entities, query):
        """Handle venue information queries"""
        if not entities['venues']:
            return {
                'success': False,
                'message': "Please specify a venue name."
            }
        
        venue = entities['venues'][0]
        vs_venue = self.datasets['player_vs_venue']
        venue_data = vs_venue[vs_venue['venue'] == venue]
        
        if venue_data.empty:
            return {
                'success': False,
                'message': f"No data available for {venue}"
            }
        
        avg_sr = venue_data['strike_rate'].fillna(0).mean()
        avg_economy = venue_data['economy'].fillna(0).mean()
        
        return {
            'success': True,
            'message': f"Venue Analysis: {venue}",
            'data': {
                'venue': venue,
                'avg_strike_rate': f"{avg_sr:.2f}",
                'avg_economy': f"{avg_economy:.2f}",
                'batting_friendly': 'Yes' if avg_sr > 130 else 'No',
                'matches_played': len(venue_data['matches_x'].unique())
            },
            'visualization': 'venue_stats'
        }
    
    def handle_best_performers(self, entities, query):
        """Handle best performers queries"""
        career = self.datasets['player_career']
        
        query_lower = query.lower()
        
        if 'batter' in query_lower or 'batting' in query_lower:
            top = career.nlargest(5, 'runs')[['player_full_name', 'team', 'runs', 'strike_rate']]
            category = 'Top Batters'
        elif 'bowler' in query_lower or 'bowling' in query_lower:
            top = career.nlargest(5, 'wickets')[['player_full_name', 'team', 'wickets', 'economy']]
            category = 'Top Bowlers'
        else:
            top = career.nlargest(5, 'runs')[['player_full_name', 'team', 'runs']]
            category = 'Top Performers'
        
        return {
            'success': True,
            'message': category,
            'data': top.to_dict('records'),
            'visualization': 'leaderboard'
        }
    
    def handle_tournament_query(self, entities, query):
        """Handle World Cup tournament queries"""
        return {
            'success': True,
            'message': "T20 World Cup 2026 will be held in India and Sri Lanka. Use the Tournament Simulator page for predictions!",
            'data': {
                'host': 'India & Sri Lanka',
                'year': 2026,
                'teams': 20,
                'favorites': ['India', 'Australia', 'England', 'South Africa']
            },
            'visualization': 'info_card'
        }
    
    def handle_general_query(self, entities, query):
        """Handle general queries"""
        return {
            'success': True,
            'message': "I can help you with player stats, match predictions, team comparisons, and more. Try asking specific questions!",
            'suggestions': [
                "Predict India vs Australia at Wankhede",
                "Compare Virat Kohli and Babar Azam",
                "Show me top batters",
                "What's the squad for England?",
                "Predict score for Pakistan vs South Africa"
            ]
        }


if __name__ == "__main__":
    # Test chatbot
    import sys
    sys.path.append('..')
    from data_loader import DataLoader
    from feature_engineering import FeatureEngineer
    
    loader = DataLoader('../data')
    datasets = loader.load_all_data()
    fe = FeatureEngineer(datasets)
    
    # Mock predictors
    class MockPredictor:
        def predict_match(self, *args, **kwargs):
            return {
                'winner': 'India',
                'probability': 0.65,
                'team1_prob': 0.65,
                'team2_prob': 0.35,
                'confidence': 'Medium'
            }
        
        def predict_score(self, *args, **kwargs):
            return {
                'predicted_score': 165,
                'range_min': 150,
                'range_max': 180,
                'confidence': 'High',
                'powerplay_score': 50,
                'middle_overs_score': 65,
                'death_overs_score': 50
            }
    
    chatbot = CricketChatbot(datasets, fe, MockPredictor(), MockPredictor())
    
    # Test queries
    queries = [
        "Predict India vs Australia at Wankhede",
        "Show me top batters",
        "Compare teams India and Pakistan"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        response = chatbot.query(q)
        print(f"Response: {response['message']}")
