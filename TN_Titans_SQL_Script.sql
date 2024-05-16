-- select * from game_data_final

-- Order all stadiums based on their total inclement weather incidence for the 2021 - 2023 season.
select Game_Site, Home_Team, 
sum(case when rain_sum > 0 or snowfall_sum > 0 then 1 end) as total_inclement_weather_game_occurrences 
from game_data_final group by Game_Site, Home_Team order by total_inclement_weather_game_occurrences desc 

-- Does the home team win more often during inclement weather if the roof is retractable or fixed? Doesn't seem like it has much effect, we see the bills with an open roof win 20 games despite 23 weather inclement weather occurrences across the 2021 - 2023 seasons.
select distinct Home_Team, Roof_Type, 
sum(case when Home_Team_Final_Score > Visit_Team_Final_Score then 1 end) as Home_Team_Winnings, 
sum(case when rain_sum > 0 or snowfall_sum > 0 then 1 end) as total_inclement_weather_game_occurrences 
from game_data_final group by Home_Team, Roof_Type order by total_inclement_weather_game_occurrences desc

-- Does wind speed have a major effect on the home team winning? The best home team win records are 21, 20, 19, and 18. We see the overall best performing team in 2021- 2023 has a middle of the pack number of high wind games 
-- and the 5th best overall performing team has the highest number of high wind games, but we notice the lions and the bears have a pretty poor winrate while having the 2nd and 3rd highest wind count games. It does seem there is more evidence that it has a low
-- effect than not, however I could also be framing my 'high_wind_game_count' threshold incorrectly - perhaps you need much greater than 10 mph to start affecting pass or kick trajectories.
select Home_Team, 
sum(case when Home_Team_Final_Score > Visit_Team_Final_Score then 1 end) as Home_Team_Winnings, 
sum(case when wind_speed_10m_max > 10 then 1 end) as high_wind_game_count
from game_data_final group by Home_Team order by high_wind_game_count desc

-- Does any kind of inclement weather have major effect on a team's overall win count? Doesn't seem so - the highest winning teams have some of the highest numbers of inclement_weather_game_occurrences.
select distinct Home_Team, 
sum(case when Home_Team_Final_Score > Visit_Team_Final_Score then 1 end) as Home_Team_Winnings, 
sum(case when rain_sum > 0 or snowfall_sum > 0 or wind_speed_10m_max > 10 or wind_gusts_10m_max > 20 then 1 end) as total_inclement_weather_game_occurrences 
from game_data_final group by Home_Team order by Home_Team_Winnings desc

-- Given a rainy game, is there a particular kind of surface type that allows the home team to perform better? Bermuda grass is by far the most common surface type for games and it has the highest amount of home team wins and rainy gams as a result.
-- Cases where the home team won a greater amount on the surface than the amount of rainy games taking place on the surface are *maybe* a good indication that certain surfaces, eg FieldTurf COR, are more resistant to rainy weather? Maybe???
select Surface, count(surface) as count_of_surface, 
sum(case when Home_Team_Final_Score > Visit_Team_Final_Score then 1 end) as home_team_winnings_on_surface, 
sum(case when rain_sum > 0 then 1 end) as rainy_game_on_surface 
from game_data_final group by Surface order by count_of_surface desc
