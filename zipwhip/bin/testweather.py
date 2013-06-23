from json import load
from urllib2 import urlopen
from pprint import pprint

data = urlopen('http://openweathermap.org/data/2.1/find/name?q=san%20jose&units=imperial')
#http://api.openweathermap.org/data/2.1/forecast/city?q=Moscow
#data = urlopen('http://api.openweathermap.org/data/2.1/forecast/city?q=seattle&units=imperial&mode=daily_compact')
#print data
cities = load(data)
#pprint(cities)

if cities['count'] > 0:
	city = cities['list'][0]
	pprint(city['main'])
	ch = int(city['main']['temp_max'])
	cl = int(city['main']['temp_min'])
	pprint(ch)
	pprint(cl)
	pprint(city['weather'])
	cf = city['weather'][0]['description']
	pprint(cf)
	print(cf)
