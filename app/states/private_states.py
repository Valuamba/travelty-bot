from aiogram.dispatcher.filters.state import StatesGroup, State


# class AnswerAdmin(StatesGroup):
#     ANSWER = State()


class RoutePrivate(StatesGroup):
    # AddRoute = State()
    DEPARTURE_DATE = State()
    DEPARTURE_TOWN = State()
    ARRIVAL_TOWN = State()
    JURIDICAL_STATUS = State()
    COMPANY_NAME = State()
    CONTACT_NAME = State()
    CONFIRM_DEPARTURE_TOWN = State()
    CONFIRM_ARRIVAL_TOWN = State()
    COMPLETE = State()
    CHOOSE_PAYMENT_TYPE = State()
    COMMENTARY = State()
    SELECT_SERVICE = State()
    PAYMENT_TYPE = State()
    PICK_DATE_ID = State()
    SELECT_DATE = State()
    PHOTO = State()
    PHOTO_NUMBER = State()

