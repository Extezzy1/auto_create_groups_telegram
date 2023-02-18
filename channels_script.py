# -*- coding: utf-8 -*

import telethon
from logger import Logger
from settings import Settings
from telethon.errors import FloodWaitError, AuthKeyError, AuthKeyNotFound, \
    UserRestrictedError, ChannelPrivateError
from telethon import functions


# Добавить остальные экспешены

async def create_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel: str, is_avatar: bool,
                      permission_write_to_chat: bool, permission_show_admin: bool, avatar=None):
    try:
        async with client:
            result = await client(functions.channels.CreateChannelRequest(
                title=channel[0],
                about=channel[1],
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
            link = (await client(functions.messages.ExportChatInviteRequest(
                    chat
                ))).link
            Logger.info(f"Успешно создал группу - {link} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            return True, chat_id, link
    except UserRestrictedError as ex:
        Logger.info("Словил спам, больше не могу создавать чаты на этом аккаунте, перевожу его в badsession", settings.red, out_file="logs.txt")
        return False, 0
    except FloodWaitError:
        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")

        settings.flood_sessions.append(session)

    except AuthKeyError as ex:
        Logger.info("Словил бан, перемещаю в badsession", settings.red, out_file="logs.txt")
        settings.deleted_sessions.append(session)

    except AuthKeyNotFound as ex:
        Logger.info("Словил бан, перемещаю в badsession", settings.red, out_file="logs.txt")
        settings.deleted_sessions.append(session)

    except Exception as ex:
        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
        return False, 0


async def delete_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str):
    try:
        async with client:
            result = await client(functions.channels.DeleteChannelRequest(channel_id))
            Logger.info(f"Успешно удалил группу - {channel_name} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            return True

    except AuthKeyError as ex:
        Logger.info("Словил бан, перемещаю в badsession", settings.red, out_file="logs.txt")
        settings.deleted_sessions.append(session)
    except FloodWaitError:
        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")
        settings.flood_sessions.append(session)
    except AuthKeyNotFound as ex:
        Logger.info("Словил бан, перемещаю в badsession", settings.red, out_file="logs.txt")
        settings.deleted_sessions.append(session)

    except Exception as ex:
        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
        return False


async def add_admin(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, admin_username: str):
    try:
        async with client:
            await client.edit_admin(await client.get_entity(channel_id), admin_username, anonymous=True)
            Logger.info(f"Успешно добавил бота {admin_username} в группу - {channel_id} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            return True
    except Exception as ex:
        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
        return False


async def make_post(settings: Settings, client: telethon.TelegramClient, session: str, channel_username_from: str, id_post_from: int, id_post_to: int, channel_to_id: int, type_of_post):
    try:
        async with client:
            result = await client(functions.messages.GetHistoryRequest(
                peer=channel_username_from,
                offset_id=0,
                offset_date=0,
                add_offset=0,
                limit=100,
                max_id=id_post_to,
                min_id=id_post_from,
                hash=0
            ))
            for message in result.messages:
                if type_of_post == "1":
                    await client(functions.messages.ForwardMessagesRequest(channel_username_from, [message.id], channel_to_id))
                else:
                    print(await client.get_entity(int(channel_to_id)))
                    await client.send_message(await client.get_entity(int(channel_to_id)), message)
            Logger.info(f"Успешно отправил сообщения в группу - {channel_to_id} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            return True
    except ChannelPrivateError:
        Logger.info(f"{channel_username_from} - приватный канал, не могу переслать сообщения..", settings.red, out_file="logs.txt")
    except FloodWaitError:
        Logger.info(f"Словил флуд на аккаунте {session}", settings.red)
        settings.flood_sessions.append(session)
    except Exception as ex:
        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
        return False


