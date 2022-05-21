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
    return Location(place_id=address['place_id'],
             lat=address['lat'],
             lon=address['lon'],
             country=address['country'],
             place=address['place'],
             display_name=address['display_name']
             )


async def change_trip_status(trip_id, status: TripStatus, session):
    stmt = (
        update(Trip)
            .returning(Trip)
            .where(Trip.id == trip_id)
            .values(trip_status=status)
    )

    orm_stmt = select(Trip, Location) \
        .from_statement(stmt) \
        .options(selectinload(Trip.arrival_location), selectinload(Trip.departure_location))
        # .execution_options(populate_existing=True)

    async with session.begin():
        result = await session.execute(orm_stmt)
        return result.scalar()


async def add_new_trip(data: dict, session):
    places = [data['departure_address']['place_id'], data['arrival_address']['place_id']]
    query = select(Location, Location.place_id.in_(places))
    locations = (await session.scalars(query)).all()

    departure_location_id = None
    arrival_location_id = None

    for location in locations:
        if location.place_id == data['departure_address']['place_id']:
            departure_location_id = location.id
        elif location.place_id == data['arrival_address']['place_id']:
            arrival_location_id = location.id

    trip = Trip(user_id=data['user_id'],
                contact_name=data['contact_name'],
                departure_dates=get_departure_date_values_str(data),
                company_name=data.get('company_name', None),
                phone_number=data['phone_number'],
                caption_path=data['photo_path'],
                juridical_status=data['juridical_status'],
                trip_status=TripStatus.OnModeration,
                payment_type=data['payment_type'],
                commentary=data.get('commentary', None),
                services=data['services']
                )

    if arrival_location_id:
        trip.arrival_location_id = arrival_location_id
    else:
        trip.arrival_location = map_address_to_location(data['arrival_address'])

    if departure_location_id:
        trip.departure_location_id = departure_location_id
    else:
        trip.departure_location = map_address_to_location(data['departure_address'])

    # async with session.begin():
    session.add(trip)
    await session.commit()

    return trip
