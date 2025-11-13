"""
Home Page - Dashboard Overview
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def show(datasets, fe):
    """Display home page"""
    
    st.markdown('<h1 class="main-header">🏏 T20 World Cup 2026 Analytics</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive Analytics, Predictions & AI Assistant")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Active Players", "385+")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Teams", "20")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        total_matches = len(datasets['match_summary'])
        st.metric("Matches Analyzed", f"{total_matches:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("ML Models", "3")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top teams
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Top 10 ICC T20I Rankings")
        rankings = datasets['team_rankings'].head(10)
        
        fig = px.bar(
            rankings,
            x='rating',
            y='Team',
            orientation='h',
            color='rating',
            color_continuous_scale='Blues',
            title='ICC Team Rankings 2025'
        )
        fig.update_layout(height=500, showlegend=False)
        fig.update_yaxis(categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### ⭐ Top Batters by Strike Rate")
        career = datasets['player_career']
        
        # Filter: min 500 runs
        top_batters = career[career['runs'] >= 500].nlargest(10, 'strike_rate')
        
        fig = px.bar(
            top_batters,
            x='strike_rate',
            y='player_full_name',
            orientation='h',
            color='strike_rate',
            color_continuous_scale='Oranges',
            title='Highest Strike Rates (Min 500 runs)',
            hover_data=['team', 'runs']
        )
        fig.update_layout(height=500, showlegend=False)
        fig.update_yaxis(categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Role distribution and top wicket-takers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Player Role Distribution")
        role_dist = career['role'].value_counts()
        
        fig = px.pie(
            values=role_dist.values,
            names=role_dist.index,
            title='Distribution of Player Roles',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎳 Top Wicket Takers")
        top_bowlers = career.nlargest(10, 'wickets')
        
        fig = px.bar(
            top_bowlers,
            x='wickets',
            y='player_full_name',
            orientation='h',
            color='economy',
            color_continuous_scale='Greens_r',
            title='Most Wickets',
            hover_data=['team', 'economy']
        )
        fig.update_layout(height=500)
        fig.update_yaxis(categoryorder='total ascending')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # System features
    st.markdown("### 🚀 System Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📈 Analytics
        - Player Performance Explorer
        - Team Strength Analysis
        - Venue Statistics
        - Head-to-Head Records
        - Form Tracking
        """)
    
    with col2:
        st.markdown("""
        #### 🤖 AI/ML Models
        - Match Outcome Prediction
        - Score Forecasting
        - Player Performance Model
        - Tournament Simulation
        - Monte Carlo Analysis
        """)
    
    with col3:
        st.markdown("""
        #### 💬 AI Assistant
        - Natural Language Queries
        - Player Comparisons
        - Match Predictions
        - Statistical Insights
        - Tournament Forecasts
        """)
    
    st.markdown("---")
    
    # Recent matches
    st.markdown("### 📅 Recent Match Summary")
    matches = datasets['match_summary'].sort_values('date', ascending=False).head(10)
    
    if not matches.empty:
        display_matches = matches[['date', 'team1', 'team2', 'winner', 'venue']].copy()
        display_matches['date'] = pd.to_datetime(display_matches['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        st.dataframe(display_matches, use_container_width=True, hide_index=True)
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📊 Quick Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_runs = career['runs'].sum()
        st.metric("Total Runs Scored", f"{int(total_runs):,}")
    
    with col2:
        total_wickets = career['wickets'].sum()
        st.metric("Total Wickets Taken", f"{int(total_wickets):,}")
    
    with col3:
        avg_sr = career['strike_rate'].mean()
        st.metric("Avg Strike Rate", f"{avg_sr:.2f}")
    
    with col4:
        total_sixes = career['sixes'].sum()
        st.metric("Total Sixes", f"{int(total_sixes):,}")
    
    # Call to action
    st.markdown("---")
    st.info("👈 Use the sidebar to navigate to different sections and explore the data!")
