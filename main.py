#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os.path
import random
import time
import asyncio
from configparser import ConfigParser
import channels_script
from settings import Settings, AccountsJson
from logger import Logger
import logging

asyncio.set_event_loop(asyncio.SelectorEventLoop())
logging.disable(logging.WARN)
start_time = datetime.datetime.now()


try:
    config = ConfigParser(inline_comment_prefixes=("#"))
    config.read("config.ini")
    delay_after_account = int(config["DELAY"]["delay_after_account"])
    auto_reconnect = config["PROXY"]["auto_reconnect"]
    proxy_timeout = int(config["PROXY"]["proxy_timeout"])
    type_of_proxy = config["PROXY"]["type_of_proxy"]
    if type_of_proxy != "HTTP" and type_of_proxy != "SOCKS":
        raise ValueError("Неверное значение типа прокси (Поддерживаемые форматы - HTTP и SOCKS)!")
    path_to_channels = config["PATH_TO_TXT"]["path_to_chats"]
    path_to_undeleted_channels = config["PATH_TO_TXT"]["path_to_undeleted_chats"]
    path_to_admins = config["PATH_TO_TXT"]["path_to_admins"]
    path_to_only_sending = config["PATH_TO_TXT"]["path_to_only_sending"]
    path_to_edit_photo = config["PATH_TO_TXT"]["path_to_edit_photo"]
    path_to_edit_title = config["PATH_TO_TXT"]["path_to_edit_title"]
    path_to_send_message = config["PATH_TO_TXT"]["path_to_send_message"]

    if not (os.path.exists(path_to_channels) and os.path.isfile(path_to_channels)):
        raise ValueError("Неверный путь к файлу с чатами!")
    if not (os.path.exists(path_to_undeleted_channels) and os.path.isfile(path_to_undeleted_channels)):
        raise ValueError("Неверный путь к файлу с неудаляемыми чатами!")
    if not (os.path.exists(path_to_admins) and os.path.isfile(path_to_admins)):
        raise ValueError("Неверный путь к файлу с администраторами!")
    if not (os.path.exists(path_to_only_sending) and os.path.isfile(path_to_only_sending)):
        raise ValueError("Неверный путь к файлу с чатами, в которые отпрвалять сообщения!")
    if not (os.path.exists(path_to_edit_photo) and os.path.isfile(path_to_edit_photo)):
        raise ValueError("Неверный путь к файлу с чатами, в которых изменяем аватарки!")
    if not (os.path.exists(path_to_edit_title) and os.path.isfile(path_to_edit_title)):
        raise ValueError("Неверный путь к файлу с чатами, в которых изменяем названия!")
    if not (os.path.exists(path_to_send_message) and os.path.isfile(path_to_send_message)):
        raise ValueError("Неверный путь к файлу с чатами, в которых изменяем названия!")

except ValueError as ex:
    raise ValueError(ex.args[0])
except Exception as ex:
    raise ValueError("Не все переменные конфига заполнены!")


