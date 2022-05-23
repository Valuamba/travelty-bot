from typing import Any

from app.config import Config
from app.handlers.service.helpers.constants import Fields
from app.handlers.service.helpers.departure_date import get_departure_date_values
from app.models.sql.enums import JuridicalStatus, ServiceType, ServiceTypeLocals, PaymentType, PaymentTypeLocales


def get_default(data: dict, field_name: str, default_value: Any):
    value = data.get(field_name, None)
    if not value or (value and isinstance(value, list) and len(value) == 0):
        return default_value
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

    return map_to_template(services=services,
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

    return (countries_str, route)


def map_mock_data_to_template(**kwargs):
    if kwargs['departure_dates'] and len(kwargs['departure_dates']) > 0:
        departure_date_string = ", ".join([date.strftime('%d.%m') for date in kwargs['departure_dates']])
    else:
        departure_date_string = "дд.мм, дд.мм, дд.мм"

    services = map(lambda s: ' - ' + ServiceTypeLocals[s] if ServiceType.has_value(s) else ' - ' + s, kwargs['services'])
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
        payment_type = PaymentTypeLocales[kwargs['payment_type']]

    user_id = kwargs['user_id']
    commentary = kwargs['commentary']

    (countries, route) = map_address_to_country_and_place(**kwargs)

    return \
"""
📆 %s | 🚕 %s |

👤 <a href=\"tg://user?id=%s\">%s</a> · ☎️ %s

<b>Услуги:</b>
%s

<b>Способ оплаты:</b> %s
<b>Комментарий:</b> %s

%s

🛣 <a href="%s">A9999</a> | 🌍 <a href="https://yandex.com/maps/">Яндекс Карты</a>
""" % (departure_date_string, route,
       user_id, contact, phone_number, services_str, payment_type, commentary, countries, Config.TRAVELTY_COM_LINK)


def map_route_to_form(**kwargs):
    departure_date_string = ", ".join([date.strftime('%d.%m') for date in kwargs['departure_dates']])
    services = map(lambda s: ' - ' + ServiceTypeLocals[s], kwargs['services'])
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
    # if phone_number:

    payment_type = kwargs['payment_type']
    if PaymentType.has_value(kwargs['payment_type']):
        payment_type = PaymentTypeLocales[kwargs['payment_type']]

    user_id = kwargs['user_id']
    commentary = kwargs['commentary']

    (countries, route) = map_address_to_country_and_place(**kwargs)

    return \
"""
📆 %s | 🚕 %s |

👤 <a href=\"tg://user?id=%s\">%s</a> %s

<b>Услуги:</b>
%s

<b>Способ оплаты:</b> %s
<b>Комментарий:</b> %s

%s

🛣 <a href="%s">A9999</a> | 🌍 <a href="https://yandex.com/maps/">Яндекс Карты</a>
""" % (departure_date_string, route,
       user_id, contact, phone_number, services_str, payment_type, commentary, countries, Config.TRAVELTY_COM_LINK)

