__version__ = '0.1.0'

from motor.motor_asyncio import AsyncIOMotorClient

from bson.objectid import ObjectId

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from envparse import env

env.read_envfile()

MONGO_HOST = env.str('MONGO_HOST')
MONGO_PORT = env.int('MONGO_PORT', default=27017)
MONGO_DB = env.str('MONGO_DB', default='standups')

mongo = AsyncIOMotorClient(host=MONGO_HOST, port=MONGO_PORT)

db = mongo[MONGO_DB]

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'])

@app.get("/users")
async def list_users():
    return await db.report.distinct('user')

N_PER_PAGE = 60

@app.get("/reports/{user_name}")
async def list_reports(user_name: str, start_value: str = None):
    start_value = ObjectId(start_value) if start_value else ObjectId()
    reports = await db.report.find({
        'user': user_name,
        '_id': { '$lt': start_value }
    }).sort([
        ('_id', -1)
    ]).limit(N_PER_PAGE).to_list(N_PER_PAGE)
    # todo: rewrite
    for report in reports:
        report['_id'] = { '$oid': str(report['_id'])}
    return reports
