import pandas as pd
import os
from datetime import datetime
import json
import warnings

# Define Excel file paths
EXCEL_DIR = "data/excel"
TEAMS_EXCEL = os.path.join(EXCEL_DIR, "teams.xlsx")
MATCHES_EXCEL = os.path.join(EXCEL_DIR, "matches.xlsx")
BETS_EXCEL = os.path.join(EXCEL_DIR, "bets.xlsx")

# Ensure Excel directory exists
os.makedirs(EXCEL_DIR, exist_ok=True)

# Check if openpyxl is available
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    warnings.warn("openpyxl not installed. Excel backup will be disabled. Install with 'pip install openpyxl'")

def init_excel_files():
    """Initialize Excel files if they don't exist"""
    if not EXCEL_AVAILABLE:
        return
    
    # Teams Excel
    if not os.path.exists(TEAMS_EXCEL):
        # Load from JSON if available
        try:
            with open("data/teams.json") as f:
                teams = json.load(f)
            df_teams = pd.DataFrame(teams)
        except:
            df_teams = pd.DataFrame(columns=["team", "balance", "home_team"])
        df_teams.to_excel(TEAMS_EXCEL, index=False)
    
    # Matches Excel
    if not os.path.exists(MATCHES_EXCEL):
        try:
            with open("data/matches.json") as f:
                matches = json.load(f)
            df_matches = pd.DataFrame(matches)
            # Reorder columns to put venue at the end
            if "venue" in df_matches.columns and "winner" in df_matches.columns:
                cols = [col for col in df_matches.columns if col not in ["venue", "winner"]]
                cols = cols + ["winner", "venue"]
                df_matches = df_matches[cols]
        except:
            df_matches = pd.DataFrame(columns=["match_id", "date", "team1", "team2", "winner", "venue"])
        df_matches.to_excel(MATCHES_EXCEL, index=False)
    
    # Bets Excel
    if not os.path.exists(BETS_EXCEL):
        try:
            with open("data/bets.json") as f:
                bets = json.load(f)
            df_bets = pd.DataFrame(bets)
        except:
            df_bets = pd.DataFrame(columns=["match_id", "team", "prediction", "amount", 
                                           "is_home_team", "status", "winnings", "timestamp"])
        df_bets.to_excel(BETS_EXCEL, index=False)

def backup_to_excel():
    """Backup all JSON data to Excel files"""
    if not EXCEL_AVAILABLE:
        return
    
    # Backup teams
    try:
        with open("data/teams.json") as f:
            teams = json.load(f)
        df_teams = pd.DataFrame(teams)
        df_teams.to_excel(TEAMS_EXCEL, index=False)
    except Exception as e:
        warnings.warn(f"Failed to backup teams to Excel: {str(e)}")
    
    # Backup matches
    try:
        with open("data/matches.json") as f:
            matches = json.load(f)
        df_matches = pd.DataFrame(matches)
        
        # Reorder columns to put venue at the end after winner
        if "venue" in df_matches.columns and "winner" in df_matches.columns:
            cols = [col for col in df_matches.columns if col not in ["venue", "winner"]]
            cols = cols + ["winner", "venue"]
            df_matches = df_matches[cols]
            
        df_matches.to_excel(MATCHES_EXCEL, index=False)
    except Exception as e:
        warnings.warn(f"Failed to backup matches to Excel: {str(e)}")
    
    # Backup bets
    try:
        with open("data/bets.json") as f:
            bets = json.load(f)
        df_bets = pd.DataFrame(bets)
        df_bets.to_excel(BETS_EXCEL, index=False)
    except Exception as e:
        warnings.warn(f"Failed to backup bets to Excel: {str(e)}")

def load_teams_excel():
    """Load teams data from Excel"""
    if not EXCEL_AVAILABLE:
        with open("data/teams.json") as f:
            return json.load(f)
            
    if not os.path.exists(TEAMS_EXCEL):
        init_excel_files()
    df = pd.read_excel(TEAMS_EXCEL)
    return df.to_dict('records')

def load_matches_excel():
    """Load matches data from Excel"""
    if not EXCEL_AVAILABLE:
        with open("data/matches.json") as f:
            return json.load(f)
            
    if not os.path.exists(MATCHES_EXCEL):
        init_excel_files()
    df = pd.read_excel(MATCHES_EXCEL)
    # Convert NaN to None for winner column
    df['winner'] = df['winner'].where(pd.notna(df['winner']), None)
    return df.to_dict('records')

def load_bets_excel():
    """Load bets data from Excel"""
    if not EXCEL_AVAILABLE:
        try:
            with open("data/bets.json") as f:
                return json.load(f)
        except:
            return []
            
    if not os.path.exists(BETS_EXCEL):
        init_excel_files()
    df = pd.read_excel(BETS_EXCEL)
    return df.to_dict('records')

def save_teams_excel(teams):
    """Save teams data to Excel"""
    if not EXCEL_AVAILABLE:
        return
        
    df = pd.DataFrame(teams)
    df.to_excel(TEAMS_EXCEL, index=False)

def save_matches_excel(matches):
    """Save matches data to Excel"""
    if not EXCEL_AVAILABLE:
        return
        
    df = pd.DataFrame(matches)
    df.to_excel(MATCHES_EXCEL, index=False)

def save_bets_excel(bets):
    """Save bets data to Excel"""
    if not EXCEL_AVAILABLE:
        return
        
    df = pd.DataFrame(bets)
    df.to_excel(BETS_EXCEL, index=False) 