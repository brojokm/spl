import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
from core.betting import place_bet
from core.results import update_result
from core.excel_storage import init_excel_files
import json
from datetime import datetime
import pandas as pd
from core.github_storage import test_github_connection
from core.github_storage import update_json_file

# Initialize session state for confirmation dialog
if 'confirm_update' not in st.session_state:
    st.session_state.confirm_update = False
if 'confirm_match_id' not in st.session_state:
    st.session_state.confirm_match_id = None
if 'confirm_winner' not in st.session_state:
    st.session_state.confirm_winner = None

# Set page configuration
st.set_page_config(
    page_title="SPL Betting Platform - Admin",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with better contrast
st.markdown("""
<style>
    /* Base theme */
    .stApp {
        background-color: #1e1e2e;
        color: #e0e0e0;
    }
    
    /* Increase sidebar width */
    [data-testid="stSidebar"] {
        min-width: 530px !important;
        max-width: 530px !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 2rem;
        color: #89b4fa;
        text-align: center;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #313244;
    }
    .section-header {
        font-size: 1.5rem;
        color: #89b4fa;
        margin-top: 1.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #313244;
    }
    
    /* Boxes */
    .info-box {
        margin-bottom: 0.8rem;
    }
    .success-box {
        margin-bottom: 0.8rem;
    }
    .warning-box {
        margin-bottom: 0.8rem;
    }
    .match-details {
        margin-bottom: 0.8rem;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #128306;
        color: #1e1e2e;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.4rem 0.8rem;
        width: 20%;
        margin: 0 auto;
        display: block;
    }
    .stButton button:hover {
        background-color: #16a108;
    }
    
    /* Text highlights */
    .team-balance {
        font-size: 1.3rem;
        font-weight: bold;
        color: #89b4fa;
    }
    .home-team {
        font-weight: bold;
        color: #a6e3a1;
    }
    
    /* Form elements */
    div.stSelectbox > div[data-baseweb="select"] > div {
        background-color: #313244;
        border-color: #45475a;
        color: #e0e0e0;
    }
    div.stNumberInput > div > div > input {
        background-color: #313244;
        border-color: #45475a;
        color: #e0e0e0;
    }
    .stSlider > div > div {
        background-color: #45475a;
    }
    .stSlider > div > div > div > div {
        background-color: #89b4fa;
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem !important;
    }
    .dataframe th {
        background-color: #45475a !important;
        color: #cdd6f4 !important;
        padding: 0.4rem !important;
    }
    .dataframe td {
        background-color: #313244 !important;
        color: #e0e0e0 !important;
        padding: 0.4rem !important;
    }
    
    /* Make everything more compact */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        margin: 0 0.5rem 0 0;
        padding: 0.2rem 0.5rem;
    }
    .stTextInput > div > div > input {
        padding: 0.4rem;
    }
    
    /* Update result container */
    .update-result-container {
        max-width: 75%;
        margin: 0 auto;
    }
    
    /* Form container */
    .form-container {
        background-color: #313244;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem auto;
        max-width: 90%;
    }
    
    /* Logout button */
    .logout-button button {
        width: 100% !important;
    }

    /* Section containers with border */
    .section-box {
        background-color: #313244;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        border: 2px solid #45475a;
    }
    
    /* Make form submit button green */
    .stButton>button, div[data-testid="stFormSubmitButton"] button {
        background-color: #128306 !important;
        color: #1e1e2e !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        border: none !important;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #16a108 !important;
    }
    .stButton>button:active, div[data-testid="stFormSubmitButton"] button:active {
        background-color: #0f6605 !important;
    }
    
    /* Home page link */
    .home-link {
        margin-top: 20px;
        padding: 10px;
        background-color: #313244;
        border-radius: 5px;
        text-align: center;
    }
    .home-link a {
        color: #89b4fa;
        text-decoration: none;
        font-weight: bold;
    }
    .home-link a:hover {
        text-decoration: underline;
    }

    /* GitHub sync button styling */
    .github-sync-btn {
        width: 50% !important;
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.75rem !important;
        border-radius: 5px !important;
        border: none !important;
        cursor: pointer !important;
        margin-top: 10px !important;
    }
    
    .github-sync-btn:hover {
        background-color: #45a049 !important;
    }
            

    /* GitHub sync button styling */
    .github-sync-btn1 {
        width: 150% !important;
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 0.75rem !important;
        border-radius: 5px !important;
        border: none !important;
        cursor: pointer !important;
        margin-top: 10px !important;
    }
    
    .github-sync-btn:hover {
        background-color: #45a049 !important;
    }

    /* Override button width only in sidebar */
    [data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        margin: 5px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Excel files
init_excel_files()

# Main header
st.markdown("<h1 class='main-header'>🏏 SPL Betting Platform - Admin Panel</h1>", unsafe_allow_html=True)

# Check if user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in from the main page to access admin features.")
    st.markdown("""
    <div class="home-link">
        <a href="/" target="_self">Go to Home Page</a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Helper function to format currency
def format_currency(amount):
    """Format amount in Indian currency format (Lakhs and Crores)"""
    if amount >= 10000000:  # 1 Crore = 10,000,000
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh = 100,000
        return f"₹{amount/100000:.2f} Lakh"
    else:
        return f"₹{amount:,}"

# Helper function to format date
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %b %Y")
    except:
        return date_str

# Cache data loading to improve performance
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    with open("data/teams.json") as f:
        teams = json.load(f)
    with open("data/matches.json") as f:
        matches = json.load(f)
    try:
        with open("data/bets.json") as f:
            bets = json.load(f)
    except:
        bets = []
    return teams, matches, bets

# Load data
teams, matches, bets = load_data()

# Create team options for dropdowns
team_options = [team["team"] for team in teams]

# Add a link to the Home page
st.sidebar.markdown("""
<div class="home-link">
    <a href="/" target="_self">← Back to Home Page</a>
</div>
""", unsafe_allow_html=True)

# Create a container for centered content
with st.container():
    # Place Bet Section
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col2:
        st.markdown("""
        <div style="background-color: #313244; border-radius: 8px; padding: .5rem; margin-bottom: 1rem; margin-top: 1rem; border: 2px solid #45475a;">
        <h2 class='section-header'>💰 Place Bet</h2>
        """, unsafe_allow_html=True)
        
        # Team selection
        team = st.selectbox("Select Your Team", team_options)
        
        # Get team info
        selected_team_info = next((t for t in teams if t["team"] == team), None)
        home_team = ""
        
        if selected_team_info:
            current_balance = selected_team_info.get('balance', 0)
            st.markdown(f"<div class='team-balance'>Current Balance: {format_currency(current_balance)}</div>", unsafe_allow_html=True)
            home_team = selected_team_info.get("home_team", "")
            if home_team:
                st.markdown(f"<div class='home-team'>Home team: {home_team} (4x payout)</div>", unsafe_allow_html=True)
        
        # Match selection
        # Filter matches that don't have a winner yet
        available_matches = [m for m in matches if m.get("winner") is None]
        
        if not available_matches:
            st.markdown("<div class='warning-box'>No upcoming matches available for betting.</div>", unsafe_allow_html=True)
        else:
            # Include formatted date in the match options
            match_options = [f"{m['match_id']}: {m['team1']} vs {m['team2']} ({format_date(m['date'])})" for m in available_matches]
            match_selection = st.selectbox("Select Match", match_options)
            match_id = int(match_selection.split(":")[0])
            
            # Get match details
            selected_match = next((m for m in matches if m["match_id"] == match_id), None)
            if selected_match:
                # Display only venue in a nice box
                st.markdown(f"""
                <div class='match-details'>
                    <p><strong>Venue:</strong> {selected_match['venue']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if this is a home team match
                is_home_team_match = False
                if selected_team_info and home_team and (selected_match["team1"] == home_team or selected_match["team2"] == home_team):
                    is_home_team_match = True
                    st.markdown(f"<div class='info-box'>This match involves your home team ({home_team}). You must bet on your home team.</div>", unsafe_allow_html=True)
                    
                    # For home team matches, pre-select and disable the dropdown
                    prediction_options = [home_team]
                    prediction_index = 0
                    prediction = st.selectbox(
                        "Predicted Winner (Home Team - Locked)", 
                        options=prediction_options,
                        index=prediction_index,
                        disabled=True
                    )
                else:
                    # For non-home team matches, allow selection between the two teams
                    prediction = st.selectbox("Predicted Winner", 
                                            [selected_match["team1"], selected_match["team2"]])
            else:
                prediction = st.text_input("Predicted Winner (Team Name)")
            
            # Input amount in lakhs with a number input
            lakh_amount = st.number_input("Bet Amount (in Lakhs)", min_value=5, step=5, value=5)
            amount = lakh_amount * 100000  # Convert lakhs to actual amount
            
            st.markdown(f"""
            <div class='info-box'>
                <p>You are betting: <strong>{format_currency(amount)}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display simple payout information
            if selected_team_info and selected_match:
                is_home_team_bet = home_team == prediction and is_home_team_match
                multiplier = 4 if is_home_team_bet else 2
                potential_winnings = amount * multiplier
                
                st.markdown(f"""
                <div class='success-box'>
                    <p>Payout multiplier: <strong>{multiplier}x</strong></p>
                    <p>Potential winnings: <strong>{format_currency(potential_winnings)}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Place Bet"):
                result = place_bet(team, match_id, prediction, amount)
                if "successfully" in result:
                    st.success(result)
                    # Clear cache to force data reload
                    load_data.clear()
                    st.rerun()  # Refresh the page to show updated balance
                else:
                    st.error(result)
        st.markdown("</div>", unsafe_allow_html=True)
    
    
    # Update Match Result Section
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col2:
        # Show confirmation dialog above the section if needed
        if st.session_state.confirm_update:
            st.markdown("""
            <div style="background-color: #f38ba8; border-radius: 8px; padding: 1rem; margin-bottom: 2rem;">
                <h3 style="color: white; margin-bottom: 0.5rem;">⚠️ Confirm Match Result Update</h3>
                <p style="color: white;">Are you sure you want to update this match result? This action cannot be undone.</p>
                <p style="color: white; font-weight: bold;">Winner: {}</p>
            </div>
            """.format(st.session_state.confirm_winner), unsafe_allow_html=True)
            
            col1_confirm, col2_confirm = st.columns(2)
            
            with col1_confirm:
                if st.button("No, Cancel"):
                    st.session_state.confirm_update = False
                    st.session_state.confirm_match_id = None
                    st.session_state.confirm_winner = None
                    st.rerun()
            
            with col2_confirm:
                if st.button("Yes, Update Result"):
                    result = update_result(st.session_state.confirm_match_id, st.session_state.confirm_winner)
                    if "updated" in result:
                        st.success(result)
                        # Clear cache to force data reload
                        load_data.clear()
                        # Reset confirmation dialog state
                        st.session_state.confirm_update = False
                        st.session_state.confirm_match_id = None
                        st.session_state.confirm_winner = None
                        st.rerun()  # Refresh the page to show updated balances
                    else:
                        st.error(result)
        
        # The regular Update Match Result section
        st.markdown("""
        <div style="background-color: #313244; border-radius: 8px; padding: .5rem; margin-top: 5rem; margin-bottom: 1rem; border: 2px solid #45475a;">
        <h2 class='section-header'>🏁 Update Match Result</h2>
        """, unsafe_allow_html=True)
        
        # Create columns for the form
        col1_result, col2_result = st.columns(2)
        
        with col1_result:
            # Filter matches that don't have a winner yet
            pending_matches = [m for m in matches if not m.get("winner")]
            
            # Match selection
            match_result_options = [f"Match {m['match_id']}: {m['team1']} vs {m['team2']} ({format_date(m['date'])})" 
                                    for m in pending_matches]
            
            if match_result_options:
                match_result_selection = st.selectbox("Select Match to Update", 
                                                    match_result_options, 
                                                    key="match_result_select")
                match_result_id = int(match_result_selection.split(":")[0].replace("Match ", "").strip())
                
                # Get the selected match
                selected_match = next((m for m in matches if m["match_id"] == match_result_id), None)
                
                # Display match details
                if selected_match:
                    st.markdown(f"""
                    <div class='match-details'>
                        <p><strong>Date:</strong> {format_date(selected_match['date'])}</p>
                        <p><strong>Teams:</strong> {selected_match['team1']} vs {selected_match['team2']}</p>
                        <p><strong>Venue:</strong> {selected_match['venue']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No pending matches to update.")
                match_result_id = None
                selected_match = None
        
        with col2_result:
            if selected_match:
                # Create a selectbox with the two teams
                if selected_match["team1"] and selected_match["team2"]:
                    winner_team = st.selectbox("Select Winner",
                                            [selected_match["team1"], selected_match["team2"]], key="winner")
                else:
                    winner_team = st.text_input("Winner Team Name")
            else:
                winner_team = st.text_input("Winner Team Name")
        
        # Only show the update button if there are pending matches
        if match_result_options:
            if st.button("Update Result"):
                # Set confirmation dialog state
                st.session_state.confirm_update = True
                st.session_state.confirm_match_id = match_result_id
                st.session_state.confirm_winner = winner_team
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True) 

def sync_data_to_github():
    """Force sync all data files to GitHub"""
    # from core.github_storage import update_json_file
    
    success = True
    messages = []
    
    try:
        # Load data files
        with open("data/teams.json") as f:
            teams = json.load(f)
        with open("data/matches.json") as f:
            matches = json.load(f)
        try:
            with open("data/bets.json") as f:
                bets = json.load(f)
        except:
            bets = []
            
        # Update GitHub
        if not update_json_file("data/teams.json", teams):
            success = False
            messages.append("Failed to sync teams.json")
            
        if not update_json_file("data/matches.json", matches):
            success = False
            messages.append("Failed to sync matches.json")
            
        if not update_json_file("data/bets.json", bets):
            success = False
            messages.append("Failed to sync bets.json")
            
        if success:
            return True, "All data successfully synced to GitHub"
        else:
            return False, "Some files failed to sync: " + ", ".join(messages)
            
    except Exception as e:
        return False, f"Error syncing data: {str(e)}"

# Add this button to your sidebar
with st.sidebar:
    st.markdown("""
    <h2 class='section-header' style='text-align: center; margin-top: 50px;'>GitHub Integration</h2>
    """, unsafe_allow_html=True)
    
    # Test connection button
    if st.button("Test GitHub Connection", key="github-sync-btn", use_container_width=True):
        with st.spinner("Testing GitHub connection..."):
            success, message = test_github_connection()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Force sync button
    if st.button("Force Sync to GitHub", key="github-sync-btn1", use_container_width=True):
        with st.spinner("Syncing data to GitHub..."):
            success, message = test_github_connection()
            if not success:
                st.error(f"Could not connect to GitHub: {message}")
            else:
                success, message = sync_data_to_github()
                if success:
                    st.success(message)
                else:
                    st.error(message)