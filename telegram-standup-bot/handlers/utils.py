from ..app import dp


def convert_to_str_report(user_data: dict) -> str:
    return "\n\n".join(
        [
            f"<b>{ch}</b>\n{descr}"
            for ch, descr in user_data.items()
        ]
    )


async def get_target_chat(user_id: int) -> int:
    for chat_id, _user_id in await dp.storage.get_data_list():
        if (
            chat_id != user_id
            and user_id == _user_id
        ):
            return chat_id
    return user_id
