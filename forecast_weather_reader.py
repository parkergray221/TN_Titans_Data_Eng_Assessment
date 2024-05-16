import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# so the forecast weather reader here IS just the meteo sample code with some minor changes. that might look lazy. however, the prompt is this:
# Engineer a reusable method to easily retrieve weather forecasts for upcoming games in the 2024 season.  
# Assume the upcoming schedule is unknown and this method will be run on a continuous basis in the days leading up to the scheduled games. 
# therefore you would simply need to run the forecast sample provided for the given geo location of the stadium with an upcoming game. 
# i've set the code to loop through each geo location provided in venues so you can have an exhaustive 7 day look at every stadium whenever you run this code, so for the purpose of the hypothetical,
# you could simply look at the resultant csv for stadiums with a known game within the next 7 days and view the columns that display temp, rain, snow, and wind.
venues = pd.read_csv('Venues.csv',encoding='windows-1252')

venues['Latitude'] = venues['Geo'].str.split(',').str[0].astype(float)
venues['Longitude'] = venues['Geo'].str.split(',').str[1].astype(float)
# print(venues)
venues_stripped = venues.drop(['Capacity', 'Surface', 'Roof_Type', 'Team(s)', 'Opened', 'Geo'], axis ='columns')
# print(venues_stripped)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"

forecast_dataframe = pd.DataFrame(columns=['stadium_name', 'location', 'date', 'latitude', 'longitude', 'temperature_2m_max', "temperature_2m_min", "rain_sum", "snowfall_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"])
for index, row in venues_stripped.iterrows():
	params = {
        "latitude": row['Latitude'],
        "longitude": row['Longitude'],
		"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "rain_sum", "snowfall_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
		"temperature_unit": "fahrenheit",
		"wind_speed_unit": "mph",
		"precipitation_unit": "inch"
	}
	responses = openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]

	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_weather_code = daily.Variables(0).ValuesAsNumpy()
	daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(4).ValuesAsNumpy()
	daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()
	daily_wind_gusts_10m_max = daily.Variables(6).ValuesAsNumpy()
	daily_wind_direction_10m_dominant = daily.Variables(7).ValuesAsNumpy()

	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
		end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}
	daily_data['stadium_name'] = row['Name']
	daily_data['location'] = row['Location']
	daily_data['latitude'] = response.Latitude()
	daily_data['longitude'] = response.Longitude()
	daily_data["weather_code"] = daily_weather_code
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum
	daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
	daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
	daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

	forcast_day_df = pd.DataFrame(data = daily_data)
	forecast_dataframe = pd.concat([forecast_dataframe, forcast_day_df])

forecast_dataframe_final = forecast_dataframe
# print(forecast_dataframe_final)
forecast_dataframe_final.to_csv('forecast_game_data_final.csv', index=False)