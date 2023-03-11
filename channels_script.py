# -*- coding: utf-8 -*
import asyncio

import telethon
from logger import Logger
from settings import Settings
from telethon.errors import FloodWaitError, AuthKeyError, AuthKeyNotFound, \
    UserRestrictedError, ChannelPrivateError, PhoneNumberInvalidError
from telethon import functions



async def create_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel: str, is_avatar: bool,
                      permission_write_to_chat: bool, permission_show_admin: bool, avatar=None):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")

            result = await client(functions.channels.CreateChannelRequest(
                title=channel[0],
                about=channel[1],
                megagroup=True,

            ))
            # result = await client(functions.messages.EditChatAboutRequest)
            chat = result.chats[0]
            chat_id = chat.id
            await client.edit_permissions(chat, change_info=False)
            if is_avatar:
                photo = await client.upload_file(avatar)
                await client(functions.channels.EditPhotoRequest(chat, photo))
            if permission_write_to_chat:
                await client.edit_permissions(chat, send_messages=False)
            if permission_show_admin:
                await client.edit_admin(chat, await client.get_me(), anonymous=True,
                                        change_info=True, post_messages=True, edit_messages=True, delete_messages=True,
                                        ban_users=True, invite_users=True, pin_messages=True, add_admins=True,
                                        manage_call=True)
            link = (await client(functions.messages.ExportChatInviteRequest(
                    chat
                ))).link
            Logger.info(f"Успешно создал группу - {link} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()
            return True, chat_id, link
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)

    except UserRestrictedError as ex:
        await client.disconnect()
        Logger.info("Словил спам, больше не могу создавать чаты на этом аккаунте, перевожу его в badsession", settings.red, out_file="logs.txt")
        return False, 0
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")

        settings.flood_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except AuthKeyError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)

    except AuthKeyNotFound as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ConnectionError as ex:

        await client.disconnect()

        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def delete_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            result = await client(functions.channels.DeleteChannelRequest(channel_id))
            Logger.info(f"Успешно удалил группу - {channel_name} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()

            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)

    except AuthKeyError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")
        settings.flood_sessions.append(session)
    except AuthKeyNotFound as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ConnectionError:
        await client.disconnect()

        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def edit_title_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str, title: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            result = await client(functions.channels.EditTitleRequest(channel_id, title))
            Logger.info(f"Успешно изменил название группы - {channel_name} на {title} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()

            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)

    except AuthKeyError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")
        settings.flood_sessions.append(session)
    except AuthKeyNotFound as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ConnectionError:
        await client.disconnect()

        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def edit_title_about_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str, title: str, about: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            await client(functions.channels.EditTitleRequest(channel_id, title))
            await client(functions.messages.EditChatAboutRequest(channel_id, about))
            Logger.info(f"Успешно изменил название и описание группы - {channel_name} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()

            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)

    except AuthKeyError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")
        settings.flood_sessions.append(session)
    except AuthKeyNotFound as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ConnectionError:
        await client.disconnect()

        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def edit_photo_chat(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, channel_name: str, path_to_avatar: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            photo = await client.upload_file(path_to_avatar)
            await client(functions.channels.EditPhotoRequest(channel_id, photo))
            Logger.info(f"Успешно изменил название группы - {channel_name} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()

            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)

    except AuthKeyError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red, out_file="logs.txt")
        settings.flood_sessions.append(session)
    except AuthKeyNotFound as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ConnectionError:
        await client.disconnect()

        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def add_admin(settings: Settings, client: telethon.TelegramClient, session: str, channel_id: int, admin_username: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            await client.edit_admin(await client.get_entity(channel_id), admin_username, anonymous=True,
                                    change_info=True, post_messages=True, edit_messages=True, delete_messages=True,
                                    ban_users=True, invite_users=True, pin_messages=True, add_admins=True,
                                    manage_call=True)
            Logger.info(f"Успешно добавил бота {admin_username} в группу - {channel_id} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            settings.count_created_channels += 1
            await client.disconnect()

            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()

        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")
        settings.deleted_sessions.append(session)
    except ConnectionError:
        await client.disconnect()


        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def make_post(settings: Settings, client: telethon.TelegramClient, session: str, channel_username_from: str, id_post_from: int, id_post_to: int, channel_to_id: int, type_of_post, channel_link: str):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
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
                    await client.send_message(await client.get_entity(int(channel_to_id)), message)
            Logger.info(f"Успешно отправил сообщения в группу - {channel_link} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            await client.disconnect()
            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()
        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except ChannelPrivateError:
        await client.disconnect()

        Logger.info(f"{channel_username_from} - приватный канал, не могу переслать сообщения..", settings.red, out_file="logs.txt")
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red)
        settings.flood_sessions.append(session)
    except ConnectionError:
        await client.disconnect()
        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


async def make_post_from_txt(settings: Settings, client: telethon.TelegramClient, session: str, channel_to_id: int, channel_link: str, text_post: str, path_to_file=None):
    try:
        await client.connect()

        if await client.is_user_authorized():
            await client.start("0")
            if path_to_file:
                await client.send_file(await client.get_entity(int(channel_to_id)), caption=text_post, file=path_to_file, parse_mode="md")
            else:
                await client.send_message(await client.get_entity(int(channel_to_id)), text_post, parse_mode="md")
            Logger.info(f"Успешно отправил сообщения в группу - {channel_link} на аккаунте - {session}", settings.gr, out_file="logs.txt")
            await client.disconnect()
            return True, 1
        else:
            await client.disconnect()
            Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

            settings.deleted_sessions.append(session)
    except PhoneNumberInvalidError as ex:
        await client.disconnect()
        Logger.info(f"Сессия {session} словила  бан, перемещаю в badsession", settings.red, out_file="logs.txt")

        settings.deleted_sessions.append(session)
    except FloodWaitError:
        await client.disconnect()

        Logger.info(f"Словил флуд на аккаунте {session}", settings.red)
        settings.flood_sessions.append(session)
    except ConnectionError:
        await client.disconnect()
        Logger.info(f"Не смог подключиться к {session}, пробую другую прокси...", settings.red, out_file="logs.txt")
        return False, 1
    except Exception as ex:
        await client.disconnect()

        Logger.info(f"Словил неизвестную ошибку {ex} на аккаунте - {session}", settings.red, out_file="logs.txt")
    return False, 0


