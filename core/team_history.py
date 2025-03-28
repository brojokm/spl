import json
from datetime import datetime

def get_team_history(team_name):
    """
    Get the betting history and balance changes for a specific team.
    Returns a list of bets and their outcomes, along with balance changes.
    """
    try:
        # Load data from JSON
        with open("data/teams.json") as f:
            teams = json.load(f)
        with open("data/matches.json") as f:
            matches = json.load(f)
        with open("data/bets.json") as f:
            bets = json.load(f)
            
        # Get team info
        team_info = next((t for t in teams if t["team"] == team_name), None)
        if not team_info:
            return {"error": f"Team {team_name} not found."}
            
        # Get all bets for this team
        team_bets = [b for b in bets if b["team"] == team_name]
        
        # Sort bets by timestamp
        team_bets.sort(key=lambda x: x.get("timestamp", ""))
        
        # Create history entries
        history = []
        
        for bet in team_bets:
            match_id = bet["match_id"]
            match = next((m for m in matches if m["match_id"] == match_id), None)
            
            if not match:
                continue
                
            # Only include completed matches
            if not match.get("winner"):
                continue
                
            # Create history entry
            entry = {
                "match_id": match_id,
                "match": f"{match['team1']} vs {match['team2']}",
                "date": match.get("date", ""),
                "bet_amount": bet["amount"],
                "prediction": bet["prediction"],
                "actual_winner": match["winner"],
                "result": bet["status"],
                "winnings": bet.get("winnings", 0),
                "balance_change": bet.get("winnings", 0) - bet["amount"] if bet["status"] == "won" else -bet["amount"]
            }
            
            history.append(entry)
            
        return {
            "team": team_name,
            "current_balance": team_info["balance"],
            "home_team": team_info.get("home_team", ""),
            "history": history
        }
        
    except Exception as e:
        return {"error": f"Error retrieving team history: {str(e)}"}