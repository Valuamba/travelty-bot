from aiogram.dispatcher.filters.state import StatesGroup, State


class RoutePrivate(StatesGroup):
    DEPARTURE_DATE = State()
    PICK_ADDRESS = State()
    WRITE_ADDRESS = State()
    CONFIRM_ADDRESS = State()
    JURIDICAL_STATUS = State()
    COMPANY_NAME = State()
    CONTACT_NAME = State()
    COMPLETE = State()
    CHOOSE_PAYMENT_TYPE = State()
    COMMENTARY = State()
    SELECT_SERVICE = State()
    PAYMENT_TYPE = State()
    PICK_DATE_ID = State()
    SELECT_DATE = State()
    PHOTO = State()
    PHOTO_NUMBER = State()
    ACCEPT_ROUTE = State()

