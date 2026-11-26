# %%
import pandas
from pathlib import Path

arenas_url = "https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/arenas.csv"
arenas = pandas.read_csv(arenas_url)

for team in arenas["home_team"].unique():
    print(f"Processing team: {team}")
    url = f"https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/2526gamelogs/{team}_games_2526_wdistance.csv"
    tmlog = pandas.read_csv(url)
    tmlog["GAME_DATE"] = pandas.to_datetime(tmlog["GAME_DATE"])
    tmlog["distance_miles"] = tmlog["distance_miles"].fillna(0)
    tmlog["tzs_traveled"] = tmlog["tzs_traveled"].fillna(0)
    trailing_7daymiles_list = []
    trailing_14daymiles_list = []
    trailing_30daymiles_list = []
    trailing_7daytz_list = []
    trailing_14daytz_list = []
    trailing_30daytz_list = []

    for index, row in tmlog.iterrows():
        trailing_7daymiles = row["distance_miles"]
        trailing_14daymiles = row["distance_miles"]
        trailing_30daymiles = row["distance_miles"]
        trailing_7daytz = row["tzs_traveled"]
        trailing_14daytz = row["tzs_traveled"]
        trailing_30daytz = row["tzs_traveled"]
        current_date = row["GAME_DATE"]
        for index2, row2 in tmlog.iterrows():
            if row2["GAME_DATE"] < current_date:
                date_diff = (current_date - row2["GAME_DATE"]).days
                if date_diff <= 7:
                    trailing_7daymiles += row2["distance_miles"]
                    trailing_7daytz += abs(row2["tzs_traveled"])
                if date_diff <= 14:
                    trailing_14daymiles += row2["distance_miles"]
                    trailing_14daytz += abs(row2["tzs_traveled"])
                if date_diff <= 30:
                    trailing_30daymiles += row2["distance_miles"]
                    trailing_30daytz += abs(row2["tzs_traveled"])
        trailing_7daymiles_list.append(trailing_7daymiles)
        trailing_14daymiles_list.append(trailing_14daymiles)
        trailing_30daymiles_list.append(trailing_30daymiles)
        trailing_7daytz_list.append(trailing_7daytz)
        trailing_14daytz_list.append(trailing_14daytz)
        trailing_30daytz_list.append(trailing_30daytz)
    tmlog["trailing_7daymiles"] = trailing_7daymiles_list
    tmlog["trailing_14daymiles"] = trailing_14daymiles_list
    tmlog["trailing_30daymiles"] = trailing_30daymiles_list
    tmlog["trailing_7daytz"] = trailing_7daytz_list
    tmlog["trailing_14daytz"] = trailing_14daytz_list
    tmlog["trailing_30daytz"] = trailing_30daytz_list
    
    output_dir = Path("2526gamelogs")
    output_dir.mkdir(exist_ok=True)
    tmlog.to_csv(output_dir / f"{team}_games_2526_wdistance.csv", index=False)
    print(f"Saved {team} game logs")