async def all():
    is_not_exit = True
    accounts = AccountsJson.read_json_file("accounts.json")
    active_accounts = accounts["active"]
    Logger.info(f"В работу запущено {len(active_accounts)} аккаунтов!", settings.gr)
    while is_not_exit:
        try:
            accounts = AccountsJson.read_json_file("accounts.json")
            settings.check_flood_sessions()
            action = input("Выбор задания\n"
                           "\t1. Создание чатов\n"
                           "\t2. Удаление всех чатов\n"
                           "\t3. Удаление чатов, кроме списка\n"
                           "\t4. Отправка постов\n"
                           "\t5. Добавление админов\n"
                           "\t6. Поиск создателей чатов\n"
                           "\t7. Переименовать указанные чаты\n"
                           "\t8. Изменить аватары\n"
                           "\t9. Отправить сообщение из тхт\n"
                           "\t10. Удаление всех постов\n"
                           "Введите номер пункта: ")
            if action == "1":
                type_of_name = input("Имена генерировать из тхт или везде одно имя??\n\t1 - тхт\n\t2 - везде одно имя\nВведите цифру: ")
                while type_of_name != "1" and type_of_name != "2":
                    type_of_name = input(
                        "Имена генерировать из тхт или везде одно имя??\n\t1 - тхт\n\t2 - везде одно имя\nВведите цифру: ")

                if type_of_name == "2":
                    name_of_channel = input("Введите имя для каждого чата: ")
                    while len(name_of_channel) == 0:
                        name_of_channel = input("Имя не может быть пустым! Введите имя для каждого чата: ")

                is_avatar = input("Ставить аватары? да/нет: ").lower()
                while is_avatar != "да" and is_avatar != "нет":
                    is_avatar = input(
                        "Ставить аватары? да/нет: ").lower()

                if is_avatar == "да":
                    is_avatar = True
                    settings.read_avatars()
                else:
                    is_avatar = False

                print("Какие разрешения отключить?")
                permissions_write_to_chat = input("писать в чат всем - да/нет: ").lower()
                while permissions_write_to_chat != "да" and permissions_write_to_chat != "нет":
                    permissions_write_to_chat = input("писать в чат всем - да/нет: ").lower()

                if permissions_write_to_chat == "да":
                    permissions_write_to_chat = True
                else:
                    permissions_write_to_chat = False

                permissions_show_admin = input("анонимность админа - да/нет: ").lower()
                while permissions_show_admin != "да" and permissions_show_admin != "нет":
                    permissions_show_admin = input("анонимность админа - да/нет: ").lower()

                if permissions_show_admin == "да":
                    permissions_show_admin = True
                else:
                    permissions_show_admin = False

                Logger.info("Считываю чаты для создания...", settings.gr)
                if type_of_name == "1":
                    settings.read_channels_from_txt()
                else:
                    settings.read_channels_from_txt(name_of_channel)
                Logger.info(f"Считано {len(settings.channels)} чатов, начинаю создание...", settings.gr)
                index_account = 0
                count_active_acccounts = len(accounts["active"])
                limited_accounts = []
                while index_account < count_active_acccounts:
                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                    session = accounts["active"][index_account]
                    data = AccountsJson.read_json_file("data.json")
                    if data.get(session, False):
                        if len(data[session]) > 0:
                            limited_accounts.append(session)
                            index_account += 1
                            continue
                    client = settings.get_client(session, proxy)
                    channel = settings.channels[random.randint(0, len(settings.channels) - 1)]
                    if len(settings.avatars) > 0:

                        path_to_avatar = f"avatars/{settings.avatars[random.randint(0, len(settings.avatars) - 1)]}"
                    else:
                        # Logger.info("Закончились аватарки, продолжаю создание чатов без аватарок", settings.ye)
                        is_avatar = False

                    if is_avatar:

                        result = await channels_script.create_chat(settings, client, session, channel,
                                                          is_avatar, permissions_write_to_chat, permissions_show_admin,
                                                          avatar=path_to_avatar)
                        if result[0]:
                            data = AccountsJson.read_json_file("data.json")
                            if not data.get(session, False):
                                data[session] = [[result[1], channel[0], result[2]]]
                            else:
                                data[session].append([result[1], channel[0], result[2]])
                            AccountsJson.write_json_file(data, "data.json")
                            limited_accounts.append(session)
                            index_account += 1
                        elif not result[0]:
                            if result[1]:
                                continue
                            else:
                                index_account += 1


                    else:
                        result = await channels_script.create_chat(settings, client, session, channel,
                                                          is_avatar, permissions_write_to_chat, permissions_show_admin)
                        if result[0]:
                            data = AccountsJson.read_json_file("data.json")
                            if not data.get(session, False):
                                data[session] = [[result[1], channel[0], result[2]]]
                            else:
                                data[session].append([result[1], channel[0], result[2]])
                            AccountsJson.write_json_file(data, "data.json")
                            limited_accounts.append(session)
                            index_account += 1

                        elif not result[0]:
                            if result[1]:
                                continue
                            else:
                                index_account += 1

                    time.sleep(delay_after_account)
                for session in limited_accounts:
                    accounts["active"].remove(session)
                    accounts["limited"].append(session)
                AccountsJson.write_json_file(accounts, "accounts.json")
                Logger.info(f"Завершил создание чатов! Было создано {settings.count_created_channels} чатов!", settings.gr)
                settings.count_created_channels = 0
            elif action == "2":
                confirmation = input("Точно удаляем все чаты?? да/нет: ").lower()

                while confirmation != "да" and confirmation != "нет":
                    confirmation = input("Точно удаляем все чаты?? да/нет: ").lower()

                if confirmation == "да":
                    Logger.info("Начинаю удаление всех чатов...", settings.ye)
                    data = AccountsJson.read_json_file("data.json")
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(f"Не смог удалить чаты привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..", settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:
                            is_deleted = False
                            while not is_deleted:
                                proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                client = settings.get_client(session, proxy)

                                result = await channels_script.delete_chat(settings, client, session, channel[0],
                                                                           channel[1])
                                if result[0]:
                                    data[session].remove(channel)
                                    accounts["limited"].remove(session)
                                    accounts["active"].append(session)
                                    is_deleted = True
                                elif not result[0]:
                                    if result[1]:
                                        continue
                                    else:
                                        is_deleted = True
                    AccountsJson.write_json_file(accounts, "accounts.json")
                    AccountsJson.write_json_file(data, "data.json")

                else:
                    Logger.info("Отменяю действие...", settings.ye)

            elif action == "3":
                
                confirmation = input("Точно удаляем чаты?? да/нет: ").lower()

                while confirmation != "да" and confirmation != "нет":
                    confirmation = input("Точно удаляем все чаты?? да/нет: ").lower()

                if confirmation == "да":

                    Logger.info("Считываю чаты, которые не нужно удалять...", settings.ye)
                    settings.read_undeleted_channels()
                    Logger.info(f"Считал {len(settings.undeleted_channels)} чатов.", settings.gr)

                    Logger.info("Начинаю удаление всех чатов...", settings.ye)
                    data = AccountsJson.read_json_file("data.json")
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(
                                f"Не смог удалить чаты привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:
                            if not (channel[2] in settings.undeleted_channels):
                                is_deleted = False
                                while not is_deleted:
                                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                    client = settings.get_client(session, proxy)

                                    result = await channels_script.delete_chat(settings, client, session, channel[0], channel[1])
                                    if result[0]:
                                        data[session].remove(channel)
                                        accounts["limited"].remove(session)
                                        accounts["active"].append(session)
                                        is_deleted = True
                                    elif not result[0]:
                                        if result[1]:
                                            continue
                                        else:
                                            is_deleted = True


                    AccountsJson.write_json_file(accounts, "accounts.json")
                    AccountsJson.write_json_file(data, "data.json")
                else:
                    Logger.info("Отменяю действие...", settings.ye)

            elif action == "4":
                type_of_post = input("Делать репост или выкладывать от имени чата?"
                                     "\n\t1. Репост"
                                     "\n\t2. От имена чата"
                                     "\nВведите действие: ")

                while type_of_post != "1" and type_of_post != "2":
                    type_of_post = input("Делать репост или выкладывать от имени чата?"
                                         "\n\t1. Репост"
                                         "\n\t2. От имена чата"
                                         "\nВведите действие: ")

                channel_from = input("Введите юзернейм канала из которого брать посты: ")
                id_from = input("Введите id С которого брать сообщения: ")
                id_to = input("Введите id ДО которого брать сообщения: ")

                while not(id_from.isdigit() and id_to.isdigit()):
                    id_from = input("Введите id С которого брать сообщения: ")
                    id_to = input("Введите id ДО которого брать сообщения: ")

                id_from = int(id_from) - 1
                id_to = int(id_to) + 1

                Logger.info("Считываю чаты, в которые публикуем сообщения", settings.ye)
                settings.read_only_sending_chats()
                Logger.info(f"Считано {len(settings.only_sending_chats)} чатов! Начинаю рассылку!")

                data = AccountsJson.read_json_file("data.json")
                for session in data:
                    if session not in accounts["active"] and session not in accounts["limited"]:
                        Logger.info(
                            f"Не смог отправить сообщения в чаты привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..",
                            settings.red, out_file="logs.txt")
                        continue
                    for channel in data[session]:
                        if channel[2] not in settings.only_sending_chats:
                            is_posted = False
                            while not is_posted:
                                proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                client = settings.get_client(session, proxy)
                                result = await channels_script.make_post(settings, client, session, channel_from, id_from, id_to, channel[0], type_of_post, channel[2])
                                if result[0]:
                                    is_posted = True
                                elif not result[0]:
                                    if result[1]:
                                        continue
                                    else:
                                        is_posted = True
                AccountsJson.write_json_file(accounts, "accounts.json")

            elif action == "5":
                Logger.info("Считываю файл с администраторами...", settings.ye)
                settings.read_admins()
                Logger.info(f"Успешно считал {len(settings.admins)} администраторов! Начинаю добавление админов...", settings.gr)

                data = AccountsJson.read_json_file("data.json")

                for channel_admin in settings.admins:
                    channel_link = channel_admin[0]

                    admin_bot = channel_admin[1]
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(
                                f"Не смог добавить {admin_bot} в администраторы чата {channel_link}, так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:

                            if channel[2] == channel_link:
                                is_add_admin = False
                                while not is_add_admin:
                                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                    client = settings.get_client(session, proxy)
                                    result = await channels_script.add_admin(settings, client,
                                                                             session,
                                                                             channel[0], admin_bot)
                                    if result[0]:
                                        is_add_admin = True
                                    elif not result[0]:
                                        if result[1]:
                                            continue
                                        else:
                                            is_add_admin = True

                    AccountsJson.write_json_file(accounts, "accounts.json")

                Logger.info("Закончил добавление администраторов в чаты!", settings.gr)

            elif action == "6":
                Logger.info("Считываю данные....", settings.ye)
                data = AccountsJson.read_json_file("data.json")
                for session in data:
                    for channel in data[session]:
                        Logger.info(f"Аккаунт - [{session}] создал чат [{channel[2]}] с id - [{channel[0]}]", settings.purple, out_file="logs.txt")
                Logger.info("Закончил вывод созданных чатов", settings.gr)
            elif action == "7":
                # Изменение названия чата
                Logger.info("Считываю файл с названиями чатов...", settings.ye)
                settings.read_edit_title_chats()
                Logger.info(f"Успешно считал {len(settings.edit_title_chats)} чатов! Начинаю изменение...",
                            settings.gr)

                data = AccountsJson.read_json_file("data.json")

                for channel_edit in settings.edit_title_chats:
                    channel_link = channel_edit[0]

                    new_title = channel_edit[1]
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(
                                f"Не смог переименовать чат {admin_bot} в администраторы чата {channel_link}, так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:

                            if channel[2] == channel_link:
                                is_edit_title = False
                                while not is_edit_title:
                                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                    client = settings.get_client(session, proxy)
                                    result = await channels_script.edit_title_chat(settings, client,
                                                                             session,
                                                                             channel[0], channel[1], new_title)
                                    if result[0]:
                                        data[session] = [[channel[0], new_title, channel_link]]
                                        is_edit_title = True
                                    elif not result[0]:
                                        if result[1]:
                                            continue
                                        else:
                                            is_edit_title = True

                    AccountsJson.write_json_file(accounts, "accounts.json")
                    AccountsJson.write_json_file(data, "data.json")

                Logger.info("Закончил изменение названий чатов!", settings.gr)
            elif action == "8":
                # Изменение аватаров
                Logger.info("Считываю аватарки...", settings.ye)
                settings.read_avatars()
                if len(settings.avatars) > 0:
                    Logger.info(f"Успешно считал {len(settings.avatars)} аватарок!",
                                settings.gr)


                    Logger.info("Считываю чаты для изменения...", settings.ye)
                    settings.read_edit_photo_chats()
                    Logger.info(f"Успешно считал {len(settings.edit_photo_chats)} чатов! Начинаю изменение",
                                settings.gr)

                    data = AccountsJson.read_json_file("data.json")

                    for channel_link in settings.edit_photo_chats:
                        path_to_avatar = f"avatars/{settings.avatars[random.randint(0, len(settings.avatars) - 1)]}"
                        for session in data:
                            if session not in accounts["active"] and session not in accounts["limited"]:
                                Logger.info(
                                    f"Не смог изменить аватарку чата {channel_link}, так как аккаунт [{session}] не активен, пропускаю..",
                                    settings.red, out_file="logs.txt")
                                continue
                            for channel in data[session]:
                                if channel[2] == channel_link:
                                    is_edit_photo = False
                                    while not is_edit_photo:
                                        proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                        client = settings.get_client(session, proxy)
                                        result = await channels_script.edit_photo_chat(settings, client,
                                                                                 session,
                                                                                 channel[0], channel[1], path_to_avatar)
                                        if result[0]:
                                            is_edit_photo = True
                                        elif not result[0]:
                                            if result[1]:
                                                continue
                                            else:
                                                is_edit_photo = True

                        AccountsJson.write_json_file(accounts, "accounts.json")

                    Logger.info("Закончил изменение аватарок чатов!", settings.gr)
                else:
                    Logger.info("Загрузите аватарки в папку avatars!")
            elif action == "9":
                # Изменение названия чата
                Logger.info("Считываю файл с сообщениями...", settings.ye)
                settings.read_send_message_txt()
                Logger.info(f"Успешно считал {len(settings.send_message)} чатов! Начинаю отправку...",
                            settings.gr)


                is_video_or_photo = input("Отправлять видео/фото в канал? да/нет: ").lower()
                while is_video_or_photo != "да" and is_video_or_photo != "нет":
                    is_video_or_photo = input("Отправлять видео/фото в канал? да/нет: ").lower()

                if is_video_or_photo:
                    Logger.info("Считываю видео/фото из папки...", settings.ye)
                    settings.read_video_and_photo_for_send()
                Logger.info(f"Успешно считал {len(settings.send_media)} медиа для отправки!", settings.ye)

                data = AccountsJson.read_json_file("data.json")

                for channel_send in settings.send_message:
                    channel_link = channel_send[0]
                    message_text = channel_send[1]
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(
                                f"Не смог отправить сообщения в чат {channel_link}, так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:

                            if channel[2] == channel_link:
                                is_send_message = False
                                while not is_send_message:
                                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                    client = settings.get_client(session, proxy)
                                    if is_video_or_photo and len(settings.send_media) > 0:
                                        # Отправляет пост с видео или фото
                                        random_media = settings.send_media[random.randint(0, len(settings.send_media) - 1)]
                                        result = await channels_script.make_post_from_txt(settings, client,
                                                                             session,
                                                                             channel[0], channel[2], message_text, path_to_file=f"files/for_posts/{random_media}")
                                    else:
                                        result = await channels_script.make_post_from_txt(settings, client,
                                                                             session,
                                                                             channel[0], channel[2], message_text)
                                    if result[0]:
                                        is_send_message = True
                                    elif not result[0]:
                                        if result[1]:
                                            continue
                                        else:
                                            is_send_message = True

                    AccountsJson.write_json_file(accounts, "accounts.json")
                    AccountsJson.write_json_file(data, "data.json")

                Logger.info("Закончил отправку сообщений!", settings.gr)
            elif action == "10":
                # Изменение названия чата
                Logger.info("Считываю файл с чатами, из которых удаляем все посты...", settings.ye)
                settings.read_delete_posts()
                Logger.info(f"Успешно считал {len(settings.send_message)} чатов! Начинаю отправку...",
                            settings.gr)


                data = AccountsJson.read_json_file("data.json")

                for channel_send in settings.send_message:
                    channel_link = channel_send[0]
                    message_text = channel_send[1]
                    for session in data:
                        if session not in accounts["active"] and session not in accounts["limited"]:
                            Logger.info(
                                f"Не смог отправить сообщения в чат {channel_link}, так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red, out_file="logs.txt")
                            continue
                        for channel in data[session]:

                            if channel[2] == channel_link:
                                is_send_message = False
                                while not is_send_message:
                                    proxy = settings.proxies[random.randint(0, len(settings.proxies) - 1)]
                                    client = settings.get_client(session, proxy)
                                    if is_video_or_photo and len(settings.send_media) > 0:
                                        # Отправляет пост с видео или фото
                                        random_media = settings.send_media[random.randint(0, len(settings.send_media) - 1)]
                                        result = await channels_script.make_post_from_txt(settings, client,
                                                                             session,
                                                                             channel[0], channel[2], message_text, path_to_file=f"files/for_posts/{random_media}")
                                    else:
                                        result = await channels_script.make_post_from_txt(settings, client,
                                                                             session,
                                                                             channel[0], channel[2], message_text)
                                    if result[0]:
                                        is_send_message = True
                                    elif not result[0]:
                                        if result[1]:
                                            continue
                                        else:
                                            is_send_message = True

                    AccountsJson.write_json_file(accounts, "accounts.json")
                    AccountsJson.write_json_file(data, "data.json")

                Logger.info("Закончил отправку сообщений!", settings.gr)
            else:
                Logger.info("Действие должно быть числом от 1 до 9!", settings.red)
            settings.delete_sessions()
            # settings.delete_limited_session()
            settings.move_flood_sessions()
            time.sleep(1)
            # Everything will work as expected now.
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
        settings = Settings(path_to_channels=path_to_channels,path_to_admins=path_to_admins,
                            path_to_undeleted_channels=path_to_undeleted_channels, type_of_proxy=type_of_proxy,
                            path_to_only_sending=path_to_only_sending, path_to_edit_title=path_to_edit_title,
                            path_to_edit_photo=path_to_edit_photo, path_to_send_message=path_to_send_message)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(all())
        input("Нажмите enter для выхода..")
