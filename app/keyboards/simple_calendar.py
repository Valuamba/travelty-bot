import calendar
import locale
from datetime import datetime, timedelta
from typing import Any

from aiogram import Bot
from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
import pymorphy2

from app.handlers.fsm.pipeline import FSMPipeline
from app.handlers.service.helpers.departure_date import get_departure_date_values
from app.utils.markup_constructor import InlineMarkupConstructor

morph = pymorphy2.MorphAnalyzer()


class SimpleCalendarCD(CallbackData, prefix='calendar'):
    act: Any
    year: Any
    month: Any
    day: Any


class SimpleCalendar:

    date_key = "departure_date_%s"

    async def _get_date(self, data):
        date = None
        try:
            departure_date = data.get(self.date_key % data['departure_date_id'], "")
            date = datetime.strptime(
                departure_date if departure_date else " ", '%Y-%m-%d'
            )
        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD")
        return date

    async def _set_departure_date(self, state, data, callback_data: SimpleCalendarCD, value):
        current_date_key = self.date_key % data['departure_date_id']
        picked_date = datetime(int(callback_data.year), int(callback_data.month), int(callback_data.day))
        departure_date = await self._get_date(data)

        if picked_date == departure_date:
            data[current_date_key] = None
        else:
            data[current_date_key] = value
        await state.update_data(data)

    def _get_utility_buttons(self, departure_date, year, month, day):
        ignore_callback = SimpleCalendarCD(act="IGNORE", year=year, month=month, day=0).pack()

        utility_buttons = []
        utility_buttons.append(
            InlineKeyboardButton(
                text=f"⬅️Назад",
                callback_data=SimpleCalendarCD(act="BACK", year=year, month=month, day=day).pack()
            )
        )
        if departure_date:
            utility_buttons.append(InlineKeyboardButton(
                    text=f"🗑 Очистить",
                    callback_data=SimpleCalendarCD(act="CLEAR", year=year, month=month, day=day).pack()
                ))
            utility_buttons.append(InlineKeyboardButton(
                    text=f"✅ Подтвердить",
                    callback_data=SimpleCalendarCD(act="ACCEPT", year=year, month=month, day=day).pack()
                ))
        else:
            utility_buttons.append(InlineKeyboardButton(text=f"➖", callback_data=ignore_callback))
            utility_buttons.append(InlineKeyboardButton(text=f"➖", callback_data=ignore_callback))

        return utility_buttons

    async def start_calendar(
        self,
        bot: Bot,
        state: FSMContext,
        year: int = datetime.now().year,
        month: int = datetime.now().month,
    ) -> InlineKeyboardMarkup:
        locale.setlocale(locale.LC_ALL, 'ru_RU')
        max_delta_days = 31
        data = await state.get_data()

        departure_date = await self._get_date(data)

        ignore_callback = SimpleCalendarCD(act="IGNORE", year=year, month=month, day=0).pack()

        month_name = morph.parse(calendar.month_name[month])[0].normal_form.capitalize()

        month_nav = []
        lastMonth = datetime(year, month, 1) - timedelta(days=1)

        if lastMonth < datetime.today():
            month_nav.append(InlineKeyboardButton(text=" ",
                             callback_data=ignore_callback))
        else:
            month_nav.append(
                InlineKeyboardButton(text="<",
                                     callback_data=SimpleCalendarCD(act="PREV-MONTH", year=year, month=month, day=1
                                                                    ).pack()))

        month_nav.append(InlineKeyboardButton(text=f'{month_name} {str(year)}', callback_data=ignore_callback))

        if month - datetime.today().month >= 1:
            month_nav.append(InlineKeyboardButton(text=" ",
                                                  callback_data=ignore_callback
                                                  )
                             )
        else:
            month_nav.append(InlineKeyboardButton(text=">",
                             callback_data=SimpleCalendarCD(act="NEXT-MONTH", year=year, month=month, day=1
                                                                ).pack()))

        days_of_week = []
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            days_of_week.append(InlineKeyboardButton(text=day, callback_data=ignore_callback))

        month_days = []
        month_calendar = calendar.monthcalendar(year, month)
        for week in month_calendar:
            week_days = []
            for day in week:
                if(day == 0):
                    week_days.append(InlineKeyboardButton(text=" ", callback_data=ignore_callback))
                elif datetime.today().date() > datetime(year, month, day) .date()\
                        or datetime.today() + timedelta(days=max_delta_days) < datetime(year, month, day):
                    week_days.append(InlineKeyboardButton(text=f"-{day}-", callback_data=ignore_callback))
                elif datetime(year, month, day).date() == departure_date.date() if departure_date else None:
                    week_days.append(InlineKeyboardButton(
                        text=f"•{day}•", callback_data=SimpleCalendarCD(act="DAY", year=year, month=month, day=day).pack()
                    ))
                elif datetime(year, month, day).date() in get_departure_date_values(data):
                    week_days.append(InlineKeyboardButton(text=f"*{day}*", callback_data=ignore_callback))
                else:
                    week_days.append(InlineKeyboardButton(
                        text=f"{day}", callback_data=SimpleCalendarCD(act="DAY", year=year, month=month, day=day).pack()
                    ))

            if len(week_days) > 0:
                month_days.append(week_days)

        utility_buttons = self._get_utility_buttons(departure_date, year, month, 1)

        inline_keyboard = [month_nav, days_of_week]
        inline_keyboard += month_days
        inline_keyboard.append(utility_buttons)
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    async def process_selection(self, query: CallbackQuery, callback_data: SimpleCalendarCD, bot: Bot, state: FSMContext, fsmPipeline: FSMPipeline) -> tuple:
        return_data = (False, None)
        temp_date = datetime(int(callback_data.year), int(callback_data.month), 1)

        if callback_data.act == "IGNORE":
            await query.answer(cache_time=60)

        if callback_data.act == "DAY":
            data = await state.get_data()
            await self._set_departure_date(state, data, callback_data,
                                           datetime(int(callback_data.year), int(callback_data.month),
                                                    int(callback_data.day)
                                                    ).strftime('%Y-%m-%d')
                                           )
            await query.message.edit_reply_markup(await self.start_calendar(bot, state, int(callback_data.year), int(callback_data.month)))

        if callback_data.act == "PREV-MONTH":
            prev_date = temp_date - timedelta(days=1)
            await query.message.edit_reply_markup(await self.start_calendar(bot, state, int(prev_date.year), int(prev_date.month)))

        if callback_data.act == "NEXT-MONTH":
            next_date = temp_date + timedelta(days=31)
            await query.message.edit_reply_markup(await self.start_calendar(bot, state, int(next_date.year), int(next_date.month)))

        if callback_data.act == "CLEAR":
            data = await state.get_data()
            await self._set_departure_date(state, data, callback_data, None)
            await query.message.edit_reply_markup(await self.start_calendar(bot, state, int(callback_data.year), int(callback_data.month)))

        if callback_data.act == "BACK":
            data = await state.get_data()
            await self._set_departure_date(state, data, callback_data, None)
            await fsmPipeline.prev(query, bot, state)
        if callback_data.act == "ACCEPT":
            await fsmPipeline.prev(query, bot, state)

        return return_data
