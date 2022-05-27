from pathlib import Path
from typing import NamedTuple

from environs import Env


class Config(NamedTuple):
    __env = Env()
    __env.read_env()

    BASE_DIR = Path(__name__).resolve().parent.parent

    BOT_TOKEN = __env.str('BOT_TOKEN')

    ADMINS = __env.list('ADMIN_ID')

    MEDIA_DIRECTORY_PATH = __env.str("MEDIA_DIRECTORY_PATH")
    ROUTE_PHOTO_DIRECTORY = __env.str("ROUTE_PHOTO_DIRECTORY")

    POSTGRES_USER = __env.str('POSTGRES_USER')
    POSTGRES_PASSWORD = __env.str('POSTGRES_PASSWORD')
    POSTGRES_DB = __env.str('POSTGRES_DB')
    POSTGRES_HOST = __env.str('POSTGRES_HOST')

    POSTGRESQL_CONNECTION = "postgresql+asyncpg://%s:%s@%s:5432/%s" % (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB)

    MONGODB_DATABASE = __env.str('MONGODB_DATABASE')
    MONGODB_USERNAME = __env.str('MONGODB_USERNAME')
    MONGODB_PASSWORD = __env.str('MONGODB_PASSWORD')
    MONGODB_HOSTNAME = __env.str('MONGODB_HOSTNAME')
    MONGODB_PORT = __env.str('MONGODB_PORT')
    MONGODB_URI = 'mongodb://'
    ADMIN_CHAT = __env.str('ADMIN_CHAT')
    TRAVELTY_COM_CHANNEL = __env.str('TRAVELTY_COM_CHANNEL')
    TRAVELTY_COM_LINK = __env.str('TRAVELTY_COM_LINK')

    if MONGODB_USERNAME and MONGODB_PASSWORD:
        MONGODB_URI += f"{MONGODB_USERNAME}:{MONGODB_PASSWORD}@"
    MONGODB_URI += f"{MONGODB_HOSTNAME}"