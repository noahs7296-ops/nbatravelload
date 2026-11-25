pip install nba_api pandas
 
import pandas from numpy
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog, teamgamelogs
# Pulls all games across the entire league for the season if team_id_nullable is omitted
logs = teamgamelogs.TeamGameLogs(
    season_nullable='2025-26',
    season_type_nullable='Regular Season',
    measure_type_player_game_logs_nullable='Base',  # Options: 'Base', 'Advanced', 'Misc', 'Four Factors', 'Scoring', 'Opponent'
    location_nullable='',  # Optional: 'Home' or 'Road'
    last_n_games_nullable=''  # Optional: e.g., '10'
)

df_all = logs.get_data_frames()[0]
print(df_all[['TEAM_ABBREVIATION', 'GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'PLUS_MINUS']].head())
