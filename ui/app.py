import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
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

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

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

# Set page configuration
st.set_page_config(
    page_title="SPL Betting Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for responsive design with table text color fixes
st.markdown("""
<style>
    /* Base theme */
    .stApp {
        background-color: #1e1e2e;
        color: #e0e0e0;
    }
    
    /* Responsive sidebar */
    [data-testid="stSidebar"] {
        min-width: min(30vw, 130px) !important;
        max-width: min(30vw, 330px) !important;
    }
    
    /* Headers with responsive font sizes */
    .main-header {
        font-size: clamp(1.5rem, 2.5vw, 2rem);
        color: #89b4fa;
        text-align: center;
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid #313244;
    }
    
    .section-header {
        font-size: clamp(1.2rem, 2vw, 1.5rem);
        color: #89b4fa;
        margin-top: 1.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #313244;
    }
    
    /* Boxes */
    .info-box, .success-box, .warning-box, .match-details {
        margin-bottom: 0.8rem;
    }
    
    /* Responsive buttons */
    .stButton button {
        background-color: #128306;
        color: #1e1e2e;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.4rem 0.8rem;
        width: auto !important;
        min-width: 120px;
        max-width: 200px;
        margin: 0 auto;
        display: block;
    }
    
    .stButton button:hover {
        background-color: #16a108;
    }
    
    /* Text highlights with responsive sizing */
    .team-balance {
        font-size: clamp(1rem, 1.5vw, 1.3rem);
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
    
    /* TABLE TEXT COLOR FIXES - DARK THEME */
    /* Force white text for all tables in dark theme */
    .stApp[data-theme="dark"] table,
    .stApp[data-theme="dark"] th,
    .stApp[data-theme="dark"] td,
    .stApp[data-theme="dark"] tr {
        color: white !important;
    }
    
    .stApp[data-theme="dark"] .dataframe {
        color: white !important;
    }
    
    .stApp[data-theme="dark"] .dataframe th {
        background-color: #45475a !important;
        color: white !important;
        padding: 0.4rem !important;
    }
    
    .stApp[data-theme="dark"] .dataframe td {
        background-color: #313244 !important;
        color: white !important;
        padding: 0.4rem !important;
    }
    
    /* TABLE TEXT COLOR FIXES - LIGHT THEME */
    /* Force dark text for all tables in light theme */
    .stApp[data-theme="light"] table,
    .stApp[data-theme="light"] th,
    .stApp[data-theme="light"] td,
    .stApp[data-theme="light"] tr {
        color: #333333 !important;
    }
    
    .stApp[data-theme="light"] .dataframe {
        color: #333333 !important;
    }
    
    .stApp[data-theme="light"] .dataframe th {
        background-color: #c1c8e4 !important;
        color: #333333 !important;
        padding: 0.4rem !important;
    }
    
    .stApp[data-theme="light"] .dataframe td {
        background-color: #e8eaf6 !important;
        color: #333333 !important;
        padding: 0.4rem !important;
    }
    
    /* Fix for any text inside table cells */
    .stApp[data-theme="dark"] td div,
    .stApp[data-theme="dark"] th div,
    .stApp[data-theme="dark"] td span,
    .stApp[data-theme="dark"] th span,
    .stApp[data-theme="dark"] td p,
    .stApp[data-theme="dark"] th p {
        color: white !important;
    }
    
    .stApp[data-theme="light"] td div,
    .stApp[data-theme="light"] th div,
    .stApp[data-theme="light"] td span,
    .stApp[data-theme="light"] th span,
    .stApp[data-theme="light"] td p,
    .stApp[data-theme="light"] th p {
        color: #333333 !important;
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
        max-width: 90%;
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
    
    /* Fix for light theme history */
    [data-theme="light"] .history-won {
        color: #388e3c !important;
    }
    
    [data-theme="light"] .history-lost {
        color: #d32f2f !important;
    }
    
    /* Form container */
    .form-container {
        background-color: #313244;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem auto;
        max-width: 90%;
    }
    
    /* Fix for light theme form container */
    [data-theme="light"] .form-container {
        background-color: #e8eaf6;
        border: 1px solid #c5cae9;
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
    
    /* Fix for light theme section box */
    [data-theme="light"] .section-box {
        background-color: #e8eaf6;
        border: 1px solid #c5cae9;
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
    
    /* Admin page link */
    .admin-link {
        margin-top: 20px;
        padding: 10px;
        background-color: #313244;
        border-radius: 5px;
        text-align: center;
    }
    
    .admin-link a {
        color: #89b4fa;
        text-decoration: none;
        font-weight: bold;
    }
    
    .admin-link a:hover {
        text-decoration: underline;
    }
    
    /* Fix for light theme admin link */
    [data-theme="light"] .admin-link {
        background-color: #e8eaf6;
    }
    
    [data-theme="light"] .admin-link a {
        color: #3949ab;
    }
    
    /* Override for sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        width: 100% !important;
        margin: 5px 0 !important;
    }
    
    /* Responsive column layout */
    .stHorizontalBlock {
        flex-wrap: wrap;
    }
    
    /* Ensure tables are scrollable when needed */
    div:has(> .dataframe) {
        overflow-x: auto;
    }
    
    /* Match card styling */
    .match-card {
        background-color: #313244;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #45475a;
    }
    
    /* Fix for light theme match card */
    [data-theme="light"] .match-card {
        background-color: #e8eaf6;
        border: 1px solid #c5cae9;
    }
    
    /* Team name styling */
    .team-name {
        font-weight: bold;
        font-size: clamp(0.9rem, 1.2vw, 1.1rem);
    }
    
    /* Match date styling */
    .match-date {
        font-size: clamp(0.8rem, 1vw, 0.9rem);
        color: #cdd6f4;
    }
    
    /* Fix for light theme match date */
    [data-theme="light"] .match-date {
        color: #5c6bc0;
    }
    
    /* Bet amount styling */
    .bet-amount {
        font-weight: bold;
        color: #f9e2af;
    }
    
    /* Fix for light theme bet amount */
    [data-theme="light"] .bet-amount {
        color: #ff9800;
    }
    
    /* FORCE WHITE TEXT FOR ALL TABLES REGARDLESS OF THEME */
    table,
    th,
    td,
    tr,
    .dataframe,
    .dataframe th,
    .dataframe td,
    .stTable,
    .stDataFrame {
        color: white !important;
    }
    
    /* Force white text for all elements inside tables */
    td div,
    th div,
    td span,
    th span,
    td p,
    th p {
        color: white !important;
    }
    
    /* Target Streamlit's internal table styling */
    [data-testid="stTable"] {
        color: white !important;
    }
    
    /* Override any inherited styles */
    .dataframe * {
        color: white !important;
    }
    
    /* Ensure all text in tables is visible */
    .stTable * {
        color: white !important;
    }
    
    /* Force white text for all tables in dark theme */
    .stApp[data-theme="dark"] .dataframe,
    .stApp[data-theme="dark"] .dataframe th,
    .stApp[data-theme="dark"] .dataframe td,
    .stApp[data-theme="dark"] .dataframe div,
    .stApp[data-theme="dark"] .stTable,
    .stApp[data-theme="dark"] .stDataFrame {
        color: white !important;
    }
    
    /* Force dark text for all tables in light theme */
    .stApp[data-theme="light"] .dataframe,
    .stApp[data-theme="light"] .dataframe th,
    .stApp[data-theme="light"] .dataframe td,
    .stApp[data-theme="light"] .dataframe div,
    .stApp[data-theme="light"] .stTable,
    .stApp[data-theme="light"] .stDataFrame {
        color: #333333 !important;
    }
    
    /* Additional specific selectors for Streamlit's table elements */
    .stApp[data-theme="light"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] {
        color: #333333 !important;
    }
    
    .stApp[data-theme="dark"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] {
        color: white !important;
    }
    
    /* Target the text directly */
    .stApp[data-theme="light"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] p,
    .stApp[data-theme="light"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] span {
        color: #333333 !important;
    }
    
    .stApp[data-theme="dark"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] p,
    .stApp[data-theme="dark"] [data-testid="StyledFullScreenFrame"] div[data-testid="stTable"] span {
        color: white !important;
    }
    
    /* Ensure all text in tables is visible regardless of theme */
    .stTable * {
        color: inherit !important;
    }
    
    /* EXCEPTION FOR WON/LOST TEXT */
    td[data-text="WON"], 
    .dataframe td[data-text="WON"],
    td div:contains("WON"),
    td span:contains("WON") {
        color: #00ff00 !important;  /* Bright green */
        font-weight: bold !important;
    }

    td[data-text="LOST"], 
    .dataframe td[data-text="LOST"],
    td div:contains("LOST"),
    td span:contains("LOST") {
        color: #ff0000 !important;  /* Bright red */
        font-weight: bold !important;
    }

    td[data-text="PENDING"], 
    .dataframe td[data-text="PENDING"],
    td div:contains("PENDING"),
    td span:contains("PENDING") {
        color: #ffff00 !important;  /* Bright yellow */
        font-weight: bold !important;
    }

    /* Add this after your existing table styling */
    /* Override for specific result values */
    .dataframe td:has(> div:contains("WON")) * {
        color: #00ff00 !important;
    }

    .dataframe td:has(> div:contains("LOST")) * {
        color: #ff0000 !important;
    }

    .dataframe td:has(> div:contains("PENDING")) * {
        color: #ffff00 !important;
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

# Load data
teams, matches, bets = load_data()

# Create team options for dropdowns
team_options = [team["team"] for team in teams]

# Create a container for centered content
with st.container():
    # Leaderboard Section (Public)
    
    # Create a centered container for the leaderboard
    col1, col2, col3 = st.columns([1, 4, 1])
    
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
    col1, col2, col3 = st.columns([1, 4, 1])
    
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
        
        col1, col2, col3 = st.columns([1, 4, 1])
        
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
                            return 'color: #00ff00 !important; font-weight: bold'  # Bright green with !important
                        elif val == "LOST":
                            return 'color: #ff0000 !important; font-weight: bold'  # Bright red with !important
                        elif val == "PENDING":
                            return 'color: #ffff00 !important; font-weight: bold'  # Bright yellow with !important
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
