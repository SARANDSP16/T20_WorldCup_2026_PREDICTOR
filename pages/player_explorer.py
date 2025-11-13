"""
Player Performance Explorer Page
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def show(datasets, fe):
    """Display player explorer page"""
    
    st.markdown('<h1 class="main-header">👤 Player Performance Explorer</h1>', unsafe_allow_html=True)
    
    career = datasets['player_career']
    players = sorted(career['player_full_name'].unique())
    
    # Player selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_player = st.selectbox(
            "🔍 Search Player",
            players,
            help="Type to search for a player"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    if selected_player:
        player_data = career[career['player_full_name'] == selected_player].iloc[0]
        
        # Player header
        st.markdown(f"## {selected_player}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Team", player_data['team'])
        with col2:
            st.metric("Role", player_data['role'])
        with col3:
            st.metric("Matches", int(player_data['matches_played']))
        with col4:
            form_score = fe.calculate_player_form_score(selected_player)
            st.metric("Form Score", f"{form_score:.2f}", 
                     delta="Good" if form_score > 0.6 else "Average")
        
        st.markdown("---")
        
        # Batting and bowling stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏏 Batting Statistics")
            
            bat_metrics = {
                "Runs": int(player_data['runs']),
                "Average": f"{player_data['batting_average']:.2f}",
                "Strike Rate": f"{player_data['strike_rate']:.2f}",
                "Fifties": int(player_data['fifties']),
                "Hundreds": int(player_data['hundreds']),
                "Fours": int(player_data['fours']),
                "Sixes": int(player_data['sixes']),
                "Highest Score": int(player_data['highest_score'])
            }
            
            for metric, value in bat_metrics.items():
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.write(f"**{metric}:**")
                with col_b:
                    st.write(value)
        
        with col2:
            st.markdown("### ⚾ Bowling Statistics")
            
            bowl_metrics = {
                "Wickets": int(player_data['wickets']),
                "Average": f"{player_data['bowling_average']:.2f}",
                "Economy": f"{player_data['economy']:.2f}",
                "5-wicket hauls": int(player_data['five_wicket_hauls']),
                "Balls Bowled": int(player_data['balls_bowled']),
                "Runs Conceded": int(player_data['runs_conceded'])
            }
            
            for metric, value in bowl_metrics.items():
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    st.write(f"**{metric}:**")
                with col_b:
                    st.write(value)
        
        # Radar chart
        st.markdown("---")
        st.markdown("### 📊 Performance Radar")
        
        # Create normalized scores
        categories = ['Batting Avg', 'Strike Rate', 'Sixes', 'Wickets', 'Economy']
        
        # Normalize to 0-100
        values = [
            min(player_data['batting_average'] / 50 * 100, 100),
            min(player_data['strike_rate'] / 150 * 100, 100),
            min(player_data['sixes'] / 100 * 100, 100),
            min(player_data['wickets'] / 100 * 100, 100),
            max(0, 100 - (player_data['economy'] / 10 * 100))  # Lower is better
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=selected_player,
            line_color='#1f77b4'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance vs opponent
        st.markdown("---")
        st.markdown("### ⚔️ Performance vs Opponents")
        
        vs_opp = datasets['player_vs_opponent']
        player_vs_opp = vs_opp[vs_opp['player_name'] == selected_player]
        
        if not player_vs_opp.empty:
            # Batting performance
            bat_vs_opp = player_vs_opp[player_vs_opp['runs'] > 0].sort_values('runs', ascending=False)
            
            if not bat_vs_opp.empty:
                fig = px.bar(
                    bat_vs_opp,
                    x='opponent_team',
                    y='runs',
                    title='Runs vs Each Opponent',
                    color='strike_rate',
                    color_continuous_scale='Greens',
                    hover_data=['avg_bat', 'strike_rate']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Bowling performance
            bowl_vs_opp = player_vs_opp[player_vs_opp['wickets'] > 0].sort_values('wickets', ascending=False)
            
            if not bowl_vs_opp.empty:
                fig = px.bar(
                    bowl_vs_opp,
                    x='opponent_team',
                    y='wickets',
                    title='Wickets vs Each Opponent',
                    color='economy',
                    color_continuous_scale='Reds_r',
                    hover_data=['avg_bowl', 'economy']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No opponent-wise data available for this player.")
        
        # Performance at venues
        st.markdown("---")
        st.markdown("### 🌍 Performance at Venues")
        
        vs_venue = datasets['player_vs_venue']
        player_vs_venue = vs_venue[vs_venue['player_name'] == selected_player]
        
        if not player_vs_venue.empty:
            top_venues = player_vs_venue.nlargest(10, 'runs')
            
            if not top_venues.empty:
                fig = px.bar(
                    top_venues,
                    x='venue',
                    y='runs',
                    title='Top 10 Venues by Runs',
                    color='strike_rate',
                    color_continuous_scale='Blues',
                    hover_data=['matches_x', 'avg']
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No venue-wise data available for this player.")
        
        # Recent form
        st.markdown("---")
        st.markdown("### 📈 Recent Form (Last 10 Matches)")
        
        form = datasets['player_form']
        player_form = form[form['player_name'] == selected_player].sort_values('date', ascending=False).head(10)
        
        if not player_form.empty:
            # Batting form
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=player_form['date'],
                y=player_form['runs'],
                mode='lines+markers',
                name='Runs',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title='Runs in Last 10 Matches',
                xaxis_title='Date',
                yaxis_title='Runs',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Strike rate trend
            if player_form['strike_rate'].sum() > 0:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=player_form['date'],
                    y=player_form['strike_rate'],
                    mode='lines+markers',
                    name='Strike Rate',
                    line=dict(color='#ff7f0e', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title='Strike Rate Trend',
                    xaxis_title='Date',
                    yaxis_title='Strike Rate',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recent form data available for this player.")
        
        # Fielding stats
        st.markdown("---")
        st.markdown("### 🧤 Fielding Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Catches", int(player_data['catches']))
        with col2:
            st.metric("Stumpings", int(player_data['stumpings']))
        with col3:
            st.metric("Run Outs", int(player_data['run_outs']))
        
        # Strengths and weaknesses
        st.markdown("---")
        st.markdown("### 💪 Strengths & Weaknesses")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Strengths")
            strengths = []
            
            if player_data['strike_rate'] > 140:
                strengths.append("🔥 High strike rate power hitter")
            if player_data['batting_average'] > 35:
                strengths.append("📊 Consistent batting average")
            if player_data['sixes'] > 50:
                strengths.append("💪 Big hitting ability")
            if player_data['economy'] < 7.5 and player_data['wickets'] > 20:
                strengths.append("🎯 Economical bowler")
            if player_data['wickets'] > 50:
                strengths.append("⚡ Prolific wicket-taker")
            if player_data['catches'] > 20:
                strengths.append("🧤 Excellent fielder")
            
            if strengths:
                for strength in strengths:
                    st.write(strength)
            else:
                st.write("Developing player with potential")
        
        with col2:
            st.markdown("#### ⚠️ Areas to Improve")
            weaknesses = []
            
            if player_data['strike_rate'] < 110:
                weaknesses.append("🐌 Below-average strike rate")
            if player_data['batting_average'] < 20:
                weaknesses.append("📉 Low batting average")
            if player_data['economy'] > 9 and player_data['balls_bowled'] > 100:
                weaknesses.append("💸 High economy rate")
            if player_data['wickets'] < 10 and player_data['balls_bowled'] > 500:
                weaknesses.append("🎳 Low wicket-taking ability")
            
            if weaknesses:
                for weakness in weaknesses:
                    st.write(weakness)
            else:
                st.write("Well-rounded performer!")
