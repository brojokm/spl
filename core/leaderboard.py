import json
from core.excel_storage import load_teams_excel

def format_currency(amount):
    """Format amount in Indian currency format (Lakhs and Crores)"""
    if amount >= 10000000:  # 1 Crore = 10,000,000
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh = 100,000
        return f"₹{amount/100000:.2f} Lakh"
    else:
        return f"₹{amount:,}"

def get_leaderboard():
    # Get data from JSON
    with open("data/teams.json") as f:
        teams = json.load(f)
    
    # Sort by balance in descending order
    leaderboard = sorted(teams, key=lambda x: x["balance"], reverse=True)
    return leaderboard

def get_leaderboard_excel():
    # Get data from Excel
    teams = load_teams_excel()
    
    # Sort by balance in descending order
    leaderboard = sorted(teams, key=lambda x: x["balance"], reverse=True)
    return leaderboard