"""Venue Analytics Page"""
import streamlit as st
import plotly.express as px
import pandas as pd

def show(datasets, fe):
    st.markdown('<h1 class="main-header">🌍 Venue Analytics</h1>', unsafe_allow_html=True)
    
    vs_venue = datasets['player_vs_venue']
    venues = sorted([v for v in vs_venue['venue'].unique() if v and len(v) > 3])
    
    selected_venue = st.selectbox("Select Venue", venues)
    
    if selected_venue:
        venue_data = vs_venue[vs_venue['venue'] == selected_venue]
        
        # Venue stats
        st.markdown(f"## {selected_venue}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Matches Played", int(venue_data['matches_x'].sum()))
        with col2:
            avg_sr = venue_data['strike_rate'].mean()
            st.metric("Avg Strike Rate", f"{avg_sr:.2f}")
        with col3:
            avg_economy = venue_data['economy'].mean()
            st.metric("Avg Economy", f"{avg_economy:.2f}")
        with col4:
            batting_friendly = "Yes" if avg_sr > 130 else "No"
            st.metric("Batting Friendly", batting_friendly)
        
        st.markdown("---")
        
        # Top batters at venue
        st.markdown("### 🏏 Top Batters at This Venue")
        top_batters = venue_data.nlargest(10, 'runs')[['player_name', 'runs', 'strike_rate', 'avg']]
        
        fig = px.bar(top_batters, x='player_name', y='runs', color='strike_rate',
                    title='Top 10 Run Scorers', color_continuous_scale='Blues')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top bowlers at venue
        st.markdown("### ⚾ Top Bowlers at This Venue")
        top_bowlers = venue_data[venue_data['wickets'] > 0].nlargest(10, 'wickets')[
            ['player_name', 'wickets', 'economy', 'bowling_avg']]
        
        fig = px.bar(top_bowlers, x='player_name', y='wickets', color='economy',
                    title='Top 10 Wicket Takers', color_continuous_scale='Reds_r')
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Venue characteristics
        st.markdown("---")
        st.markdown("### 📊 Venue Characteristics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Batting Conditions:**")
            if avg_sr > 140:
                st.success("🔥 Excellent for batting - High scoring venue")
            elif avg_sr > 130:
                st.info("✅ Good for batting")
            else:
                st.warning("⚠️ Challenging for batters")
        
        with col2:
            st.markdown("**Bowling Conditions:**")
            if avg_economy < 7.5:
                st.success("🎯 Bowler-friendly venue")
            elif avg_economy < 8.5:
                st.info("⚖️ Balanced venue")
            else:
                st.warning("💸 Difficult for bowlers")
