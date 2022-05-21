import re
from datetime import datetime

DEPARTURE_DATE_KEY: str = "departure_date_"


def get_departure_date_ids(data: dict):
    departure_date_keys = [key for key in data.keys() if DEPARTURE_DATE_KEY in key and data[key]]
    departure_keys_id = []

    if len(departure_date_keys) > 0:
        for key in departure_date_keys:
            key_matches = re.search('(?<=_)(\d+)$', key)
            if key_matches:
                departure_keys_id.append(int(key_matches.group(0)))

    return departure_keys_id


def get_departure_date_values(data: dict):
    ids = get_departure_date_ids(data)
    return [datetime.strptime(data[DEPARTURE_DATE_KEY + str(id)], '%Y-%m-%d').date() for id in ids if data[DEPARTURE_DATE_KEY + str(id)]]


def dates_to_str_array(dates: []):
    return [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]


def get_departure_date_values_str(data: dict):
    ids = get_departure_date_ids(data)
    return [data[DEPARTURE_DATE_KEY + str(id)] for id in ids if data[DEPARTURE_DATE_KEY + str(id)]]
