from typing import Any

from app.config import Config
from app.handlers.service.helpers.constants import Fields
from app.handlers.service.helpers.departure_date import get_departure_date_values, dates_to_str_array
from app.models.sql.enums import JuridicalStatus, ServiceType, ServiceTypeLocals, PaymentType, PaymentTypeLocales
from app.models.sql.service import Trip
from app.utils.str import first_letter_to_lower


def get_default(data: dict, field_name: str, default_value: Any = None):
    value = data.get(field_name, None)
    if not value or (value and isinstance(value, list) and len(value) == 0):
        # if default_value:
        return default_value
        # else:
        #     raise Exception(f'Value doesent exist for key {field_name}')
    return value


def map_route_data_to_str(data: dict):
    services = get_default(data, Fields.SERVICES, ['услуга 1️⃣', 'услуга 2️⃣', 'услуга 3️⃣'])
    phone_number = get_default(data, Fields.PHONE_NUMBER, '+XXX (XX) XXX XX-XX')
    juridical_status = get_default(data, Fields.JURIDICAL_STATUS, JuridicalStatus.Individual)
    contact_name = get_default(data, Fields.CONTACT_NAME, data['full_name'])
    company_name = get_default(data, Fields.COMPANY_NAME, data['full_name'])
    commentary = get_default(data, Fields.COMMENTARY, '📜')
    payment_type = get_default(data, Fields.PAYMENT_TYPE, '💸💸💸')

    departure_address = get_default(data, 'departure_address', {'place': 'Откуда', 'country': 'Страна1' })
    arrival_address = get_default(data, 'arrival_address', {'place': 'Куда', 'country': 'Страна2' })
    address_1 = get_default(data, 'address_1', None)
    address_2 = get_default(data, 'address_2', None)
    address_3 = get_default(data, 'address_3', None)

    departure_dates = get_departure_date_values(data)
    # if departure_dates and len(departure_dates) > 0:
    #     departure_date_string = ", ".join([date.strftime('%d.%m') for date in departure_dates])
    # else:
    #     departure_date_string = "дд.мм, дд.мм, дд.мм"
    user_id = data['user_id']
    full_name = data['full_name']

    return map_mock_data_to_template(services=services,
                            phone_number=phone_number,
                            juridical_status=juridical_status,
                            contact_name=contact_name,
                            company_name=company_name,
                            commentary=commentary,
                            payment_type=payment_type,
                            departure_address=departure_address,
                            arrival_address=arrival_address,
                            address_1=address_1,
                            address_2=address_2,
                            address_3=address_3,
                            departure_dates=departure_dates,
                            user_id=user_id,
                            full_name=full_name
                           )


def map_address_to_country_and_place(**kwargs):
    departure_address = kwargs['departure_address']
    arrival_address = kwargs['arrival_address']
    full_addresses = [departure_address, kwargs['address_1'], kwargs['address_2'], kwargs['address_3'], arrival_address]
    countries = list(dict.fromkeys([address['country'] for address in filter(None, full_addresses)]))
    proxy_addresses_str = ' - '.join(map(lambda a: a['place'], filter(None, full_addresses)))
    countries_str = ' '.join(map(lambda c: f'#%s' % c, countries))
    route = f"<b>{proxy_addresses_str}</b>"

    rtext = "~".join(
        map(lambda a: f'{a["lat"]}%2C{a["lon"]}',
        filter(lambda a: a and a.get('lon', None) and a.get('lat', None), full_addresses)))

    if rtext:
        yandex_domain = f"https://yandex.com/maps/?ll={full_addresses[0]['lon']}%2C{full_addresses[0]['lat']}&mode=routes&rtext={rtext}"
    else:
        yandex_domain = f"https://yandex.com/maps/"

    return (countries_str, route, yandex_domain)


