from app.handlers.service.helpers.departure_date import get_departure_date_values, dates_to_str_array
from app.models.sql.enums import ServiceTypeLocals, PaymentTypeLocales, JuridicalStatus
from app.models.sql.service import Trip


def map_trip_to_str(trip: Trip):
    departure_address = trip.departure_location.place
    arrival_address = trip.arrival_location.place

    departure_dates = dates_to_str_array(trip.departure_dates)

    departure_date_string = ", ".join([date.strftime('%d.%m') for date in departure_dates])

    text = [
        f"<b>Маршрут: </b>"
    ]

    text.append(f"   📆 {departure_date_string} <b>|</b> {departure_address} - {arrival_address} <b>|</b>")

    juridical_status = trip.juridical_status
    if juridical_status == JuridicalStatus.IndividualEntrepreneur:
        text.append(f"<b>Наименование компании: </b>{trip.company_name}")
    elif juridical_status == JuridicalStatus.Individual:
        text.append(f"<b>Контактное лицо: </b>{trip.contact_name}")

    phone_number = trip.phone_number
    if phone_number:
        text.append(f"<b>Номер телефона: </b>{phone_number}")

    text.append(f"<b>Сервисы: </b>")
    services = trip.services
    text.append("\r\n".join([" - " + ServiceTypeLocals[service] for service in services]))

    text.append(f"<b>Способ оплаты:</b> {PaymentTypeLocales[trip.payment_type]}")
    text.append(f"<b>Комментарий: </b>{trip.commentary}")

    return '\r\n'.join(text)


def map_data_to_trip_str(data: dict):
    departure_address = data['departure_address']['place']
    arrival_address = data['arrival_address']['place']

    departure_dates = get_departure_date_values(data)

    departure_date_string = ", ".join([date.strftime('%d.%m') for date in departure_dates])

    text = [
        f"<b>Маршрут: </b>"
    ]

    text.append(f"   📆 {departure_date_string} <b>|</b> {departure_address} - {arrival_address} <b>|</b>")

    juridical_status = data['juridical_status']
    if juridical_status == JuridicalStatus.IndividualEntrepreneur:
        text.append(f"<b>Наименование компании: </b>{data['company_name']}")
    elif juridical_status == JuridicalStatus.Individual:
        text.append(f"<b>Контактное лицо: </b>{data['contact_name']}")

    phone_number = data.get('phone_number', None)
    if phone_number:
        text.append(f"<b>Номер телефона: </b>{phone_number}")

    text.append(f"<b>Сервисы: </b>")
    services = data['services']
    text.append("\r\n".join([" - " + ServiceTypeLocals[service] for service in services]))

    text.append(f"<b>Способ оплаты:</b> {PaymentTypeLocales[data['payment_type']]}")
    text.append(f"<b>Комментарий: </b>{data['commentary']}")

    return '\r\n'.join(text)