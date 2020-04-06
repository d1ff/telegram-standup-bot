import asyncio
import logging
import pickle
import datetime

from aiogram import types, Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from .app import bot, dp
from .handlers.manage_users_in_standup import (
    new_member_welcome,
    add_me,
    remove_me,
)
from .handlers.start_bot import start_bot, help_bot
from .handlers.user_report import (
    stop_report,
    report_handler,
    process_feel,
    process_today,
    process_yesterday,
    process_block,
    process_absences,
)
from .handlers.user_settings import (
    settings_handler,
    deactivate,
    activate,
)
from .handlers.warnings import (
    only_non_private_groups,
    only_private_groups,
)
from .structs import BotStates
from .utils import cancel_task

__version__ = "0.0.1"

logger = logging.getLogger()


async def register_handlers():
    dp.register_message_handler(
        start_bot,
        types.ChatType.is_private,
        commands=["start"],
    )
    dp.register_message_handler(
        help_bot, state="*", commands=["help"]
    )

    dp.register_message_handler(
        new_member_welcome,
        types.ChatType.is_group_or_super_group,
        content_types=types.ContentType.NEW_CHAT_MEMBERS,
    )
    dp.register_message_handler(
        add_me,
        types.ChatType.is_group_or_super_group,
        commands=["add_me"],
    )
    dp.register_message_handler(
        only_non_private_groups,
        types.ChatType.is_private,
        state="*",
        commands=["add_me"],
    )
    dp.register_message_handler(
        remove_me,
        types.ChatType.is_group_or_super_group,
        commands=["remove_me"],
    )
    dp.register_message_handler(
        only_non_private_groups,
        types.ChatType.is_private,
        state="*",
        commands=["remove_me"],
    )

    dp.register_message_handler(
        settings_handler,
        types.ChatType.is_private,
        commands=["settings"],
        state=BotStates.STANDBY,
    )
    dp.register_message_handler(
        only_private_groups,
        types.ChatType.is_group_or_super_group,
        state="*",
        commands=["settings"],
    )
    dp.register_callback_query_handler(
        deactivate,
        lambda c: c.data == "deactivate",
        state=BotStates.STANDBY,
    )
    dp.register_callback_query_handler(
        activate,
        lambda c: c.data == "activate",
        state=BotStates.STANDBY,
    )
    dp.register_message_handler(
        report_handler,
        types.ChatType.is_private,
        state=BotStates.STANDBY,
        commands=["report"],
    )
    dp.register_message_handler(
        only_private_groups,
        types.ChatType.is_group_or_super_group,
        commands=["report"],
    )

    dp.register_message_handler(
        stop_report,
        types.ChatType.is_private,
        state="*",
        commands=["stop_report"],
    )
    dp.register_message_handler(
        only_private_groups,
        types.ChatType.is_group_or_super_group,
        state="*",
        commands=["stop_report"],
    )
    dp.register_message_handler(
        process_feel, state=BotStates.FEEL
    )
    dp.register_message_handler(
        process_today, state=BotStates.TODAY
    )
    dp.register_message_handler(
        process_yesterday, state=BotStates.YESTERDAY
    )
    dp.register_message_handler(
        process_block, state=BotStates.BLOCK
    )
    dp.register_message_handler(
        process_absences, state=BotStates.ABSENCES
    )


async def send_reminders(chat_id: int, user_id: int):
    while True:
        user = await dp.storage.get_data(chat=chat_id, user=user_id)
        now = datetime.datetime.now()
        if user and 'last_report' in user:
            if now - user['last_report'] < datetime.timedelta(hours=24):
                logger.info(f'Do not send reminder for {user_id}')
                await asyncio.sleep(1 * 3600)
                continue
        else:
            await asyncio.sleep(1 * 3600)
            continue

        try:
            await bot.send_message(
                user_id,
                r"Hi! A friendly reminder to submit a report."
                r" Use `/report` command for this. If you want"
                r" to deactivate the reminder, go to `/settings`",
            )
        except asyncio.CancelledError:
            return
        else:
            await asyncio.sleep(1 * 24 * 3600)


async def reminders_manager():
    loop = asyncio.get_event_loop()
    while True:
        for (
            chat_id,
            user_id,
        ) in await dp.storage.get_data_list():
            user = await dp.storage.get_data(
                chat=chat_id, user=user_id
            )
            if not user or chat_id == user_id:
                continue
            if (
                user["active"]
                and not user["task_id"]
            ):
                task = loop.create_task(
                    send_reminders(chat_id, user_id)
                )
                await dp.storage.update_data(
                    chat=chat_id,
                    user=user_id,
                    data={"task_id": id(task)},
                ),
                logger.info(
                    f"user {user_id} were added to standup"
                )
            if (
                not user["active"]
                and user["task_id"]
            ):
                user = await dp.storage.get_data(
                    chat=chat_id, user=user_id
                )
                await cancel_task(user["task_id"])
                await dp.storage.update_data(
                    chat=chat_id,
                    user=user_id,
                    data={"task_id": None},
                )
                logger.info(
                    f"user {user_id} were removed from standup"
                )
        await asyncio.sleep(5)


async def on_startup(_):
    await register_handlers()
    try:
        with open('/data/storage.pickle', 'rb') as f:
            mem = MemoryStorage()
            mem.data = pickle.load(f)
            for chat_id, users_data in mem.data.items():
                for user_id in users_data.keys():
                    data = await mem.get_data(chat=chat_id, user=user_id)
                    if 'task_id' in data: data['task_id'] = None
                    await dp.storage.set_data(
                        chat=int(chat_id), user=int(user_id), data=data)
            for chat_id, users_data in mem.data.items():
                for user_id in users_data.keys():
                    state = await mem.get_state(chat=chat_id, user=user_id)
                    await dp.storage.set_state(
                        chat=int(chat_id), user=int(user_id), state=state)
    except:
        logger.exception("Could not load data")
    loop = asyncio.get_event_loop()
    loop.create_task(reminders_manager())


async def on_shutdown(dp: Dispatcher):
    for ( chat_id,
            user_id,) in await dp.storage.get_data_list():
        user = await dp.storage.get_data(
            chat=chat_id, user=user_id
        )
        if not user or chat_id == user_id:
            continue
        if user["task_id"]:
            try:
                await cancel_task(user["task_id"])
            except:
                logging.exception("Unable to cancel task")
            await dp.storage.update_data(
                chat=chat_id,
                user=user_id,
                data={"task_id": None},
            )

    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.close()
    await asyncio.sleep(0.250)


def initialize_bot():
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
    )
