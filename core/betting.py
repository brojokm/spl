import json
from datetime import datetime
from core.excel_storage import backup_to_excel
from core.github_storage import update_json_file, batch_update_github_files

def place_bet(team_name, match_id, prediction, amount):
    # Load data from JSON
    with open("data/teams.json") as f:
        teams = json.load(f)
    with open("data/matches.json") as f:
        matches = json.load(f)
    
    # Handle empty or invalid bets.json file
    try:
        with open("data/bets.json") as f:
            bets = json.load(f)
    except json.JSONDecodeError:
        bets = []

    match = next((m for m in matches if m["match_id"] == match_id), None)
    if not match:
        return f"Match ID {match_id} not found."

    team_info = next((t for t in teams if t["team"] == team_name), None)
    if not team_info:
        return f"Team {team_name} not registered."

    # Check if team has already placed a bet for this match
    existing_bet = next((b for b in bets if b["match_id"] == match_id and b["team"] == team_name), None)
    if existing_bet:
        return f"Your team has already placed a bet for match {match_id}."

    # Check if amount is in multiples of 5 lakhs (500,000)
    if amount % 500000 != 0:
        return "Bet amount must be in multiples of ₹5 Lakh"

    if team_info["balance"] < amount:
        return "Insufficient balance to place the bet."

    is_home_team = match["team1"] == team_info["home_team"] or match["team2"] == team_info["home_team"]
    if is_home_team and prediction != team_info["home_team"]:
        return f"Must bet on home team: {team_info['home_team']}"

    # Deduct the bet amount from the team's balance immediately
    team_info["balance"] -= amount

    new_bet = {
        "match_id": match_id,
        "team": team_name,
        "prediction": prediction,
        "amount": amount,
        "is_home_team": is_home_team,
        "status": "pending",
        "winnings": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    bets.append(new_bet)
    
    # Save to local files first
    with open("data/bets.json", "w") as f:
        json.dump(bets, f, indent=2)
    with open("data/teams.json", "w") as f:
        json.dump(teams, f, indent=2)
    
    # Update GitHub repository using batch update
    batch_update_github_files({
        "data/bets.json": bets,
        "data/teams.json": teams
    })
    
    # Backup to Excel
    backup_to_excel()
    
    return f"Bet placed successfully for {team_name} on match {match_id}."