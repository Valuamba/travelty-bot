from app.states.private_states import RoutePrivate


class Fields:
    COMPANY_NAME = "company_name"
    CONTACT_NAME = "contact_name"
    JURIDICAL_STATUS = "juridical_status"
    SERVICES = "services"
    PAYMENT_TYPE = "payment_type"
    COMMENTARY = "commentary"
    PHOTO = "photo_path"
    PHONE_NUMBER = "phone_number"


MapRouteStateToField = {
    RoutePrivate.PHOTO.state: Fields.PHOTO,
    RoutePrivate.COMMENTARY.state: Fields.COMMENTARY,
    RoutePrivate.PAYMENT_TYPE.state: Fields.PAYMENT_TYPE,
    RoutePrivate.JURIDICAL_STATUS.state: Fields.JURIDICAL_STATUS,
    RoutePrivate.SELECT_SERVICE.state: Fields.SERVICES,
    RoutePrivate.COMPANY_NAME.state: Fields.COMPANY_NAME,
    RoutePrivate.CONTACT_NAME.state: Fields.CONTACT_NAME,
    RoutePrivate.PHONE_NUMBER.state: Fields.PHONE_NUMBER
}