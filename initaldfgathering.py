# %%
%pip install nba_api pandas

# %%
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog, teamgamelogs
import pandas
from pathlib import Path

# Pulls all games across the entire league for the season if team_id_nullable is omitted
logs = teamgamelogs.TeamGameLogs(
    season_nullable='2025-26',
    season_type_nullable='Regular Season',
    measure_type_player_game_logs_nullable='Base'
)

gmlogdirty2526 = logs.get_data_frames()[0]
gmlogdirty2526['home'] = gmlogdirty2526['MATCHUP'].apply(lambda x: 'home' if '@' not in x else 'away')
gmlogdirty2526['home_team'] = gmlogdirty2526.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'home' else x['MATCHUP'].split(' ')[-1], axis=1)
gmlogdirty2526['away_team'] = gmlogdirty2526.apply(lambda x: x['TEAM_ABBREVIATION'] if x['home'] == 'away' else x['MATCHUP'].split(' ')[-1], axis=1)
# Both teams can be marked away at a neutral site. Give those games a consistent ordering so the later home/away merge matches both team rows.
neutral_mask = gmlogdirty2526.groupby('GAME_ID')['home'].transform(
    lambda values: len(values) == 2 and values.eq('away').all()
)

team_pairs = gmlogdirty2526.groupby('GAME_ID')['TEAM_ABBREVIATION'].agg(
    lambda values: sorted(values.unique())
)

gmlogdirty2526.loc[neutral_mask, 'home_team'] = (
    gmlogdirty2526.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[0])
)
gmlogdirty2526.loc[neutral_mask, 'away_team'] = (
    gmlogdirty2526.loc[neutral_mask, 'GAME_ID']
    .map(team_pairs)
    .map(lambda pair: pair[1])
)

# Use the winning team's own abbreviation, rather than inferring the winner
# from the home/away labels.
winners = gmlogdirty2526['TEAM_ABBREVIATION'].where(
    gmlogdirty2526['WL'].eq('W')
)
gmlogdirty2526['winner'] = winners.groupby(
    gmlogdirty2526['GAME_ID']
).transform('first')

gmlogclean2526 = gmlogdirty2526[['home_team', 'away_team', 'GAME_DATE']].drop_duplicates()
winner_by_game = (
    gmlogdirty2526.loc[
        gmlogdirty2526['WL'].eq('W'),
        ['GAME_DATE', 'home_team', 'away_team', 'TEAM_ABBREVIATION']
    ]
    .rename(columns={'TEAM_ABBREVIATION': 'winner'})
    .drop_duplicates(subset=['GAME_DATE', 'home_team', 'away_team'])
)

gmlogclean2526 = gmlogclean2526.merge(
    winner_by_game,
    on=['GAME_DATE', 'home_team', 'away_team'],
    how='left'
)

for team in gmlogclean2526['home_team'].unique():
    team_games2526 = {}

    for team in gmlogclean2526['home_team'].unique():
        team_games2526[team] = gmlogclean2526[
            (gmlogclean2526['home_team'] == team)
            | (gmlogclean2526['away_team'] == team)
        ]
    team_games2526[team] = team_games2526[team].drop_duplicates()
    team_games2526[team] = team_games2526[team].sort_values(by='GAME_DATE', ascending=False)
    team_games2526[team]['prev_home_team'] = team_games2526[team]['home_team'].shift(-1)
    for team_name in team_games2526:
        team_games2526[team_name] = (
            team_games2526[team_name]
            .sort_values(by='GAME_DATE', ascending=False)
            .copy()
        )
        team_games2526[team_name]['prev_home_team'] = (
            team_games2526[team_name]['home_team'].shift(-1)
        )
        team_games2526[team_name] = team_games2526[team_name].sort_values(by='GAME_DATE', ascending=True)

    output_dir.mkdir(parents=True, exist_ok=True)

    for team_name, team_df in team_games2526.items():
        team_df.to_csv(output_dir / f'{team_name}_games_2526.csv', index=False)

# %%
from math import asin, cos, radians, sin, sqrt

team_games = {
    file.stem.removesuffix("_games_2526"): pandas.read_csv(file)
    for file in output_dir.glob("*_games_2526.csv")
}
print(f"Loaded {len(team_games)} team CSVs")
arenas_url = "https://raw.githubusercontent.com/noahs7296-ops/nbatravelload/main/arenas.csv"
arenas = pandas.read_csv(arenas_url)

for log in team_games.keys():
    team_games[log]['GAME_DATE'] = pandas.to_datetime(team_games[log]['GAME_DATE'])
    team_games[log] = team_games[log].merge(arenas, left_on='home_team', right_on='home_team', how='left')
    team_games[log] = team_games[log].merge(arenas, left_on='prev_home_team', right_on='home_team', how='left', suffixes=('', '_prev'))

def haversine_miles(row):
    if pandas.isna(row['lat_prev']) or pandas.isna(row['long_prev']):
        return 0

    lat1, lon1 = radians(row['lat']), radians(row['long'])
    lat2, lon2 = radians(row['lat_prev']), radians(row['long_prev'])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 3959 * 2 * asin(sqrt(a))

for log in team_games.keys():
    team_games[log]['distance_miles'] = team_games[log].apply(haversine_miles, axis=1)

print(output_dir.resolve())




