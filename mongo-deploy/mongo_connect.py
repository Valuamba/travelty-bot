import asyncio

import motor.motor_asyncio
from beanie import init_beanie

from app import models
from app.models import ChatModel
from app.utils.db import MyBeanieMongo
from app.utils.db.mongo_storage import MongoStorage


async def main():

#     client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://valuamba:16zomole@localhost:27017")
#
# # 'mongodb://valuamba:16zomole@localhost:27017'
#
#     db = client.get_database('travelty')
#     await init_beanie(database=db, document_models=models.__models__)
#
#     chat_db = await ChatModel(id=123, type="hehe").create()
#
#     client.close()

    # storage = MongoStorage.from_url(
    #     "mongodb://valuamba:16zomole@localhost:27017",
    #     'travelty',
    # )
    mongo = MyBeanieMongo()
    #
    await mongo.init_db()
    print('End')

asyncio.run(main())
