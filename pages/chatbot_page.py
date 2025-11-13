"""AI Chatbot Page"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def show(chatbot):
    st.markdown('<h1 class="main-header">🤖 AI Cricket Assistant</h1>', unsafe_allow_html=True)
    st.markdown("### Ask me anything about players, teams, matches, and predictions!")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.markdown("""
        - "Predict India vs Australia at Wankhede"
        - "Compare Virat Kohli and Babar Azam"
        - "Show me top batters"
        - "What's the squad for England?"
        - "Who will win India vs Pakistan?"
        - "Predict score for South Africa vs New Zealand"
        - "Best bowlers in the tournament"
        - "Show performance of Rohit Sharma"
        """)
    
    # Chat input
    user_query = st.text_input("💬 Your Question:", placeholder="Ask me anything about T20 cricket...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("Send", use_container_width=True)
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Process query
    if send_button and user_query:
        with st.spinner("🤔 Thinking..."):
            response = chatbot.query(user_query)
            
            # Add to history
            st.session_state.chat_history.append({
                'query': user_query,
                'response': response
            })
    
    # Display chat history
    st.markdown("---")
    
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            # User query
            st.markdown(f"**👤 You:** {chat['query']}")
            
            # Bot response
            response = chat['response']
            
            if response['success']:
                st.markdown(f"**🤖 Assistant:** {response['message']}")
                
                # Display data if available
                if response.get('data'):
                    data = response['data']
                    viz = response.get('visualization')
                    
                    if viz == 'bar_chart' and 'team1_prob' in data:
                        # Match prediction visualization
                        fig = go.Figure(go.Bar(
                            x=[data['team1_prob'], data['team2_prob']],
                            y=[data['team1'], data['team2']],
                            orientation='h',
                            marker_color=['#1f77b4', '#ff7f0e'],
                            text=[data['team1_prob'], data['team2_prob']],
                            textposition='inside'
                        ))
                        fig.update_layout(title='Win Probability', height=250)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.info(f"**Winner:** {data['winner']} | **Confidence:** {data['confidence']}")
                    
                    elif viz == 'gauge_chart' and 'predicted_score' in data:
                        # Score prediction
                        st.metric("Predicted Score", data['predicted_score'])
                        st.write(f"**Range:** {data['range']}")
                        st.write(f"**Confidence:** {data['confidence']}")
                    
                    elif viz == 'stat_card' and 'name' in data:
                        # Player stats
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Runs", data.get('runs', 0))
                            st.metric("Avg", data.get('batting_avg', 0))
                        with col2:
                            st.metric("Strike Rate", data.get('strike_rate', 0))
                            st.metric("Wickets", data.get('wickets', 0))
                        with col3:
                            st.metric("Economy", data.get('economy', 0))
                            st.metric("Catches", data.get('catches', 0))
                    
                    elif viz == 'leaderboard' and isinstance(data, list):
                        # Leaderboard
                        import pandas as pd
                        df = pd.DataFrame(data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    elif viz == 'team_overview' and 'squad_size' in data:
                        # Team info
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Ranking", data.get('ranking', 'N/A'))
                            st.metric("Squad Size", data.get('squad_size', 0))
                        with col2:
                            st.metric("Rating", data.get('rating', 'N/A'))
                        
                        if 'top_batters' in data:
                            st.write("**Top Batters:**", ", ".join(data['top_batters']))
                        if 'top_bowlers' in data:
                            st.write("**Top Bowlers:**", ", ".join(data['top_bowlers']))
                
                # Show suggestions if available
                if response.get('suggestions'):
                    st.markdown("**💡 Try asking:**")
                    for suggestion in response['suggestions']:
                        st.write(f"  • {suggestion}")
            else:
                st.error(f"**🤖 Assistant:** {response['message']}")
                if response.get('suggestion'):
                    st.info(f"💡 {response['suggestion']}")
            
            st.markdown("---")
    else:
        st.info("👋 Ask me a question to get started!")
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📊 Chat Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Queries", len(st.session_state.chat_history))
    
    with col2:
        successful = sum(1 for chat in st.session_state.chat_history if chat['response']['success'])
        st.metric("Successful", successful)
    
    with col3:
        if st.session_state.chat_history:
            success_rate = (successful / len(st.session_state.chat_history)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
