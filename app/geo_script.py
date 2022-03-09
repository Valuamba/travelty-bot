from geopy.geocoders import Nominatim
import pprint
import json

geolocator = Nominatim(user_agent="travelty-bot")
# location = geolocator.geocode("Брестская область", language='ru')
location = geolocator.geocode(
    query="Жабинка",
    timeout=10,
    exactly_one=True,
    language='ru',
    namedetails=True,
    addressdetails=True)

# print('Country' + ": " + place.split()[-1])

# name_ru = location.raw['namedetails']['name:ru']
# name_en = location.raw['namedetails']['name:en']
#
address = location.raw['address']


# print(name_ru)
# print(name_en)

pprint.pprint (location.raw)

# print(json.dumps(location, sort_keys=False, indent=4))