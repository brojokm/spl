import json
from core.excel_storage import backup_to_excel

def update_result(match_id, winner):
    # Validate winner is not empty
    if not winner or winner.strip() == "":
        return "Winner team name cannot be empty."
    
    try:
        # Load data from JSON
        with open("data/matches.json") as f:
            matches = json.load(f)
        
        # Handle empty or invalid bets.json file
        try:
            with open("data/bets.json") as f:
                bets = json.load(f)
        except json.JSONDecodeError:
            bets = []
            
        with open("data/teams.json") as f:
            teams = json.load(f)

        match = next((m for m in matches if m["match_id"] == match_id), None)
        if not match:
            return f"Match ID {match_id} not found."
            
        # Validate winner is one of the teams in the match
        if winner not in [match["team1"], match["team2"]]:
            return f"Winner must be either {match['team1']} or {match['team2']}."

        match["winner"] = winner

        # Process bets
        for bet in bets:
            if bet["match_id"] == match_id and bet["status"] == "pending":
                team = next((t for t in teams if t["team"] == bet["team"]), None)
                if not team:
                    continue  # Skip if team not found
                    
                if bet["prediction"] == winner:
                    # If the prediction is correct:
                    # For home team: Add 4x bet amount to balance
                    # For non-home team: Add 2x bet amount to balance
                    multiplier = 4 if bet["is_home_team"] else 2
                    winnings = bet["amount"] * multiplier
                    bet["status"] = "won"
                    bet["winnings"] = winnings
                    
                    # Add winnings to team balance
                    # Since we already deducted the bet amount when placing the bet,
                    # we need to add the full winnings amount
                    team["balance"] += winnings
                else:
                    bet["status"] = "lost"
                    bet["winnings"] = 0
                    # No need to deduct the bet amount again as it was already deducted when placing the bet

        # Save updated data to JSON
        with open("data/matches.json", "w") as f:
            json.dump(matches, f, indent=2)
        with open("data/bets.json", "w") as f:
            json.dump(bets, f, indent=2)
        with open("data/teams.json", "w") as f:
            json.dump(teams, f, indent=2)
        
        # Backup to Excel
        backup_to_excel()

        return f"Match {match_id} result updated. Winner: {winner}"
        
    except Exception as e:
        return f"Error updating result: {str(e)}"