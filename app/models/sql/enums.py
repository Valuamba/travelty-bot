from enum import IntEnum


class PaymentType(IntEnum):
    WithPayment = 1
    WithoutPayment = 2
    NotDecided = 3


class ServiceType(IntEnum):
    Passengers = 1
    Pets = 2
    Documents = 3
    Package = 4
    LargeItems = 5
    ApartmentRemovals = 6


class JuridicalStatus(IntEnum):
    IndividualEntrepreneur = 1
    Individual = 2


class TripStatus(IntEnum):
    Outdated = 1,
    OnModeration = 2,
    Published = 3,
    Canceled = 4


JuridicalStatusLocals = {
    JuridicalStatus.Individual: "👤 Физическое лицо",
    JuridicalStatus.IndividualEntrepreneur: "👔 ИП"
}

ServiceTypeLocals = {
    ServiceType.Passengers: '💃🏻 Трансфер пассажиров',
    ServiceType.Pets: '🐕‍🦺 Трансфер животных',
    ServiceType.Documents: '📥 Передача документов',
    ServiceType.Package: '📦 Передача посылок',
    ServiceType.LargeItems: '🛏 Перевоз крупногабаритных предметов',
    ServiceType.ApartmentRemovals: '🏡 Квартирный переезд',
}


PaymentTypeLocales = {
    PaymentType.WithoutPayment: '🤝 Без оплаты',
    PaymentType.WithPayment: '💶 С оплатой',
    PaymentType.NotDecided: '🤔 Не определился'
}