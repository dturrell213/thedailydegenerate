import json
from datetime import datetime
from pathlib import Path

# Files to backfill
files = [
    ("exports/ev_baseball_mlb_20260514_154100.json", "2026-05-14"),
    ("exports/ev_baseball_mlb_20260515_105922.json", "2026-05-15"),
]

tracker_path = Path("results/tracker.json")
with open(tracker_path) as f:
    tracker = json.load(f)

existing_ids = {p["pick_id"] for p in tracker["picks"]}
added = 0

for filepath, date in files:
    with open(filepath) as f:
        data = json.load(f)
    
    bets = data.get("value_bets", [])
    bets = [b for b in bets if abs(b.get("best_odds_american", 0)) <= 350]
    bets = sorted(bets, key=lambda x: x.get("edge_pp", 0), reverse=True)[:5]
    
    for bet in bets:
        pick_id = f"{date}_{bet.get('game','')}_{bet.get('team','')}"
        if pick_id in existing_ids:
            continue
        
        tracker["picks"].append({
            "pick_id": pick_id,
            "date": date,
            "logged_at": datetime.now().isoformat(),
            "result": "P",
            "settled_at": None,
            "sport": "baseball_mlb",
            "game": bet.get("game", ""),
            "team": bet.get("team", ""),
            "best_bookmaker": bet.get("best_bookmaker", ""),
            "best_odds": bet.get("best_odds", ""),
            "best_odds_american": bet.get("best_odds_american", 0),
            "book_implied_pct": bet.get("best_book_implied_pct", 0),
            "model_prob_pct": bet.get("model_prob_pct", 0),
            "edge_pp": bet.get("edge_pp", 0),
            "home_pitcher": bet.get("home_pitcher", ""),
            "away_pitcher": bet.get("away_pitcher", ""),
            "units_wagered": 1.0,
            "units_profit": None,
        })
        existing_ids.add(pick_id)
        added += 1
        print(f"Added: {bet.get('team')} {bet.get('best_odds')} on {date}")

with open(tracker_path, "w") as f:
    json.dump(tracker, f, indent=2)

print(f"\nAdded {added} picks. Now settling...")