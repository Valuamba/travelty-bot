import pprint

from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import select, update
# from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.handlers.service.helpers.departure_date import get_departure_date_values, get_departure_date_values_str
from app.models.sql.enums import TripStatus
from app.models.sql.location import Location
from app.models.sql.service import Trip


# def get_users(session: AsyncSession):
#     session


def map_address_to_location(address):
    return Location(place_id=address['place_id'], lat=address['lat'], lon=address['lon'], country=address['country'],
                    place=address['place'], display_name=address['display_name']
                    )


async def change_trip_status(trip_id, status: TripStatus, session):
    stmt = (update(Trip).returning(Trip).where(Trip.id == trip_id).values(trip_status=status))

    orm_stmt = select(Trip, Location).from_statement(stmt).options(selectinload(Trip.arrival_location),
                                                                   selectinload(Trip.departure_location),
                                                                   selectinload(Trip.address_1),
                                                                   selectinload(Trip.address_2),
                                                                   selectinload(Trip.address_3)
                                                                   )
    # .execution_options(populate_existing=True)

    async with session.begin():
        result = await session.execute(orm_stmt)
        return result.scalar()


async def add_new_trip(data: dict, session):
    addresses_keys = ['departure_address', 'arrival_address', 'address_1', 'address_2', 'address_3']
    addresses = filter(None, [data.get(a, None) for a in addresses_keys])
    places = [a['place_id'] for a in addresses]
    query = select(Location, Location.place_id.in_(places))
    locations = (await session.scalars(query)).all()

    trip = Trip(user_id=data['user_id'],
                contact_name=data.get('contact_name', None),
                departure_dates=get_departure_date_values_str(data),
                company_name=data.get('company_name', None),
                phone_number=data.get('phone_number', None),
                caption_path=data.get('photo_path', None),
                juridical_status=data['juridical_status'],
                trip_status=TripStatus.OnModeration,
                payment_type=data['payment_type'],
                commentary=data.get('commentary', None),
                services=data['services']
                )

    addresses = [(data[a], a) for a in addresses_keys if a in data.keys()]

    new_locations = []
    for address, key in addresses:
        location = next((location for location in locations if address['place_id'] == location.place_id), None)
        if not location and address['place_id'] not in [l.place_id for l in new_locations]:
            new_locations.append(map_address_to_location(address))

    if new_locations and len(new_locations) > 0:
        for location in new_locations:
            session.add(location)
        await session.commit()

    locations = (await session.scalars(query)).all()

    for address, key in addresses:
        location = next((location for location in locations if address['place_id'] == location.place_id), None)
        set_address_value(location.id, address, key, trip)

    session.add(trip)
    await session.commit()

    return trip


def set_address_value(location_id, address, key, trip: Trip):
    if key == 'departure_address':
        if location_id:
            trip.departure_location_id = location_id
        else:
            trip.departure_location = map_address_to_location(address)
    elif key == 'arrival_address':
        if location_id:
            trip.arrival_location_id = location_id
        else:
            trip.arrival_location = map_address_to_location(address)
    elif key == 'address_1':
        if location_id:
            trip.address_1_id = location_id
        else:
            trip.address_1 = map_address_to_location(address)
    elif key == 'address_2':
        if location_id:
            trip.address_2_id = location_id
        else:
            trip.address_2 = map_address_to_location(address)
    elif key == 'address_3':
        if location_id:
            trip.address_3_id = location_id
        else:
            trip.address_3 = map_address_to_location(address)
