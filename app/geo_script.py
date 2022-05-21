import re
import sys
from urllib.parse import unquote

from geopy.geocoders import Nominatim
import pprint
import json
# print ('Number of arguments:', len(sys.argv), 'arguments.')
# print ('Argument List:', str(sys.argv))

geolocator = Nominatim(user_agent="travelty-bot")
# location = geolocator.geocode("Брестская область", language='ru')
locations = geolocator.geocode(
    query=sys.argv[1],
    timeout=10,
    exactly_one=False,
    language='ru',
    namedetails=False,
    addressdetails=True,
    )

# print('Country' + ": " + place.split()[-1])
# name_ru = location.raw['namedetails']['name:ru']
# name_en = location.raw['namedetails']['name:en']
#
# address = location.raw['address']


# print(name_ru)
# print(name_en)

# pprint.pprint(location)
# locations.reverse()
# pprint.pprint(location)


# pprint.pprint(locations[0].raw)

# locations = [location for location in locations
#              if location.raw['type'] in ['administrative', 'village']
#              # and 'country' in location.raw['address']
#              ]

selected_locations = []

for location in locations:
    if \
            location.raw['type'] in ['administrative', 'village', 'city', 'town'] \
            and location.raw['class'] in ['place', 'boundary'] \
            and location.raw['osm_type'] in ['relation', 'node'] \
            and 'country' in location.raw['address']\
            and location.raw['display_name'] not in [sl.raw['display_name'] for sl in selected_locations]:
        selected_locations.append(location)


# res = []
# [res.append(x) for x in locations if x not in res]

# locations = sorted(selected_locations, key=lambda l: l)

# pprint.pprint([l for l in locations])

def get_place(address):
    if 'village' in address:
        return  address['village']
    elif 'town' in address:
        return  address['town']
    elif 'municipality' in address:
        return  address['municipality']
    elif 'city' in address:
        return  address['city']
    elif 'administrative' in address:
        return address['administrative']
    elif 'country' in address:
        return address['country']
    else:
        raise Exception(f'Incorrect address: {address}')

selected_locations = sorted(selected_locations, key=lambda l: bool(re.search('[а-яА-Я]', get_place(l.raw['address']))), reverse=True)

# selected_locations = locations
def create_object(location):
    return {
        'display_name': location.raw['display_name'],
        'place': get_place(location.raw['address']),
        'country': location.raw['address']['country'],
        'lat': location.raw['lat'],
        'lon': location.raw['lon'],
        'place_id': location.raw['place_id']
    }
# pprint.pprint([(l.raw['display_name'], l.raw['type'], l.raw['place_id'], l.raw['class'], l.raw['osm_type']) for l in selected_locations])
# pprint.pprint([(l.raw['display_name'], l.raw['type'], l.raw['place_id'], l.raw['class'], l.raw['osm_type']) for l in selected_locations])
# pprint.pprint([get_place(l.raw['address']) for l in selected_locations])
pprint.pprint([create_object(l) for l in selected_locations])
# pprint.pprint([(l.raw) for l in selected_locations])



# pprint.pprint (location[0].raw['address'])

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
# url =
# unquote(url)
# https://yandex.by/maps/?
# ll=20.647037, 51.140190
# &mode=routes
# &rtext=53.902284, 27.561831~48.206487, 16.363460~51.776770, 19.454724~51.049631, 13.737891
# &rtt=auto
# &ruri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D27.562%252C53.902%26spn%3D0.706%252C0.178%26text%3D%25D0%2591%25D0%25B5%25D0%25BB%25D0%25B0%25D1%2580%25D1%2583%25D1%2581%25D1%258C%252C%2520%25D0%259C%25D1%2596%25D0%25BD%25D1%2581%25D0%25BA~~~ymapsbm1%3A%2F%2Fgeo%3Fll%3D13.738%252C51.050%26spn%3D0.287%252C0.126%26text%3DDeutschland%252C%2520Sachsen%252C%2520Stadt%2520Dresden&z=7.04
#
#
# https://yandex.by/maps/?ll=20.647037, 51.140190&mode=routes&rtext=53.902284, 27.561831~48.206487, 16.363460~51.776770, 19.454724~51.049631, 13.737891&rtt=auto