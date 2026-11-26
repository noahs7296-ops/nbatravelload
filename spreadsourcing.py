# %%
%pip install nba_api pandas

# %%
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog, teamgamelogs
import pandas
from pathlib import Path

logs = teamgamelogs.TeamGameLogs(
    season_nullable='2025-26',
    season_type_nullable='Regular Season',
    measure_type_player_game_logs_nullable='Advanced'
)

tmgmlogs = logs.get_data_frames()
tmgmlogs = tmgmlogs[0]
tmgmlogs['home'] = tmgmlogs['MATCHUP'].apply(lambda x: 'home' if '@' not in x else 'away')
tmgmlogs['home_team'] = tmgmlogs.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'home' else x['MATCHUP'].split(' ')[-1], axis=1)
tmgmlogs['away_team'] = tmgmlogs.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'away' else x['MATCHUP'].split(' ')[-1], axis=1)

neutral_mask = tmgmlogs.groupby('GAME_ID')['home'].transform(
    lambda values: len(values) == 2 and values.eq('away').all()
)

team_pairs = tmgmlogs.groupby('GAME_ID')['TEAM_ABBREVIATION'].agg(
    lambda values: sorted(values.unique())
)

tmgmlogs.loc[neutral_mask, 'home_team'] = (
    tmgmlogs.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[0])
)
tmgmlogs.loc[neutral_mask, 'away_team'] = (
    tmgmlogs.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[1])
)

tmgmlogs = tmgmlogs.drop(columns=['home', 'MATCHUP'])
tmgmlogs = tmgmlogs[['home_team', 'away_team', 'GAME_DATE', 'POSS']].drop_duplicates()

logs2 = teamgamelogs.TeamGameLogs(
    season_nullable='2025-26',
    season_type_nullable='Regular Season',
    measure_type_player_game_logs_nullable='Base'
)

tmgmlogsstd = logs2.get_data_frames()
tmgmlogsstd = tmgmlogsstd[0]
tmgmlogsstd['home'] = tmgmlogsstd['MATCHUP'].apply(lambda x: 'home' if '@' not in x else 'away')
tmgmlogsstd['home_team'] = tmgmlogsstd.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'home' else x['MATCHUP'].split(' ')[-1], axis=1)
tmgmlogsstd['away_team'] = tmgmlogsstd.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'away' else x['MATCHUP'].split(' ')[-1], axis=1)

neutral_mask = tmgmlogsstd.groupby('GAME_ID')['home'].transform(
    lambda values: len(values) == 2 and values.eq('away').all()
)

team_pairs = tmgmlogsstd.groupby('GAME_ID')['TEAM_ABBREVIATION'].agg(
    lambda values: sorted(values.unique())
)

tmgmlogsstd.loc[neutral_mask, 'home_team'] = (
    tmgmlogsstd.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[0])
)
tmgmlogsstd.loc[neutral_mask, 'away_team'] = (
    tmgmlogsstd.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[1])
)

tmgmlogsstd = tmgmlogsstd.drop(columns=['home', 'MATCHUP'])
spreads = []
for gm, row in tmgmlogsstd.iterrows():
    if row["home_team"] == row["TEAM_ABBREVIATION"] and row["WL"] == "W":
        spreads.append(row["PLUS_MINUS"])
    elif row["away_team"] == row["TEAM_ABBREVIATION"] and row["WL"] == "L":
        spreads.append(row["PLUS_MINUS"])
    elif row["home_team"] == row["TEAM_ABBREVIATION"] and row["WL"] == "L":
        spreads.append(-row["PLUS_MINUS"])
    else:
        spreads.append(-row["PLUS_MINUS"])
tmgmlogsstd["spread"] = spreads
tmgmlogsstd = tmgmlogsstd[['home_team', 'away_team', 'GAME_DATE', 'spread']].drop_duplicates()

tm_ratings_url = "https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/teamratings.csv"
tm_ratings = pandas.read_csv(tm_ratings_url)

for team in tm_ratings["team"]:
    url = f"https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/2526gamelogs/{team}_games_2526.csv"
    gmlog = pandas.read_csv(url)

    ortg = []
    drtg = []
    opp_ortg = []
    opp_drtg = []
    for index, row in gmlog.iterrows():
        if gmlog.at[index, 'home_team'] == team:
            goodguys = tm_ratings.loc[tm_ratings["team"] == row["home_team"]].iloc[0]
            ortg.append(goodguys["ortg"])
            drtg.append(goodguys["drtg"])
            badguys = tm_ratings.loc[tm_ratings["team"] == row["away_team"]].iloc[0]
            opp_ortg.append(badguys["ortg"])
            opp_drtg.append(badguys["drtg"])
        else:
            goodguys = tm_ratings.loc[tm_ratings["team"] == row["away_team"]].iloc[0]
            ortg.append(goodguys["ortg"])
            drtg.append(goodguys["drtg"])
            badguys = tm_ratings.loc[tm_ratings["team"] == row["home_team"]].iloc[0]
            opp_ortg.append(badguys["ortg"])
            opp_drtg.append(badguys["drtg"])

    gmlog["ortg"] = ortg
    gmlog["drtg"] = drtg
    gmlog["opp_ortg"] = opp_ortg
    gmlog["opp_drtg"] = opp_drtg
    gmlog["exp_spread_per_100"] = (gmlog["ortg"] + gmlog["opp_drtg"])/2 - (gmlog["drtg"] + gmlog["opp_ortg"])/2
    gmlog = gmlog.merge(tmgmlogs, on=["home_team", "away_team", "GAME_DATE"], how="left", suffixes=("", "_game"))
    gmlog["exp_spread"] = round(gmlog["exp_spread_per_100"] * gmlog["POSS"] / 100, 2)
    gmlog = gmlog.merge(tmgmlogsstd, on=["home_team", "away_team", "GAME_DATE"], how="left")
    gmlog = gmlog.drop_duplicates(subset=["home_team", "away_team", "GAME_DATE"])
    perspectived_spreads = []
    for gm, row in gmlog.iterrows():
        if team == row['away_team']:
           perspectived_spreads.append(-row["spread"])
        else:
           perspectived_spreads.append(row["spread"])
    gmlog["spread"] = perspectived_spreads
    gmlog["spread_diff"] = round(gmlog["spread"] - gmlog["exp_spread"], 2)

    output_dir = Path("2526gamelogs")
    output_dir.mkdir(exist_ok=True)
    gmlog.to_csv(output_dir / f"{team}_games_2526.csv", index=False)
    print(f"Saved {team} game logs")
    

    








