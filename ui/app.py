import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.betting import place_bet
from core.results import update_result
from core.leaderboard import get_leaderboard
from core.excel_storage import init_excel_files
from core.team_history import get_team_history
import json
from datetime import datetime, timedelta
import pandas as pd
import hashlib

# Replace the plain text password with the hash
PASSWORD_HASH = "f1697db23226e6cc2483c266370b5cd0e8a89f700515f6bc98d2b4a9ff17dc93"

# Create a cookie file path
COOKIE_FILE = "data/.auth_cookie"

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    # Check if there's a valid auth cookie
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r") as f:
                cookie_data = json.load(f)
                # Check if the cookie is still valid (not expired)
                expiry = datetime.fromisoformat(cookie_data.get("expiry", ""))
                if datetime.now() < expiry:
                    st.session_state.authenticated = True
                else:
                    # Cookie expired
                    st.session_state.authenticated = False
                    # Remove expired cookie
                    os.remove(COOKIE_FILE)
        except Exception as e:
            print(f"Error reading auth cookie: {str(e)}")
            st.session_state.authenticated = False
    else:
        st.session_state.authenticated = False

# Add these session state variables at the top of your file, after other session state initializations
if 'confirm_update' not in st.session_state:
    st.session_state.confirm_update = False
if 'confirm_match_id' not in st.session_state:
    st.session_state.confirm_match_id = None
if 'confirm_winner' not in st.session_state:
    st.session_state.confirm_winner = None

