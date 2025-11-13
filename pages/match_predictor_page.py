"""
Match Predictor Page
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def show(datasets, fe, match_predictor, score_predictor):
    """Display match predictor page"""
    
    st.markdown('<h1 class="main-header">🎯 Match Predictor</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Match Outcome & Score Prediction")
    
    teams = sorted(datasets['team_rankings']['Team'].tolist())
    venues = sorted([v for v in datasets['player_vs_venue']['venue'].unique() if v and len(v) > 3])
    
    # Input form
    col1, col2, col3 = st.columns(3)
    
    with col1:
        team1 = st.selectbox("Team 1", teams, index=teams.index('India') if 'India' in teams else 0)
    
    with col2:
        team2 = st.selectbox("Team 2", teams, index=teams.index('Australia') if 'Australia' in teams else 1)
    
    with col3:
        venue = st.selectbox("Venue", venues, index=0)
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            toss_winner = st.selectbox("Toss Winner", ['Unknown', team1, team2])
        
        with col2:
            batting_first = st.checkbox("Batting First", value=True) if toss_winner != 'Unknown' else None
    
    st.markdown("---")
    
    # Predict button
    if st.button("🔮 Predict Match", use_container_width=True):
        with st.spinner("Analyzing match..."):
            
            # Match prediction
            toss = toss_winner if toss_winner != 'Unknown' else None
            match_result = match_predictor.predict_match(team1, team2, venue, fe, toss, batting_first)
            
            # Score predictions
            team1_score = score_predictor.predict_score(team1, team2, venue, fe)
            team2_score = score_predictor.predict_score(team2, team1, venue, fe)
            
            # Display results
            st.success(f"✅ Prediction Complete!")
            
            # Winner prediction
            st.markdown("### 🏆 Match Winner Prediction")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.markdown(f"#### {team1}")
                st.markdown(f'<div style="font-size: 3rem; text-align: center;">{match_result["team1_prob"]:.1%}</div>', 
                           unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### Confidence")
                confidence_color = {
                    'High': '#2ecc71',
                    'Medium': '#f39c12',
                    'Low': '#e74c3c'
                }
                st.markdown(f'<div style="font-size: 2rem; text-align: center; color: {confidence_color.get(match_result["confidence"], "#95a5a6")};">{match_result["confidence"]}</div>', 
                           unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"#### {team2}")
                st.markdown(f'<div style="font-size: 3rem; text-align: center;">{match_result["team2_prob"]:.1%}</div>', 
                           unsafe_allow_html=True)
            
            # Probability visualization
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[match_result['team1_prob'], match_result['team2_prob']],
                y=[team1, team2],
                orientation='h',
                marker=dict(
                    color=['#1f77b4', '#ff7f0e'],
                    line=dict(color='black', width=2)
                ),
                text=[f"{match_result['team1_prob']:.1%}", f"{match_result['team2_prob']:.1%}"],
                textposition='inside',
                textfont=dict(size=20, color='white')
            ))
            
            fig.update_layout(
                title='Win Probability',
                xaxis_title='Probability',
                yaxis_title='Team',
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Score predictions
            st.markdown("### 📊 Predicted Scores")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {team1}")
                st.metric("Predicted Score", team1_score['predicted_score'])
                st.write(f"**Range:** {team1_score['range_min']} - {team1_score['range_max']}")
                st.write(f"**Confidence:** {team1_score['confidence']}")
                
                # Score breakdown
                st.markdown("**Score Breakdown:**")
                st.write(f"Powerplay (1-6): {team1_score['powerplay_score']}")
                st.write(f"Middle (7-15): {team1_score['middle_overs_score']}")
                st.write(f"Death (16-20): {team1_score['death_overs_score']}")
            
            with col2:
                st.markdown(f"#### {team2}")
                st.metric("Predicted Score", team2_score['predicted_score'])
                st.write(f"**Range:** {team2_score['range_min']} - {team2_score['range_max']}")
                st.write(f"**Confidence:** {team2_score['confidence']}")
                
                # Score breakdown
                st.markdown("**Score Breakdown:**")
                st.write(f"Powerplay (1-6): {team2_score['powerplay_score']}")
                st.write(f"Middle (7-15): {team2_score['middle_overs_score']}")
                st.write(f"Death (16-20): {team2_score['death_overs_score']}")
            
            # Score comparison
            phases = ['Powerplay', 'Middle', 'Death']
            team1_phases = [team1_score['powerplay_score'], team1_score['middle_overs_score'], team1_score['death_overs_score']]
            team2_phases = [team2_score['powerplay_score'], team2_score['middle_overs_score'], team2_score['death_overs_score']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name=team1,
                x=phases,
                y=team1_phases,
                marker_color='#1f77b4'
            ))
            
            fig.add_trace(go.Bar(
                name=team2,
                x=phases,
                y=team2_phases,
                marker_color='#ff7f0e'
            ))
            
            fig.update_layout(
                title='Phase-wise Score Comparison',
                xaxis_title='Phase',
                yaxis_title='Runs',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Key insights
            st.markdown("### 💡 Key Insights")
            
            insights = []
            
            if match_result['probability'] > 0.7:
                insights.append(f"🔥 {match_result['winner']} is the strong favorite with {match_result['probability']:.1%} win probability")
            elif match_result['probability'] > 0.55:
                insights.append(f"⚖️ {match_result['winner']} has a slight edge, but it's a close contest")
            else:
                insights.append(f"🤝 Very evenly matched teams - could go either way!")
            
            if team1_score['predicted_score'] > 180:
                insights.append(f"💪 {team1} likely to post a strong total (180+)")
            
            if team2_score['predicted_score'] > 180:
                insights.append(f"💪 {team2} likely to post a strong total (180+)")
            
            if abs(team1_score['predicted_score'] - team2_score['predicted_score']) < 10:
                insights.append("📊 Predicted scores are very close - expect a thriller!")
            
            h2h = fe.get_h2h_win_rate(team1, team2)
            insights.append(f"📜 Historical H2H: {team1} wins {h2h:.1%} of matches against {team2}")
            
            for insight in insights:
                st.info(insight)
    
    # Historical H2H
    st.markdown("---")
    st.markdown("### 📜 Historical Head-to-Head")
    
    if st.button("Show H2H Stats"):
        h2h = fe.get_h2h_win_rate(team1, team2)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"{team1} Wins", f"{h2h:.1%}")
        
        with col2:
            st.metric("Total Matches", "Based on Historical Data")
        
        with col3:
            st.metric(f"{team2} Wins", f"{1-h2h:.1%}")
