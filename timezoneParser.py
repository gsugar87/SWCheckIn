# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:49:50 2015
This has a list of all Southwest cities and their associated time zones.

@author: Glenn
"""
import pytz
from collections import defaultdict
import datetime

timeDelta = datetime.timedelta(days=1,microseconds=50)

def getTimeZone(city):
    cityShort = city[0:5]
    cityToTZ = defaultdict(lambda: pytz.timezone("America/New_York"))
    cityToTZ['*Long'] = pytz.timezone("America/New_York")
    cityToTZ['*Phoenix*'] = pytz.timezone("America/Phoenix")
    cityToTZ['*Omaha*'] = pytz.timezone("US/Central")
    cityToTZ['Omaha'] = pytz.timezone("US/Central")
    cityToTZ['*Reno'] = pytz.timezone("US/Pacific")
    cityToTZ['San'] = pytz.timezone("US/Pacific")
    cityToTZ['*San'] = pytz.timezone("US/Pacific")
    cityToTZ['SFO'] = pytz.timezone("US/Pacific")
    cityToTZ['DEN'] = pytz.timezone("America/Denver")
    cityToTZ['ABQ'] = pytz.timezone("US/Mountain")
    if cityShort == '*Reno':
        return cityToTZ[cityShort]
    else:
        return cityToTZ[city]

def shortName(tz):
    return tz.localize(datetime.datetime(2001,1,1)).tzname()
    
#    ['Oranjestad',
#     'Nassau',
#     'Belize City',
#     'Liberia',
#     'San José',
#     'Punta Cana',
#     'Montego Bay',
#     'San José del Cabo',
#     'Mexico City',
#     'Puerto Vallarta',
#     'Cancún',
#     'San Juan',
#     'Birmingham',
#     'Phoenix',
#     'Tucson',
#     'Little Rock',
#     'Burbank',
#     'Los Angeles',
#     'Oakland',
#     'Ontario',
#     'Orange County',
#     'Sacramento',
#     'San Diego',
#     'San Francisco',
#     'San Jose',
#     'Denver',
#     'Hartford/Springfield',
#     'Fort Lauderdale',
#     'Fort Myers',
#     'Jacksonville',
#     'Key West',
#     'Orlando',
#     'Palm Beach',
#     'Panama City',
#     'Pensacola',
#     'Tampa',
#     'Atlanta',
#     'Boise',
#     'Chicago',
#     'Indianapolis',
#     'Des Moines',
#     'Wichita',
#     'Louisville',
#     'New Orleans',
#     'Portland',
#     'Baltimore',
#     'Boston',
#     'Detroit',
#     'Flint',
#     'Grand Rapids',
#     'Minneapolis/St. Paul',
#     'Jackson',
#     'Branson',
#     'Kansas City',
#     'St. Louis',
#     'Omaha',
#     'Las Vegas',
#     'Reno/Tahoe',
#     'Manchester',
#     'Newark',
#     'Albuquerque',
#     'Albany',
#     'Buffalo',
#     'Long Island',
#     'New York',
#     'Rochester',
#     'Charlotte',
#     'Raleigh-Durham',
#     'Akron/Canton',
#     'Cleveland',
#     'Columbus',
#     'Dayton',
#     'Oklahoma City',
#     'Tulsa',
#     'Portland',
#     'Philadelphia',
#     'Pittsburgh',
#     'Providence',
#     'Charleston',
#     'Greenville/Spartanburg',
#     'Memphis',
#     'Nashville',
#     'Amarillo',
#     'Austin',
#     'Beaumont/Port Arthur',
#     'Corpus Christi',
#     'Dallas',
#     'El Paso',
#     'Harlingen/South Padre Island',
#     'Houston',
#     'Lubbock',
#     'Midland/Odessa',
#     'San Antonio',
#     'Salt Lake City',
#     'Norfolk',
#     'Richmond',
#     'Washington D.C',
#     'Seattle/Tacoma',
#     'Spokane',
#     'Milwaukee']