def map_mock_data_to_template(**kwargs):
    if kwargs['departure_dates'] and len(kwargs['departure_dates']) > 0:
        departure_date_string = ", ".join([date.strftime('%d.%m') for date in kwargs['departure_dates']])
    else:
        departure_date_string = "дд.мм, дд.мм, дд.мм"

    services = map(lambda s: ' - ' + first_letter_to_lower(ServiceTypeLocals[s]) if ServiceType.has_value(s) else ' - ' + s, kwargs['services'])
    services_str = '\n'.join(services)

    contact_name = kwargs['contact_name']
    company_name = kwargs['company_name']

    contact = kwargs['full_name']

    if kwargs['juridical_status'] == JuridicalStatus.Individual:
        contact = contact_name
    elif kwargs['juridical_status'] == JuridicalStatus.IndividualEntrepreneur:
        # contact = f'ИП «{company_name}»'
        contact = company_name

    phone_number = kwargs['phone_number']

    payment_type = kwargs['payment_type']
    if PaymentType.has_value(kwargs['payment_type']):
        payment_type = first_letter_to_lower(PaymentTypeLocales[kwargs['payment_type']])

    user_id = kwargs['user_id']
    commentary = first_letter_to_lower(kwargs['commentary'])

    (countries, route, yandex_domain) = map_address_to_country_and_place(**kwargs)

    return \
"""
📆 %s | 🚕 %s |

👤 <a href=\"tg://user?id=%s\">%s</a> · ☎️ %s

<b>Услуги:</b>
%s

<b>Способ оплаты:</b> %s
<b>Комментарий:</b> %s

%s

🌍 <a href="%s">Яндекс Карты</a>
""" % (departure_date_string, route,
       user_id, contact, phone_number, services_str, payment_type, commentary, countries, yandex_domain)


def map_trip_to_form(trip: Trip, full_name = None):
    departure_dates = dates_to_str_array(trip.departure_dates)
    departure_date_string = ", ".join([date.strftime('%d.%m') for date in departure_dates])

    services_str = '\n'.join(map(lambda s: ' - ' + first_letter_to_lower(ServiceTypeLocals[s]), trip.services))

    juridical_status = trip.juridical_status
    
    contact = trip.contact_name
    if juridical_status == JuridicalStatus.IndividualEntrepreneur:
        contact = trip.company_name


    (countries, route, yandex_domain) = map_address_to_country_and_place(departure_address=trip.departure_location.__dict__,
                                                          arrival_address=trip.arrival_location.__dict__,
                                                          address_1=trip.address_1.__dict__ if trip.address_1 else None,
                                                          address_2=trip.address_2.__dict__ if trip.address_2 else None,
                                                          address_3=trip.address_3.__dict__ if trip.address_3 else None,
                                                          )
    return publish_template(trip.id, departure_date_string, route, trip.user_id, contact, trip.phone_number, services_str,
                            trip.payment_type, first_letter_to_lower(trip.commentary), countries, yandex_domain)


def map_route_to_form(data):
    services_str = '\n'.join(map(lambda s: ' - ' + first_letter_to_lower(ServiceTypeLocals[s]), get_default(data, Fields.SERVICES)))
    phone_number = get_default(data, Fields.PHONE_NUMBER, None)
    juridical_status = get_default(data, Fields.JURIDICAL_STATUS)

    contact = ''
    if juridical_status == JuridicalStatus.Individual:
        contact = get_default(data, Fields.CONTACT_NAME, None)
    elif juridical_status == JuridicalStatus.IndividualEntrepreneur:
        contact = get_default(data, Fields.COMPANY_NAME, None)
    else:
        raise Exception('Wrong juridical status')

    if not contact:
        contact = data['full_name']

    commentary = get_default(data, Fields.COMMENTARY, None)
    payment_type = get_default(data, Fields.PAYMENT_TYPE)

    departure_address = get_default(data, 'departure_address')
    arrival_address = get_default(data, 'arrival_address')
    address_1 = get_default(data, 'address_1', None)
    address_2 = get_default(data, 'address_2', None)
    address_3 = get_default(data, 'address_3', None)

    user_id = data['user_id']

    departure_date_string = ", ".join([date.strftime('%d.%m') for date in get_departure_date_values(data)])

    (countries, route, yandex_domain) = map_address_to_country_and_place(departure_address=departure_address,
                                                          arrival_address=arrival_address, address_1=address_1, address_2=address_2, address_3=address_3)

    return publish_template(None, departure_date_string, route, user_id, contact, phone_number, services_str, payment_type, commentary, countries, yandex_domain)


