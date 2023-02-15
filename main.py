# -*- coding: utf-8 -*
import datetime
import os.path
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
    config.read("config.ini", encoding="utf-8")
    delay_after_account = int(config["DELAY"]["delay_after_account"])
    path_to_channels = config["PATH_TO_TXT"]["path_to_channels"]
    path_to_undeleted_channels = config["PATH_TO_TXT"]["path_to_undeleted_channels"]
    path_to_admins = config["PATH_TO_TXT"]["path_to_admins"]
    if not (os.path.exists(path_to_channels) and os.path.isfile(path_to_channels)):
        raise ValueError("Неверный путь к файлу с каналами!")
    if not (os.path.exists(path_to_undeleted_channels) and os.path.isfile(path_to_undeleted_channels)):
        raise ValueError("Неверный путь к файлу с каналами!")
    if not (os.path.exists(path_to_admins) and os.path.isfile(path_to_admins)):
        raise ValueError("Неверный путь к файлу с каналами!")


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
            settings.check_flood_sessions()
            action = input("Выбор задания\n"
                           "\t1. Создание чатов\n"
                           "\t2. Удаление всех каналов\n"
                           "\t3. Удаление каналов, кроме списка\n"
                           "\t4. Отправка постов\n"
                           "\t5. Добавление админов\n"
                           "\t6. Поиск создателей чатов/каналов\n"
                           "Введите номер пункта: ")
            if action == "1":
                type_of_name = input("Имена генерировать из тхт или везде одно имя??\n\t1 - тхт\n\t2 - везде одно имя\nВведите цифру: ")
                while type_of_name != "1" and type_of_name != "2":
                    type_of_name = input(
                        "Имена генерировать из тхт или везде одно имя??\n\t1 - тхт\n\t2 - везде одно имя\nВведите цифру: ")

                if type_of_name == "2":
                    name_of_channel = input("Введите имя для каждого канала: ")
                    while len(name_of_channel) == 0:
                        name_of_channel = input("Имя не может быть пустым! Введите имя для каждого канала: ")


                is_avatar = input("Ставить аватары? да/нет: ").lower()
                while is_avatar != "да" and is_avatar != "нет":
                    is_avatar = input(
                        "Ставить аватары? да/нет: ").lower()

                if is_avatar == "да":
                    is_avatar = True
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

                Logger.info("Считываю каналы для создания...", settings.gr)
                if type_of_name == "1":
                    settings.read_channels_from_txt()
                else:
                    settings.read_channels_from_txt(name_of_channel)
                Logger.info(f"Считано {len(settings.channels)} каналов, начинаю создание...", settings.gr)
                while len(settings.channels) > 0 and len(accounts["active"]) > 0:
                    channel = settings.channels.pop(0)
                    if len(active_accounts) > 0:
                        session = active_accounts.pop(0)
                    else:
                        accounts = AccountsJson.read_json_file("accounts.json")
                        active_accounts = accounts["active"]
                        if len(active_accounts) > 0:
                            session = active_accounts.pop(0)
                        else:
                            Logger.info("Досрочно завершил создание каналов по причине - кончились аккаунты", settings.ye)
                            break
                    if is_avatar:
                        # Сделать чтение аватарок

                        path_to_avatar = "avatars/"

                        result = await channels_script.create_chat(settings, settings.accounts[session], session, channel,
                                                          is_avatar, permissions_write_to_chat, permissions_show_admin,
                                                          avatar=path_to_avatar)
                        if result[0]:
                            data = AccountsJson.read_json_file("data.json")
                            if not data.get(session, False):
                                data[session] = [[result[1], channel[0]]]
                            else:
                                data[session].append([result[1], channel[0]])
                            AccountsJson.write_json_file(data, "data.json")

                    else:
                        result = await channels_script.create_chat(settings, settings.accounts[session], session, channel,
                                                          is_avatar, permissions_write_to_chat, permissions_show_admin)
                        if result[0]:
                            data = AccountsJson.read_json_file("data.json")
                            if not data.get(session, False):
                                data[session] = [[result[1], channel[0]]]
                            else:
                                data[session].append([result[1], channel[0]])
                            AccountsJson.write_json_file(data, "data.json")

                    time.sleep(delay_after_account)
                Logger.info(f"Завершил создание каналов! Было создано {settings.count_created_channels} каналов!", settings.gr)
                settings.count_created_channels = 0
            elif action == "2":
                confirmation = input("Точно удаляем все каналы?? да/нет: ").lower()

                while confirmation != "да" and confirmation != "нет":
                    confirmation = input("Точно удаляем все каналы?? да/нет: ").lower()

                if confirmation == "да":
                    Logger.info("Начинаю удаление всех каналов...", settings.ye)
                    data = AccountsJson.read_json_file("data.json")
                    for session in data:
                        if session not in accounts["active"]:
                            Logger.info(f"Не смог удалить каналы привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..", settings.red)
                            continue
                        for channel in data[session]:
                            if await channels_script.delete_chat(settings, settings.accounts[session], session, channel[0], channel[1]):
                                data[session].remove(channel)
                    AccountsJson.write_json_file(data, "data.json")

                else:
                    Logger.info("Отменяю действие...", settings.ye)

            elif action == "3":
                
                confirmation = input("Точно удаляем каналы?? да/нет: ").lower()

                while confirmation != "да" and confirmation != "нет":
                    confirmation = input("Точно удаляем все каналы?? да/нет: ").lower()

                if confirmation == "да":

                    Logger.info("Считываю каналы, которые не нужно удалять...", settings.ye)
                    settings.read_undeleted_channels()
                    Logger.info(f"Считал {len(settings.undeleted_channels)} каналов.", settings.gr)

                    Logger.info("Начинаю удаление всех каналов...", settings.ye)
                    data = AccountsJson.read_json_file("data.json")
                    for session in data:
                        if session not in accounts["active"]:
                            Logger.info(
                                f"Не смог удалить каналы привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red)
                            continue
                        for channel in data[session]:
                            if not (channel[0] in settings.undeleted_channels or channel[1] in settings.undeleted_channels):
                                if await channels_script.delete_chat(settings, settings.accounts[session], session, channel[0],
                                                              channel[1]):
                                    data[session].remove(channel)
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

                id_from = int(id_from)
                id_to = int(id_to)
                data = AccountsJson.read_json_file("data.json")
                for session in data:
                    if session not in accounts["active"]:
                        Logger.info(
                            f"Не смог удалить каналы привязанные к [{session}], так как аккаунт [{session}] не активен, пропускаю..",
                            settings.red)
                        continue
                    for channel in data[session]:
                        await channels_script.make_post(settings, settings.accounts[session], session, channel_from, id_from, id_to, channel[0], type_of_post)

            elif action == "5":
                Logger.info("Считываю файл с администраторами...", settings.ye)
                settings.read_admins()
                Logger.info(f"Успешно считал {len(settings.admins)} администраторов! Начинаю добавление админов...", settings.gr)

                data = AccountsJson.read_json_file("data.json")

                for channel_admin in settings.admins:
                    channel_id = channel_admin[0]

                    admin_bot = channel_admin[1]
                    for session in data:
                        if session not in accounts["active"]:
                            Logger.info(
                                f"Не смог добавить {admin_bot} в администраторы канала {channel_id}, так как аккаунт [{session}] не активен, пропускаю..",
                                settings.red)
                            continue
                        for channel in data[session]:
                            if channel[0] == int(channel_id):

                                await channels_script.add_admin(settings, settings.accounts[session], session,
                                                                int(channel_id), admin_bot)

                Logger.info("Закончил добавление администраторов в каналы!", settings.gr)

            elif action == "6":
                Logger.info("Считываю данные....", settings.ye)
                data = AccountsJson.read_json_file("data.json")
                for session in data:
                    for channel in data[session]:
                        Logger.info(f"Аккаунт - [{session}] создал канал [{channel[1]}] с id - [{channel[0]}]", settings.purple)
                Logger.info("Закончил вывод созданных каналов", settings.gr)
            else:
                Logger.info("Действие должно быть числом от 1 до 9!", settings.red)
            settings.delete_sessions()
            settings.delete_limited_session()
            settings.move_flood_sessions()
            accounts = AccountsJson.read_json_file("accounts.json")
            active_accounts = accounts["active"]

            time.sleep(1)
            # Everything will work as expected now.
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
        settings = Settings(path_to_channels=path_to_channels,path_to_admins=path_to_admins,
                            path_to_undeleted_channels=path_to_undeleted_channels)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(all())
        input("Нажмите enter для выхода..")
