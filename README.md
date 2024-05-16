# TN_Titans_Data_Eng_Assessment

There's three different files in this repo pertaining to the three broad steps of this assessment.

"You should use the Open Meteo weather API (https://open-meteo.com/) to gather a dataset of historical weather forecasts for all regular season games from the 2021 – 2023 NFL seasons." -> **historical_weather_reader.py**\
"use SQL to perform five or more queries on the dataset that you think might yield interesting results" -> **TN_Titans_SQL_Script.sql**\
"Engineer a reusable method to easily retrieve weather forecasts for upcoming games in the 2024 season.  Assume the upcoming schedule is unknown and this method will be run on a continuous basis in the days leading up to the scheduled games." -> **forecast_weather_reader.py**

The two py files output csv's of the final dataframe for the reviewer's perusal if needed. Both python scripts should run through 'python <file_name.py>' in command prompt on any machine with both python and the associated packages within each py file (only two: **openmeteo_requests** and **pandas**) properly installed via **pip**. The **openmeteo_requests** package is an open-source package by https://open-meteo.com/ under the GNU Affero GPLV3 also provided within this repository.

Both python files should be fairly straightforward ETL programs for anyone familiar with only a few minor transformations necessary for the input **Games.csv** and **Venues.csv** files before they're ready for meteo submission. The portion of the project I'm less happy with is the SQL query section - althrough I do feel I've made 5 *reasonably interesting* queries, I do not feel that I have enough information to feel conclusive about the results of these queries. But they are *interesting questions* I would ask if I were actually working on this data, I would just need more data to control against to be certain of results.
