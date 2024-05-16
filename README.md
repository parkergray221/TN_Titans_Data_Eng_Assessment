# TN_Titans_Data_Eng_Assessment

There's three different files in this repo pertaining to the three broad steps of this assessment.

"You should use the Open Meteo weather API (https://open-meteo.com/) to gather a dataset of historical weather forecasts for all regular season games from the 2021 – 2023 NFL seasons." -> **historical_weather_reader.py**\
"use SQL to perform five or more queries on the dataset that you think might yield interesting results" -> **TN_Titans_SQL_Script.sql**\
"Engineer a reusable method to easily retrieve weather forecasts for upcoming games in the 2024 season.  Assume the upcoming schedule is unknown and this method will be run on a continuous basis in the days leading up to the scheduled games." -> **forecast_weather_reader.py**

The two py files output csv's of the final dataframe for the reviewer's perusal if needed. Both python scripts should run through 'python <file_name.py>' in command prompt on any machine with both python and the associated packages within each py file (only two: **openmeteo_requests** and **pandas**) properly installed via **pip**. The **openmeteo_requests** package is an open-source package by https://open-meteo.com/ under the GNU Affero GPLV3 also provided within this repository.

Both python files should be fairly straightforward ETL programs for anyone familiar with only a few minor transformations necessary for the input **Games.csv** and **Venues.csv** files before they're ready for meteo submission. The SQL file should be runnable is **SSMS** (the program I personally used to run it) or any other SQL Management Program so long as **historical_game_data_final.csv** is provided as the input for the table.

Being frank, the portion of the proect I'm less happy with is the SQL query section - althrough I do feel I've made 5 *reasonably interesting* queries, I do not feel that I have enough information to feel conclusive about the results of these queries. But they are *interesting questions* I would ask if I were actually working on this data, I would just need more data to control against to be certain of results.

I'm asked to provide **assumptions, approach, and any interesting insights you gained from your analysis**, which follow below:
* I assume that the output of open-meteo is accurate for the days queried and that all data provided in Games.csv and Venues.csv is accurate. I assume the home team of a stadium tends to win games.
* Approach is to provide as frictionless an input to the meteo API as possible, minimize the number of inputs to the API, append relevant weather data to each row of the input game_data dataframe.
* Insights... it doesn't seem like weather such a rain or snow has an overwhelming impact on game outcome. *Some* impact for certain, but I don't feel comfortable narrowing down the exact degree. The insight I feel most comfortable making is that **some** grass surfaces are more rain-resistant than others, but as said in the paragraph above I feel there are many more variables that go into a game win than just weather and do not feel comfortable being held to the above insights. 
