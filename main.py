# -*- coding: utf-8 -*
import datetime
import os.path
import random
import time
import asyncio
from configparser import ConfigParser
from mine_channels import mine_channels
from settings import Settings, AccountsJson
from logger import Logger
import logging

asyncio.set_event_loop(asyncio.SelectorEventLoop())
logging.disable(logging.WARN)
start_time = datetime.datetime.now()


try:
    config = ConfigParser(inline_comment_prefixes=("#"))
    config.read("config.ini", encoding="utf-8")
    delay_from = int(config["DELAY"]["delay_from"])
    delay_to = int(config["DELAY"]["delay_to"])
    count_thread = int(config["THREAD"]["count_thread"])
    count_accounts_per_proxy = int(config["PROXY"]["count_accounts_per_proxy"])
    auto_reconnect = config["PROXY"]["auto_reconnect"]
    proxy_timeout = int(config["PROXY"]["proxy_timeout"])
    type_of_proxy = config["PROXY"]["type_of_proxy"]
    if type_of_proxy != "HTTP" and type_of_proxy != "SOCKS":
        raise ValueError("Неверное значение типа прокси (Поддерживаемые форматы - HTTP и SOCKS)!")
    path_to_channels = config["PATH_TO_TXT"]["path_to_channels"]
    if not (os.path.exists(path_to_channels) and os.path.isfile(path_to_channels)):
        raise ValueError("Неверный путь к файлу с каналами!")


except ValueError as ex:
    raise ValueError(ex.args[0])
except Exception as ex:
    raise ValueError("Не все переменные конфига заполнены!")


async def all():
    is_not_exit = True
    while is_not_exit:
        try:
            accounts = AccountsJson.read_json_file("accounts.json")
            active_accounts = accounts["active"]
            Logger.info(f"В работу запущено {len(active_accounts)} аккаунтов!", settings.gr)
            action = input("Выбор задания\n"
                           "\t1. Создание чатов\n"
                           "\t2. Удаление всех каналов\n"
                           "\t3. Удаление каналов, кроме списка\n"
                           "\t4. Отправка постов\n"
                           "\t5. Добавление описания\n"
                           "\t6. Добавление админов\n"
                           "\t7. Поиск создателей чатов/каналов\n"
                           "Введите номер пункта: ")
            if action == "1":
                Logger.info("Считываю каналы...")
                settings.read_channels_from_txt()
                
                settings.delete_sessions()
                settings.delete_limited_session()
                settings.move_flood_sessions()
                time.sleep(1)
                accounts = AccountsJson.read_json_file("accounts.json")
                all_accounts = len(accounts["active"]) + len(accounts["flood"]) + len(accounts["bad"]) + len(
                    accounts["limited"])
                settings.check_flood_sessions()
            elif action == "2":
                pass
            elif action == "3":
                pass
            elif action == "4":
                pass
            elif action == "5":
                pass
            elif action == "6":
                pass
            elif action == "7":
                pass
            else:
                Logger.info("Действие должно быть числом от 1 до 9!", settings.red)

            # Everything will work as expected now.
        except Exception as ex:
            print(ex)
            random_delay = random.randint(delay_from, delay_to)
            time.sleep(random_delay)


if __name__ == '__main__':
        settings = Settings(delay_from=delay_from, delay_to=delay_to,
                            count_accounts_per_proxy=count_accounts_per_proxy, auto_reconnect=auto_reconnect,
                            proxy_timeout=proxy_timeout, type_of_proxy=type_of_proxy, path_to_channels=path_to_channels)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(all())
        input("Нажмите enter для выхода..")
