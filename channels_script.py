# -*- coding: utf-8 -*
import asyncio
import datetime
import json

import telethon
from logger import Logger
from telethon import functions, types
from settings import Settings
from telethon.errors import FloodWaitError, ChannelsTooMuchError, InvalidBufferError, AuthKeyError, AuthKeyNotFound, \
    UserRestrictedError
from telethon import functions, types


# Добавить остальные экспешены

async def create_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel: str, is_avatar: bool,
                      permission_write_to_chat: bool, permission_show_admin: bool, avatar=None):
    try:
        async with client:
            result = await client(functions.channels.CreateChannelRequest(
                title=channel[0],
                about='',
                megagroup=True,
            ))
            # result = await client(functions.messages.EditChatAboutRequest)
            chat = result.chats[0]
            chat_id = chat.id
            if is_avatar:
                photo = await client.upload_file(avatar)
                await client(functions.channels.EditPhotoRequest(chat, photo))
            if permission_write_to_chat:
                await client.edit_permissions(chat, send_messages=False)
            if permission_show_admin:
                await client.edit_admin(chat, await client.get_me(), anonymous=True)
            Logger.info(f"Успешно создал группу - {channel[0]} на аккаунте - {session}")
            settings.count_created_channels += 1
            return True, chat_id
    except UserRestrictedError as ex:
        Logger.info("Словил спам, больше не могу создавать каналы на этом аккаунте, перевожу его в badsession", settings.red)
        return False, 0
    except Exception as ex:
        print(ex)
        return False, 0


async def delete_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str):
    try:
        async with client:
            result = await client(functions.channels.DeleteChannelRequest(channel_id))
            Logger.info(f"Успешно удалил группу - {channel_name} на аккаунте - {session}")
            settings.count_created_channels += 1
            return True
    except Exception as ex:
        print(ex)
        return False