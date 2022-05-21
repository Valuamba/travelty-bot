import re
from geopy import Nominatim

geolocator = Nominatim(user_agent="travelty-bot")


def find_place(query: str):
    locations = geolocator.geocode(
        query=query,
        timeout=10,
        exactly_one=False,
        language='ru',
        namedetails=False,
        addressdetails=True,
        )

    selected_locations = []

    if locations:
        for location in locations:
            if \
                    location.raw['type'] in ['administrative', 'village', 'city', 'town'] \
                    and location.raw['class'] in ['place', 'boundary'] \
                    and location.raw['osm_type'] in ['relation', 'node'] \
                    and 'country' in location.raw['address']\
                    and location.raw['display_name'] not in [sl.raw['display_name'] for sl in selected_locations]:
                selected_locations.append(location)

        selected_locations = sorted(selected_locations,
                                    key=lambda l: bool(re.search('[а-яА-Я]', get_place(l.raw['address'])))
                                    and bool(re.search('(Беларусь|Россия|Польша)', l.address))
                                                 , reverse=True
                                    )

    if len(selected_locations) > 0:
        return create_object(selected_locations[0])
    else:
        return None


def get_place(address):
    if 'village' in address:
        return address['village']
    elif 'hamlet' in address:
        return address['hamlet']
    elif 'town' in address:
        return address['town']
    elif 'municipality' in address:
        return address['municipality']
    elif 'city' in address:
        return address['city']
    elif 'administrative' in address:
        return address['administrative']
    elif 'country' in address:
        return address['country']
    else:
        raise Exception(f'Incorrect address: {address}')


def create_object(location):
    return {
        'display_name': location.raw['display_name'],
        'place': get_place(location.raw['address']),
        'country': location.raw['address']['country'],
        'lat': location.raw['lat'],
        'lon': location.raw['lon'],
        'place_id': location.raw['place_id']
    }