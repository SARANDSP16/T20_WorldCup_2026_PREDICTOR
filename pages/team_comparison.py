"""Team Comparison Page"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def show(datasets, fe, match_predictor):
    st.markdown('<h1 class="main-header">⚔️ Team Comparison</h1>', unsafe_allow_html=True)
    
    teams = sorted(datasets['team_rankings']['Team'].tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("Select Team 1", teams, index=0)
    with col2:
        team2 = st.selectbox("Select Team 2", teams, index=1)
    
    if st.button("Compare Teams", use_container_width=True):
        # Get team data
        rankings = datasets['team_rankings']
        career = datasets['player_career']
        
        team1_rank = rankings[rankings['Team'] == team1].iloc[0] if not rankings[rankings['Team'] == team1].empty else None
        team2_rank = rankings[rankings['Team'] == team2].iloc[0] if not rankings[rankings['Team'] == team2].empty else None
        
        # Rankings comparison
        st.markdown("### 📊 ICC Rankings")
        col1, col2 = st.columns(2)
        
        with col1:
            if team1_rank is not None:
                st.metric(f"{team1} Rank", f"#{team1_rank['pos']}")
                st.metric("Rating", f"{team1_rank['rating']}")
        
        with col2:
            if team2_rank is not None:
                st.metric(f"{team2} Rank", f"#{team2_rank['pos']}")
                st.metric("Rating", f"{team2_rank['rating']}")
        
        # Squad comparison
        st.markdown("---")
        st.markdown("### 👥 Squad Comparison")
        
        squad1 = career[career['team'] == team1]
        squad2 = career[career['team'] == team2]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {team1} Squad")
            st.metric("Squad Size", len(squad1))
            st.metric("Avg Batting SR", f"{squad1['strike_rate'].mean():.2f}")
            st.metric("Total Wickets", int(squad1['wickets'].sum()))
            st.metric("Avg Economy", f"{squad1['economy'].mean():.2f}")
        
        with col2:
            st.markdown(f"#### {team2} Squad")
            st.metric("Squad Size", len(squad2))
            st.metric("Avg Batting SR", f"{squad2['strike_rate'].mean():.2f}")
            st.metric("Total Wickets", int(squad2['wickets'].sum()))
            st.metric("Avg Economy", f"{squad2['economy'].mean():.2f}")
        
        # Strength vectors
        st.markdown("---")
        st.markdown("### 💪 Team Strength Analysis")
        
        team1_strength = fe.create_team_strength_vector(team1)
        team2_strength = fe.create_team_strength_vector(team2)
        
        categories = ['Batting', 'Bowling', 'All-rounders', 'Depth', 'Form']
        team1_vals = [team1_strength[1], team1_strength[4], team1_strength[8], team1_strength[11], team1_strength[12]]
        team2_vals = [team2_strength[1], team2_strength[4], team2_strength[8], team2_strength[11], team2_strength[12]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=team1_vals, theta=categories, fill='toself', name=team1))
        fig.add_trace(go.Scatterpolar(r=team2_vals, theta=categories, fill='toself', name=team2))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Head to head
        st.markdown("---")
        st.markdown("### 📜 Head-to-Head")
        
        h2h_rate = fe.get_h2h_win_rate(team1, team2)
        
        fig = go.Figure(go.Bar(
            x=[h2h_rate, 1-h2h_rate],
            y=[team1, team2],
            orientation='h',
            text=[f"{h2h_rate:.1%}", f"{1-h2h_rate:.1%}"],
            textposition='inside',
            marker_color=['#1f77b4', '#ff7f0e']
        ))
        fig.update_layout(title='Historical Win Rate', xaxis_title='Win %', height=300)
        st.plotly_chart(fig, use_container_width=True)
