# %%
import pandas
from pathlib import Path

arenas_url = "https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/arenas.csv"
arenas = pandas.read_csv(arenas_url)

for team in arenas["home_team"].unique():
    spreadurl = f"https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/2526gamelogs/{team}_games_2526.csv"
    distanceurl = f"https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/2526gamelogs/{team}_games_2526_wdistance.csv"
    spreaddf = pandas.read_csv(spreadurl)
    distancedf = pandas.read_csv(distanceurl)

    spreaddf["GAME_DATE"] = pandas.to_datetime(spreaddf["GAME_DATE"])
    distancedf["GAME_DATE"] = pandas.to_datetime(distancedf["GAME_DATE"])

    mergeddf = pandas.merge(spreaddf, distancedf, how="left", on=["home_team", "away_team", "GAME_DATE"])
    print(team, ": ", mergeddf.shape[0], " games")
    mergeddf = mergeddf.drop(columns=["winner_y"])
    
    output_dir = Path("2526gamelogs")
    output_dir.mkdir(exist_ok=True)
    mergeddf.to_csv(output_dir / f"{team}_games_2526_merged.csv", index=False)
    print(f"Saved {team} game logs")



