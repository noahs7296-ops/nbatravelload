# %%
import pandas
from pathlib import Path

arenas_url = "https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/arenas.csv"
arenas = pandas.read_csv(arenas_url)

wins_list = []
losses_list=[]
total_distance_list = []
total_tzs_list = []

repo = Path(r"C:\Users\noahs\nbatravelload")

for team in arenas["home_team"]:
    wins = 0
    losses = 0
    total_distance = 0 
    total_tzs = 0

    df = pandas.read_csv(repo / "2526gamelogs" / f"{team}_games_2526_merged.csv")

    for index, gm in df.iterrows():
        if team == gm["winner_x"]:
            wins += 1
        else:
            losses += 1
        total_distance += gm["distance_miles"]
        total_tzs += abs(gm["tzs_traveled"])

    wins_list.append(wins)
    losses_list.append(losses)
    total_distance_list.append(total_distance)
    total_tzs_list.append(total_tzs)
    
df_final_dict = dict(team=arenas["home_team"], wins=wins_list, losses=losses_list, total_distance=total_distance_list, total_tzs=total_tzs_list)
df_final = pandas.DataFrame(df_final_dict)

output_dir = Path("")
output_dir.mkdir(exist_ok=True)
df_final.to_csv(output_dir / f"total_travel_numbers.csv", index=False)



