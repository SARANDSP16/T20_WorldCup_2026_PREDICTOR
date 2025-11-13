"""Tournament Simulator Page"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def show(datasets, fe, simulator):
    st.markdown('<h1 class="main-header">🏆 T20 World Cup 2026 Simulator</h1>', unsafe_allow_html=True)
    st.markdown("### Monte Carlo Tournament Prediction")
    
    # Tournament info
    st.info("""
    **T20 World Cup 2026** will feature 20 teams divided into 4 groups.
    Top 2 from each group advance to Super 8, followed by knockouts.
    """)
    
    # Show groups
    st.markdown("### 🎯 Tournament Groups")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for group_name in list(simulator.groups.keys())[:2]:
            st.markdown(f"**{group_name}**")
            for team in simulator.groups[group_name]:
                st.write(f"  • {team}")
    
    with col2:
        for group_name in list(simulator.groups.keys())[2:]:
            st.markdown(f"**{group_name}**")
            for team in simulator.groups[group_name]:
                st.write(f"  • {team}")
    
    st.markdown("---")
    
    # Simulation controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        n_simulations = st.slider("Number of Simulations", 100, 10000, 1000, step=100)
    
    with col2:
        st.write("")
        st.write("")
        run_sim = st.button("🚀 Run Simulation", use_container_width=True)
    
    if run_sim:
        with st.spinner(f"Running {n_simulations} tournament simulations..."):
            predictions = simulator.monte_carlo_simulation(n_simulations)
            
            st.success("✅ Simulation Complete!")
            
            # Winner probabilities
            st.markdown("---")
            st.markdown("### 🏆 Championship Probabilities")
            
            winner_probs = predictions['winner_probabilities']
            top_10_winners = dict(list(winner_probs.items())[:10])
            
            fig = px.bar(
                x=list(top_10_winners.values()),
                y=list(top_10_winners.keys()),
                orientation='h',
                title='Top 10 Championship Contenders',
                labels={'x': 'Win Probability (%)', 'y': 'Team'},
                color=list(top_10_winners.values()),
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500, showlegend=False)
            fig.update_yaxis(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)
            
            # Most likely winner
            most_likely = list(winner_probs.items())[0]
            st.success(f"**Most Likely Champion:** {most_likely[0]} ({most_likely[1]:.2f}%)")
            
            # Semifinal probabilities
            st.markdown("---")
            st.markdown("### 🥈 Semi-Final Qualification Probabilities")
            
            sf_probs = predictions['semifinal_probabilities']
            top_10_sf = dict(list(sf_probs.items())[:10])
            
            fig = px.bar(
                x=list(top_10_sf.values()),
                y=list(top_10_sf.keys()),
                orientation='h',
                title='Top 10 Semi-Final Contenders',
                labels={'x': 'Probability (%)', 'y': 'Team'},
                color=list(top_10_sf.values()),
                color_continuous_scale='Oranges'
            )
            fig.update_layout(height=500, showlegend=False)
            fig.update_yaxis(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)
            
            # Qualification probabilities
            st.markdown("---")
            st.markdown("### 🎯 Super 8 Qualification Probabilities")
            
            qual_probs = predictions['qualification_probabilities']
            
            fig = px.bar(
                x=list(qual_probs.values()),
                y=list(qual_probs.keys()),
                orientation='h',
                title='Qualification Chances',
                labels={'x': 'Probability (%)', 'y': 'Team'},
                color=list(qual_probs.values()),
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=600, showlegend=False)
            fig.update_yaxis(categoryorder='total ascending')
            st.plotly_chart(fig, use_container_width=True)
            
            # Key insights
            st.markdown("---")
            st.markdown("### 💡 Key Insights")
            
            top_3 = list(winner_probs.items())[:3]
            
            st.info(f"🥇 **Favorites:** {top_3[0][0]} ({top_3[0][1]:.1f}%), {top_3[1][0]} ({top_3[1][1]:.1f}%), {top_3[2][0]} ({top_3[2][1]:.1f}%)")
            
            dark_horses = [team for team, prob in winner_probs.items() if 3 < prob < 10]
            if dark_horses:
                st.success(f"🐴 **Dark Horses:** {', '.join(dark_horses[:3])}")
            
            underdogs = [team for team, prob in qual_probs.items() if prob < 30]
            if underdogs:
                st.warning(f"⚠️ **Unlikely to Qualify:** {', '.join(underdogs[:5])}")
