import asyncio
import pprint

from motor import motor_asyncio


client = motor_asyncio.AsyncIOMotorClient("localhost", 27017)
db = client.test_database


async def create_test_data():
    document1 = {"name": "Bob", "age": 12}
    document2 = {"name": "Alice", "age": 20}
    document3 = {"name": "Tod", "age": 25}

    future1 = db.test_mongo_collection.save(document1)
    future2 = db.test_mongo_collection.save(document2)
    future3 = db.test_mongo_collection.save(document3)
    res = await asyncio.gather(future1, future2, future3)
    pprint.pprint(res)


async def get_test_data():
    async for document in db.test_mongo_collection.find({'age': {"$gt": 12}}):
        pprint.pprint(document)
    # clear DB
    await db.test_mongo_collection.drop()


loop = asyncio.get_event_loop()
loop.run_until_complete(create_test_data())
loop.run_until_complete(get_test_data())
