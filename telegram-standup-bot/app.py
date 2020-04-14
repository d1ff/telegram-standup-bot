import logging
import sys

from aiogram import Dispatcher, Bot
from .storage import MongoStorage
from envparse import env

__version__ = "0.0.1"

env.read_envfile()
BOT_TOKEN = env.str("BOT_TOKEN")
LOGGING_LEVEL = env(
    "LOGGING_LEVEL", postprocessor=str.upper
)

MONGO_HOST = env.str('MONGO_HOST')
MONGO_PORT = env.int('MONGO_PORT', default=27017)
MONGO_DB = env.str('MONGO_DB', default='standups')

PROXY = env.str('PROXY', default=None)

storage = MongoStorage(MONGO_HOST, MONGO_PORT, MONGO_DB, index=False)
bot = Bot(token=BOT_TOKEN, parse_mode="HTML", proxy=PROXY)
dp = Dispatcher(bot,
                storage=storage)


def setup_logger():
    logging.basicConfig(
        format="%(asctime)s | "
        "%(name)s:%(lineno)d | "
        "%(levelname)s | %(message)s",
        level=LOGGING_LEVEL,
        stream=sys.stdout,
    )

    logging.getLogger("aiohttp").setLevel(
        logging.WARNING
    )
    logging.getLogger().setLevel(LOGGING_LEVEL)


setup_logger()
