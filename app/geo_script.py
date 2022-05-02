from geopy.geocoders import Nominatim
import pprint
import json

geolocator = Nominatim(user_agent="travelty-bot")
# location = geolocator.geocode("Брестская область", language='ru')
location = geolocator.geocode(
    query="Лодзь",
    timeout=10,
    exactly_one=False,
    language='ru',
    namedetails=True,
    addressdetails=True)

# print('Country' + ": " + place.split()[-1])
281748883
282606414
# name_ru = location.raw['namedetails']['name:ru']
# name_en = location.raw['namedetails']['name:en']
#
# address = location.raw['address']


# print(name_ru)
# print(name_en)

pprint.pprint(location)
location.reverse()
pprint.pprint(location)


location = sorted(location, key=lambda l: (l.raw is not None
                                           and 'address' not in l.raw
                                           and 'country' not in l.raw['address']),
                  reverse=True)

pprint.pprint (location[0].raw['address'])

# {'address': {'ISO3166-2-lvl4': 'BY-BR',
#              'country': 'Беларусь',
#              'country_code': 'by',
#              'county': 'Жабинковский район',
#              'postcode': '225101',
#              'state': 'Брестская область',
#              'town': 'Жабинка'},
#
# {'address': {'ISO3166-2-lvl4': 'PL-10',
#              'administrative': 'Лодзь',
#              'city': 'Лодзь',
#              'country_code': 'pl',
#              'state': 'Лодзинское воеводство'},


# print(json.dumps(location, sort_keys=False, indent=4))