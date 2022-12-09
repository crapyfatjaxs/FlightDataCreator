# Flight Data Creator
----

Flight Data Creator was created for generating airline employee data, employee performance KPIs, flight loads (cargo weight and bag counts), and merging it with real airport delay data. There are no existing public sources of employee and operational data, so for building public facing dashboards I needed non-proprietary data.

## Real Flight Data
Real airport flight delay data can be gathered from the [Bureau of Transportation Statistics](https://www.transtats.bts.gov/ontime/Departures.aspx). Select all statiscs, the airport you would like data from, the airline and the dates (months, days, years). Then save as CSV and place in the data/raw_stats folder. You will need to delete the top 7 rows before running. You can put as many data exports CSV files as you like in the folder and the program will loop through all of them, so that if you would like to have multiple airlines data you can.

## Aircraft Registration Data
Updated aircraft registration data can be gathered from the [FAA](https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download). I have included the most up to date registration data in data/aircraft-database.xlsx, but as new aircraft are added to fleets it will need to be updated. The reason for needing this data is that the flight delay data does not include aircraft type, only tail numbers. The aircraft type is needed for knowing how much cargo weight and bag count to realistacally calculate for each flight.


## Config
You can change the output file name and location in the config.yaml file. The default is Scorecard.xlsx, which will show up in the same folder as the python program. 

You can also change the number of employees created, the default is set to 100. 

You can also change the origin city. The default is SEA. 