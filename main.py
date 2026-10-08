import sqlite3
import data
import nflreadpy as nfl



# CHANGE TO CURRENT NFL SEASON
SEASON = 2026



def updateTeams():
    con = sqlite3.connect("nfl.db")
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS teams(
        abbr TEXT UNIQUE,
        city TEXT,
        name TEXT,
        conference TEXT,
        division TEXT,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        ties INTEGER DEFAULT 0
    )
    """)
    
    cur.executemany("INSERT OR IGNORE INTO teams (abbr, city, name, conference, division) VALUES(?,?,?,?,?)", data.TEAMS)


    games = nfl.load_schedules(seasons=SEASON)
    results = {}

    for game in games.iter_rows(named=True):
        if game["home_score"] is None:
            continue

        for team in (game["home_team"], game["away_team"]):
            if team not in results:
                results[team] = {"wins": 0, "losses": 0, "ties": 0}


        if game["home_score"] > game["away_score"]:
            results[game["home_team"]]["wins"]+=1
            results[game["away_team"]]["losses"]+=1
        if game["home_score"] < game["away_score"]:
            results[game["away_team"]]["wins"]+=1
            results[game["home_team"]]["losses"]+=1
        if game["home_score"] == game["away_score"]:
            results[game["home_team"]]["ties"]+=1
            results[game["away_team"]]["ties"]+=1



    for abbr, r in results.items():
        cur.execute(
            "UPDATE teams SET wins = ?, losses = ?, ties = ? WHERE abbr = ?",
            (r["wins"], r["losses"], r["ties"], abbr),
        )

    con.commit()
    con.close()


def updatePlayers():
    con = sqlite3.connect("nfl.db")
    cur = con.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS players(
        player_id TEXT PRIMARY KEY,
        name TEXT,
        position TEXT,
        team TEXT,
        jersey_number INTEGER,
        status TEXT
    )
    """)

    players = nfl.load_rosters(seasons=SEASON)
    for player in players.iter_rows(named=True):
        if player["gsis_id"] is None:
            continue


        cur.execute(
            "INSERT OR REPLACE INTO players VALUES(?,?,?,?,?,?)",
            (
                player["gsis_id"],
                player["full_name"],
                player["position"],
                player["team"],
                player["jersey_number"],
                player["status"]
            ),
        )

    con.commit()
    con.close()


def createDatabase():
    updateTeams()
    updatePlayers()







def main():
    createDatabase()



main()