from aiogram.dispatcher.filters.state import StatesGroup, State


# class AnswerAdmin(StatesGroup):
#     ANSWER = State()


class RoutePrivate(StatesGroup):
    AddRoute = State()
    departure_date = State()
    departure_town = State()
    arrival_town = State()
    confirm_departure_town = State()
    confirm_arrival_town = State()
    complete = State()
    choose_payment_type = State()
    commentary = State()
    select_service = State()