def publish_template(id, departure_date_string: str, route: str,
                     user_id, contact, phone_number, services_str, payment_type, commentary, countries, yandex_domain):
    builder = []
    builder.append('📆 %s | 🚕 %s |' % (departure_date_string, route))
    builder.append('\n\n')
    builder.append('👤 <a href=\"tg://user?id=%s\">%s</a>' % (user_id, contact))
    if phone_number:
        builder.append(' · ☎ %s' % phone_number)
    builder.append('\n\n')
    builder.append('<b>Услуги:</b>\n%s' % services_str)
    builder.append('\n\n')
    builder.append('<b>Способ оплаты:</b> %s' % first_letter_to_lower(PaymentTypeLocales[payment_type]))
    if commentary:
        builder.append('\n')
        builder.append('<b>Комментарий:</b> %s' % commentary)
    builder.append('\n\n')
    builder.append(countries)
    builder.append('\n\n')
    if id:
        builder.append('🛣 <a href="%s">A%s</a> | ' % (Config.TRAVELTY_COM_LINK, str(id).zfill(4)))
    builder.append('🌍 <a href="%s">Яндекс Карты</a>' % yandex_domain)
    return ''.join(builder)


"""

https://yandex.com/maps/?ll=22.857702 52.790451&mode=routes&rtext=52.194346 24.020061~52.093754 23.685107~54.352541 18.650283&rtt=auto
https://yandex.com/maps/?ll=24.0199973 52.1941201&mode=routes&rtext=52.1941201 24.0199973~52.2085858 24.3542923
&ruri=ymapsbm1%3A%2F%2Fgeo%3Fll%3D24.020%252C52.194%26spn%3D0.107%252C0.054%26text%3D%25D0%2591%25D0%25B5%25D0%25BB%25D0%25B0%25D1%2580%25D1%2583%25D1%2581%25D1%258C%252C%2520%25D0%2591%25D1%2580%25D1%258D%25D1%2581%25D1%2586%25D0%25BA%25D0%25B0%25D1%258F%2520%25D0%25B2%25D0%25BE%25D0%25B1%25D0%25BB%25D0%25B0%25D1%2581%25D1%2586%25D1%258C%252C%2520%25D0%2596%25D0%25B0%25D0%25B1%25D1%2596%25D0%25BD%25D0%25BA%25D0%25B0~~ymapsbm1%3A%2F%2Fgeo%3Fll%3D18.650%252C54.353%26spn%3D0.521%252C0.172%26text%3DPolska%252C%2520Wojew%25C3%25B3dztwo%2520pomorskie%252C%2520Gda%25C5%2584sk&utm_source=main_stripe_big&z=8
https://yandex.by/maps/?
ll=22.857702%2C52.790451
&mode=routes
&rtext=52.194346 24.020061~52.093754 23.685107~54.352541 18.650283

"""



# """
# 📆 %s | 🚕 %s |
#
# 👤 <a href=\"tg://user?id=%s\">%s</a> %s
#
# <b>Услуги:</b>
# %s
#
# <b>Способ оплаты:</b> %s
# <b>Комментарий:</b> %s
#
# %s
#
# 🛣 <a href="%s">A9999</a> | 🌍 <a href="https://yandex.com/maps/">Яндекс Карты</a># """ % (departure_date_string, route,
#        user_id, contact, phone_number, services_str, payment_type, commentary, countries, Config.TRAVELTY_COM_LINK)