# Set page configuration
st.set_page_config(
    page_title="SPL Betting Platform",
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
    
    /* History table */
    .history-won {
        color: #a6e3a1 !important;
        font-weight: bold;
    }
    .history-lost {
        color: #f38ba8 !important;
        font-weight: bold;
    }
    
    /* Auth section */
    .auth-container {
        max-width: 400px;
        margin: 2rem auto;
        padding: 1.5rem;
        background-color: #313244;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .auth-header {
        color: #89b4fa;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .auth-button {
        width: 100% !important;
        margin-top: 1rem !important;
    }
    .locked-section {
        background-color: #313244;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border-left: 4px solid #f38ba8;
    }
    
    /* Center content */
    .centered-content {
        max-width: 80%;
        margin: 0 auto;
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
</style>
""", unsafe_allow_html=True)

# Initialize Excel files
init_excel_files()

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

# Main header
st.markdown("<h1 class='main-header'>🏏 SPL Betting Platform</h1>", unsafe_allow_html=True)

# Authentication section in sidebar
with st.sidebar:
    st.markdown("<h2 class='section-header'>Admin Access</h2>", unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.text_input("Password", type="password", key="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                # Hash the entered password and compare with stored hash
                entered_hash = hashlib.sha256(st.session_state.password.encode()).hexdigest()
                if entered_hash == PASSWORD_HASH:
                    st.session_state.authenticated = True
                    
                    # Create a cookie that expires in 24 hours
                    cookie_data = {
                        "expiry": (datetime.now() + timedelta(hours=24)).isoformat()
                    }
                    
                    # Make sure the data directory exists
                    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
                    
                    # Save the cookie
                    try:
                        with open(COOKIE_FILE, "w") as f:
                            json.dump(cookie_data, f)
                    except Exception as e:
                        st.error(f"Error saving authentication: {str(e)}")
                    
                    st.rerun()
                else:
                    st.error("Incorrect password")
    else:
        st.markdown("<div class='logout-button'>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.authenticated = False
            
            # Remove the cookie file on logout
            if os.path.exists(COOKIE_FILE):
                try:
                    os.remove(COOKIE_FILE)
                except Exception as e:
                    st.error(f"Error removing cookie: {str(e)}")
                
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.success("Logged in as Admin")

# Load data
teams, matches, bets = load_data()

# Create team options for dropdowns
team_options = [team["team"] for team in teams]

# Create a container for centered content
with st.container():
    # Leaderboard Section (Public)
    
    
    # Create a centered container for the leaderboard
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col2:
        st.markdown("""
        <div style="background-color: #313244; border-radius: 8px; padding: .5rem; margin-bottom: 2rem; border: 2px solid #45475a;">
        <h2 class='section-header'>🏆 Leaderboard</h2>
        """, unsafe_allow_html=True)
        
        # Get leaderboard data
        leaderboard = get_leaderboard()
        
        # Create a DataFrame for the leaderboard
        leaderboard_data = []
        for i, team in enumerate(leaderboard):
            leaderboard_data.append({
                "Rank": i + 1,
                "Team": team["team"],
                "Home Team": team.get("home_team", "N/A"),
                "Balance": format_currency(team["balance"])
            })
        
        leaderboard_df = pd.DataFrame(leaderboard_data)
        st.table(leaderboard_df)
        st.markdown("</div>", unsafe_allow_html=True)
    
   
    
    # Create a centered container for the history form
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col2:
         # Team Betting History Section (Public)
        st.markdown("""
        <div style="background-color: #313244; border-radius: 8px; padding: .5rem; margin-top: 5rem; margin-bottom: 1rem; border: 2px solid #45475a;">
        <h2 class='section-header'>📜 Team Betting History</h2>
        """, unsafe_allow_html=True)
        
        # Create a form for team history selection
        with st.form(key="history_form"):
            # Team selection for history
            history_team = st.selectbox("Select Team to View History", team_options, key="history_team")
            
            # Submit button with matching green color
            submit_button = st.form_submit_button(label="View History")
    
    # Only process history when the form is submitted
    if submit_button:
        # Get team history
        history_data = get_team_history(history_team)
        
        # Get pending bets
        try:
            with open("data/bets.json") as f:
                all_bets = json.load(f)
            
            pending_bets = [bet for bet in all_bets 
                            if bet["team"] == history_team and bet["status"] == "pending"]
            pending_bets_amount = sum(bet["amount"] for bet in pending_bets)
        except Exception as e:
            pending_bets = []
            pending_bets_amount = 0
            st.error(f"Error calculating pending bets: {str(e)}")
        
        col1, col2, col3 = st.columns([2, 4, 2])
        
        with col2:
            if isinstance(history_data, dict) and "error" in history_data:
                st.error(history_data["error"])
            elif isinstance(history_data, list) or (isinstance(history_data, dict) and "history" in history_data):
                # Get current team balance and home team
                current_team = next((t for t in teams if t["team"] == history_team), None)
                current_balance = current_team["balance"] if current_team else 0
                home_team = current_team.get("home_team", "") if current_team else ""
                
                # Starting balance for history calculation (current balance)
                starting_balance = current_balance
                
                # Create a DataFrame for the history
                history_entries = []
                running_balance = starting_balance
                
                # Add pending bets to history entries
                for bet in pending_bets:
                    try:
                        # Get match details
                        with open("data/matches.json") as f:
                            matches = json.load(f)
                        match = next((m for m in matches if m["match_id"] == bet["match_id"]), None)
                        
                        if match:
                            # Determine if this was a home team bet
                            is_home_team_bet = bet.get("prediction", "") == home_team
                            home_team_display = home_team if is_home_team_bet else ""
                            
                            # For pending bets, the closing balance is the current balance
                            # The bet amount has already been deducted when the bet was placed
                            history_entries.append({
                                "Match": f"{match['team1']} vs {match['team2']}",
                                "Date": format_date(match.get("date", "")) or "N/A",
                                "Bet On": bet.get("prediction", "N/A"),
                                "Home Team": home_team_display,
                                "Amount": format_currency(bet["amount"]),
                                "Result": "PENDING",
                                "Winnings": "N/A",
                                "Closing Balance": format_currency(running_balance)
                            })
                    except Exception as e:
                        st.error(f"Error processing pending bet: {str(e)}")
                
                # Process completed bets in reverse order to calculate running balance
                history_list = history_data if isinstance(history_data, list) else history_data.get("history", [])
                sorted_history = sorted(history_list, 
                                       key=lambda x: x.get("date", ""), 
                                       reverse=True)
                
                # Add back pending bets amount to get the balance before pending bets
                running_balance_for_history = running_balance + pending_bets_amount
                
                for entry in sorted_history:
                    # Calculate balance change
                    balance_change = entry.get("balance_change", 0)
                    
                    # For display, we're going backwards in time
                    closing_balance = running_balance_for_history
                    running_balance_for_history -= balance_change
                    
                    # Format the result with color
                    result_status = "won" if entry.get("result") == "won" else "lost"
                    
                    # Determine if this was a home team bet
                    is_home_team_bet = entry.get("prediction", "") == home_team
                    home_team_display = home_team if is_home_team_bet else ""
                    
                    history_entries.append({
                        "Match": entry.get("match", "N/A"),
                        "Date": format_date(entry.get("date", "")) or "N/A",
                        "Bet On": entry.get("prediction", "N/A"),
                        "Home Team": home_team_display,
                        "Amount": format_currency(entry.get("bet_amount", 0)),
                        "Result": result_status.upper(),
                        "Winnings": format_currency(entry.get("winnings", 0)) if entry.get("result") == "won" else "N/A",
                        "Closing Balance": format_currency(closing_balance)
                    })
                
                # Display as a styled table if we have data
                if history_entries:
                    history_df = pd.DataFrame(history_entries)
                    
                    # Apply custom styling to the Result column
                    def highlight_result(val):
                        if val == "WON":
                            return 'color: #a6e3a1; font-weight: bold'
                        elif val == "LOST":
                            return 'color: #f38ba8; font-weight: bold'
                        elif val == "PENDING":
                            return 'color: #f9e2af; font-weight: bold'
                        return ''
                    
                    # Apply custom styling to the Home Team column
                    def highlight_home_team(val):
                        if val and val != "N/A":  # If there's a value (not empty or N/A)
                            return 'color: #a6e3a1; font-weight: bold'
                        return ''
                    
                    # Apply the styling
                    styled_history = history_df.style.applymap(highlight_result, subset=['Result'])
                    styled_history = styled_history.applymap(highlight_home_team, subset=['Home Team'])
                    
                    # Display pending bets information
                    if pending_bets_amount > 0:
                        st.markdown(f"""
                        <div class='info-box'>
                            <p>Note: <strong>{format_currency(pending_bets_amount)}</strong> is currently tied up in pending bets</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.table(styled_history)
                else:
                    st.markdown("<div class='warning-box'>No betting history available for this team.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='warning-box'>No betting history available for this team.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Protected sections - only show if authenticated
    if st.session_state.authenticated:
        # Place Bet Section (Protected)
           # Create a centered container for the betting form
        col1, col2, col3 = st.columns([2, 4, 2])
        
        with col2:
            st.markdown("""
            <div style="background-color: #313244; border-radius: 8px; padding: .5rem; margin-bottom: 1rem; margin-top: 5rem; border: 2px solid #45475a;">
            <h2 class='section-header'>💰 Place Bet</h2>
            """, unsafe_allow_html=True)
            # st.markdown("<h2 class='section-header'></h2>", unsafe_allow_html=True)
            
            # Team selection
            team_options = [t["team"] for t in teams]
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
        
        
        # Create a centered container for the update result form
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
            
            # Update result button - now it just sets the confirmation state
            if st.button("Update Result") and match_result_id and winner_team:
                st.session_state.confirm_update = True
                st.session_state.confirm_match_id = match_result_id
                st.session_state.confirm_winner = winner_team
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
