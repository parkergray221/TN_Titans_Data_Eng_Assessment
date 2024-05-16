# FOR EACH INDIVIDUAL GAME IN THE NFL 2021-2023 SEASON: 
# A) Get the date of that game. 
# B) Get the stadium that game is in (join Home_Team in Games.csv with Team(s) in Venue.csv then select the Geo column in Venues.csv, pass those values you meteo as latitude and longitude)
# C) Once given the day and the latitude/longitude, query however many interesting weather factoids we might want for these given days
# D) Output all of this into a pandas df that we then query separately with SQL.

# THEREFORE:
# The most relevant columns to select from Games.csv are Game_Date and Home_Team
# The most relevant columns from Venues.csv are Team(s) and Geo.
# But we may consider keeping other columns from Games and Venues because they may help us frame more interesting SQL queries (eg, how many games did the Home Team win in favorable vs unfavorable weather, and how might we define 'favorable' weather)
# Still, some columns are superfluous, such as Week or Start_Time (or at least they appear so at the time of writing)

import openmeteo_requests

import requests_cache
import pandas as pd
pd.options.mode.chained_assignment = None
from retry_requests import retry

# convert gmt offset provided by games.csv to strings that meteo can interpret.
gmt_dict = {0: 'Europe/London',  
            1: 'Europe/Berlin',
            -1: 'Europe/London',  # yeah i have two europe/london's but none of the stadiums in the venue or games csv's actually are located within the -1 timezone area so...
    		-5: 'America/New_York', 
            -6: 'America/Chicago', 
            -7: 'America/Denver', 
            -8: 'America/Los_Angeles'
            }

# initial df set up section
games = pd.read_csv('Games.csv',encoding='windows-1252')
venues = pd.read_csv('Venues.csv',encoding='windows-1252')

game_data = games[['Game_Date', 'Start_Time', 'Start_Time_GMT_Offset', 'Game_Site', 'Home_Team', 'Home_Team_Final_Score', 'Visit_Team', 'Visit_Team_Final_Score']]
# print(game_data)
game_data['Start_Time_GMT_Offset'].replace(gmt_dict, inplace=True)  # replace integers with useful strings.
game_data = game_data.replace(to_replace='Washington Football Team', value='Washington Commanders')  # addressing a mismatch with the initial data

team_locations = venues[['Surface', 'Roof_Type', 'Team(s)', 'Opened', 'Geo']]
# print(team_locations)
team_locations['Team(s)'] = team_locations['Team(s)'].str.split(', ')  # dealing with the LA/NY stadiums serving multiple teams
team_locations = team_locations.apply(pd.Series.explode) 

game_data_with_geo = pd.merge(game_data, team_locations, left_on='Home_Team', right_on='Team(s)', how='left').drop('Team(s)', axis=1)
# print(game_data_with_geo)
# separate latitude and longitude from geo to more discretely refer to them in meteo section.
game_data_with_geo['Latitude'] = game_data_with_geo['Geo'].str.split(',').str[0].astype(float)
game_data_with_geo['Longitude'] = game_data_with_geo['Geo'].str.split(',').str[1].astype(float)
game_data_with_geo = game_data_with_geo.drop('Geo', axis ='columns')
game_data_with_geo['Game_Date'] = pd.to_datetime(game_data_with_geo['Game_Date'], errors='coerce')  # change game_date column to datetime type for meteo submission
game_data_with_geo['Game_Date'] = game_data_with_geo['Game_Date'].dt.strftime('%Y-%m-%d')  # change datetime format for meteo submission
# print(game_data_with_geo)  # check geo column separation
# print(game_data_with_geo.dtypes)

# remainder of code is taken from meteo's API and modified when necesary to achieve our goals.
# first, generate the min max avg metrics tied to the day of a game at a specific lat/longitude.
# second, join the daily data to game_data_with_geo to create a final dataframe that contains relevant weather data about that particular day in that particular location.
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"

# create daily_dataframe before entering the for loop so we can concatenate each day's data to this df
daily_dataframe = pd.DataFrame(columns=['date', 'latitude', 'longitude', 'temperature_2m_max', "temperature_2m_min", "temperature_2m_mean", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max"])
print('beginning meteo api call')

for index, row in game_data_with_geo.iterrows():
    params = {   # set to the value of a given row in game_data_with_geo
        "latitude": row['Latitude'],  
        "longitude": row['Longitude'],
        "start_date": row['Game_Date'],  
        "end_date": row['Game_Date'],
	    "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max"],
        "temperature_unit": "fahrenheit",  # just using american metrics for my own sake.
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": row['Start_Time_GMT_Offset']  # despite attempts to match to the GMT offset provided by Games.csv, it doesn't seem to stick in the final meteo output date column for wahtever reason.
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_mean = daily.Variables(2).ValuesAsNumpy()
    daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
    daily_snowfall_sum = daily.Variables(4).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(5).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(6).ValuesAsNumpy()
    daily_wind_gusts_10m_max = daily.Variables(7).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["latitude"] = response.Latitude()
    daily_data["longitude"] = response.Longitude()
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
    daily_data["rain_sum"] = daily_rain_sum
    daily_data["snowfall_sum"] = daily_snowfall_sum
    daily_data["precipitation_hours"] = daily_precipitation_hours
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max

    single_day_df = pd.DataFrame(data = daily_data)
    daily_dataframe = pd.concat([daily_dataframe, single_day_df])

print("done with meteo api call")
#  print(daily_dataframe)  # should be equal to 816 rows.
daily_dataframe['latitude'] = pd.to_numeric(daily_dataframe['latitude'])
daily_dataframe['longitude'] = pd.to_numeric(daily_dataframe['longitude'])
daily_dataframe = daily_dataframe.reset_index()
# daily_dataframe.to_csv('meteo_output.csv', index=False)

game_data_with_geo.reset_index()
game_data_final = pd.merge(game_data_with_geo, daily_dataframe, left_index=True, right_index=True)
game_data_final = game_data_final.drop(columns=['date', 'latitude', 'longitude', 'index'])
#  print(game_data_final)  # should contain all of games.csv, venues.csv, and meteo's columns minus the ones that i don't think are relevant (stadium name, capacity)
game_data_final.to_csv('historical_game_data_final.csv', index=False)