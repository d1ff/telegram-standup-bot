from ..app import dp


def convert_to_str_report(user_data: dict) -> str:
    return "\n\n".join(
        [
            f"*{ch}*\n{descr}"
            for ch, descr in user_data.items()
        ]
    )


async def get_target_chat(user_id: int) -> int:
    data = await dp.storage.get_data(chat=None, user=user_id)
    return data.get('chat_id', user_id)
