# -*- coding: utf-8 -*
import json
import os
import shutil

import socks

from telethon import TelegramClient
from datetime import datetime, timedelta
from logger import Logger
import uuid
import hashlib
from colorama import init

init()


class Settings:
    red = "\033[31m"
    gr = "\033[32m"
    ye = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    turquoise = "\033[36m"
    UID = uuid.uuid1()
    DEVISE = hashlib.md5(str(UID.node).encode("utf-8")).hexdigest()
    SOCIAL_VTOPE = "m"

    def __init__(self, count_accounts_per_proxy,
                 auto_reconnect, proxy_timeout, type_of_proxy, path_to_channels):
        self.file_log = "logs.txt"
        self.count_accounts_per_proxy = count_accounts_per_proxy
        self.auto_reconnect = auto_reconnect
        self.proxy_timeout = proxy_timeout
        self.type_of_proxy = type_of_proxy
        self.path_to_channels = path_to_channels
        self.count_created_channels = 0
        self.channels = []
        self.count_ban_accounts = 0
        self.count_limited_accounts = 0
        self.count_flood_accounts = 0
        self.current_score = 0
        self.points = 0
        self.count_cancel_task = 0
        self.sessions = []
        self.proxies = []
        self.accounts = {}
        self.deleted_sessions = []
        self.limited_sessions = []
        self.flood_sessions = []
        AccountsJson.check_exists_json_accounts()
        self.load_sessions()
        self.load_proxies_from_txt()
        self.bind_proxy()
        self.delete_used_proxies_from_txt()
        self.load_accounts()
        self.load_data()

    def load_data(self):
        if not os.path.exists("data.json"):
            AccountsJson.write_json_file({}, "data.json")
        data = AccountsJson.read_json_file("data.json")

    # Загрузка сессий
    def load_sessions(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        self.sessions = []
        listdir = os.listdir('sessions')
        for session in listdir:
            if session.split(".")[1] == "session":
                if session not in accounts["bad"] and session not in \
                        accounts["limited"] and session not in accounts["flood"] and session not in accounts["active"]:
                    self.sessions.append(session)

    # Загрузка проксей из тхт файла
    def load_proxies_from_txt(self):
        with open('proxy.txt', 'r', encoding='utf-8') as read_file:
            lines = read_file.readlines()
            for line in lines:
                try:
                    line_split = line.strip().split(":")
                    if len(line_split) == 4:
                        self.proxies.append(line.strip())
                except:
                    Logger.info(f"Прокси {line.strip()} неверного формата!", self.red)
        self.proxies = self.proxies * self.count_accounts_per_proxy

    # Привязка прокси к аккаунтам
    def bind_proxy(self):
        listdir = os.listdir('sessions')
        sessions = self.sessions.copy()
        for session in sessions:
            try:
                file_name_json = session.split(".")[0] + ".json"
                if file_name_json in listdir:
                    with open(f"sessions/{file_name_json}", 'r') as file_read_json:
                        file_json = json.loads(file_read_json.read())
                    if not file_json.get("ProxyAccount", False):
                        if len(self.proxies) > 0:
                            file_json['ProxyAccount'] = self.proxies.pop(0)
                            with open(f"sessions/{file_name_json}", 'w') as file_write_json:
                                file_write_json.write(json.dumps(file_json))
                        else:
                            Logger.info(f"Не хватило прокси на аккаунт - {session}", self.red)
                            self.sessions.remove(session)
                else:
                    self.sessions.remove(session)
                    Logger.info(f"Не найден json файл - {session.split('.')[0]}.json", self.red)
            except Exception as ex:
                self.sessions.remove(session)
                Logger.info(f"Неправильный json - {session.split('.')[0]}.json", self.red)

    # Удаление привязанных прокси из тхт файла
    def delete_used_proxies_from_txt(self):
        res_list_proxies = []
        with open('proxy.txt', 'r', encoding='utf-8') as file_read:
            lines = file_read.readlines()
            for line in lines:
                if line.strip() in self.proxies:
                    res_list_proxies.append(line)
        with open('proxy.txt', 'w', encoding='utf-8') as file_write:
            for proxy in res_list_proxies:
                file_write.write(proxy)
        self.proxies = []

    # Зазругзка аккаунтов
    def load_accounts(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        all_sessions = accounts["active"] + accounts["flood"] + self.sessions
        counter_unbind = 0  # Хранит в себе количество аккаунтов без привязанного прокси
        for session in all_sessions:
            try:
                with open(f'sessions/{session.split(".")[0]}.json', 'r') as file_json:
                    json_ = json.loads(file_json.read())
                    proxy = json_.get("ProxyAccount", False)
                    if proxy:
                        client = self.get_client(session, proxy)
                        if client:
                            if session not in accounts["active"] and session not in accounts["flood"]:
                                accounts["active"].append(session)
                            self.accounts[session] = client
                            if json_.get("already_triggers", False):
                                del json_["already_triggers"]
                        else:
                            Logger.info(f"Не смог сгенерировать клиент - {session}", self.red)

                            if session in accounts["active"]:
                                accounts["active"].remove(session)
                            elif session in accounts["flood"]:
                                accounts["flood"].remove(session)
                    else:
                        if session in accounts["active"]:
                            accounts["active"].remove(session)
                        elif session in accounts["flood"]:
                            accounts["flood"].remove(session)
                        # Добавить в без прокси
                        counter_unbind += 1
            except Exception as ex:
                print(ex)
        AccountsJson.write_json_file(accounts, "accounts.json")
        # Logger.info(f"В работу запущено {len(accounts['active'])} аккаунтов!", self.gr)
        # Logger.info(f"Количество аккаунтов без прокси - {counter_unbind}", self.ye)
        # message = f"<b>Начинаю работу</b>\n\nВ работу запущено <b>{len(accounts['active'])}</b> аккаунтов!\n" \
        #           f"Количество аккаунтов без прокси - <b>{counter_unbind}</b>"
        # self.send_message_to_bot(message)

    # Метод перемещенния забанненных сессий тг
    def delete_sessions(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        for session in self.deleted_sessions:
            if self.accounts.get(session, False):
                del self.accounts[session]
            accounts["bad"].append(session)
            accounts["active"].remove(session)
            if os.path.exists(f'badsession/{session}'):
                os.remove(f'badsession/{session}')
            if os.path.exists(f'badsession/{session.split(".")[0]}.json'):
                os.remove(f'badsession/{session.split(".")[0]}.json')
            shutil.move(f"sessions/{session.split('.')[0]}.json", 'badsession')
            shutil.move(f"sessions/{session.split('.')[0]}.session", 'badsession')
        AccountsJson.write_json_file(accounts, "accounts.json")

        self.deleted_sessions = []

    # Метод, получения клиента телеграмм
    def get_client(self, session, proxy):
        proxy_ip = proxy.split(':')[0]
        proxy_port = int(proxy.split(':')[1])
        proxy_login = proxy.split(':')[2]
        proxy_password = proxy.split(':')[3].split('\n')[0]
        with open(f'sessions/{session.split(".")[0]}.json', 'r', encoding='utf-8') as config_account:
            json_ = json.loads(config_account.read())
        if json_.get("app_id", False) and json_.get("app_hash", False) and json_.get("app_version", False) and \
                json_.get("sdk", False) and json_.get("device", False) and json_.get("system_lang_pack", False):

            lang_code = json_.get("lang_code", "ru")
            if self.type_of_proxy == "HTTP":
                proxy = (socks.HTTP, proxy_ip, proxy_port, True, proxy_login, proxy_password)
            elif self.type_of_proxy == "SOCKS":
                proxy = (socks.HTTP, proxy_ip, proxy_port, True, proxy_login, proxy_password)
            client = TelegramClient(session=f"sessions/{session.split('.')[0]}", api_id=json_["app_id"], api_hash=json_["app_hash"],
                                proxy=proxy,
                                app_version=json_["app_version"], system_version=json_["sdk"],
                                device_model=json_["device"], lang_code=lang_code
                                )

        else:
            Logger.info(f'Подан неверный json - {session.split(".")[0]}.json, перемещаю аккаунт в bad',self.red, out_file=self.file_log)
            client = False
        return client

    # Метод, перемеющающий сессии и максимальный количеством подписок
    def delete_limited_session(self):

        accounts = AccountsJson.read_json_file("accounts.json")
        for session in self.limited_sessions:
            if self.accounts.get(session, False):
                del self.accounts[session]
            if os.path.exists(f'limited/{session}'):
                os.remove(f'limited/{session}')
            if os.path.exists(f'limited/{session.split(".")[0]}.json'):
                os.remove(f'limited/{session.split(".")[0]}.json')
            shutil.move(f"sessions/{session.split('.')[0]}.json", 'limited')
            shutil.move(f"sessions/{session.split('.')[0]}.session", 'limited')
            accounts["limited"].append(session)
            accounts["active"].remove(session)
        AccountsJson.write_json_file(accounts, "accounts.json")

        self.limited_sessions = []


    # Метод, инкрементирующий количество подписок на аккаунте
    @staticmethod
    def increment_subscribe(path_to_json):
        try:
            with open(path_to_json) as json_file:
                json_ = json.loads(json_file.read())
                subscribe = json_.get("Subscribe", 0)
                if subscribe == 0:
                    json_["Subscribe"] = 1
                else:
                    json_["Subscribe"] += 1
            with open(path_to_json, "w") as json_file_write:
                json_file_write.write(json.dumps(json_))
        except Exception as ex:
            pass

    def move_flood_sessions(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        for session in self.flood_sessions:
            accounts["flood"].append(session)
            accounts["active"].remove(session)
        AccountsJson.write_json_file(accounts, "accounts.json")
        self.flood_sessions = []

    def check_flood_sessions(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        flood_sessions = accounts["flood"]
        for session in flood_sessions:
            path_to_json = f"sessions/{session.split('.')[0]}.json"
            if os.path.exists(path_to_json):
                with open(path_to_json, "r") as json_file:
                    json_ = json.loads(json_file.read())
                current_date = datetime.now()
                flood_from = json_.get("flood_from", False)
                if flood_from:
                    flood_date = datetime.strptime(flood_from, "%d-%m-%Y %H:%M:%S")
                else:
                    accounts["flood"].remove(session)
                    accounts["active"].append(session)
                    with open(path_to_json, "w") as json_file:
                        json_file.write(json.dumps(json_))
                    Logger.info(f"Убрал статус flood из аккаунта {session}", self.turquoise)
                    self.count_flood_accounts -= 1
                    continue
                flood_seconds = int(json_["flood_time"])
                if flood_date + timedelta(seconds=flood_seconds) < current_date:
                    accounts["flood"].remove(session)
                    accounts["active"].append(session)
                    del json_["flood_from"]
                    del json_["flood_time"]
                    with open(path_to_json, "w") as json_file:
                        json_file.write(json.dumps(json_))
                    Logger.info(f"Убрал статус flood из аккаунта {session}", self.turquoise)
                    self.count_flood_accounts -= 1
            else:
                Logger.info(f"Не найден Json файл сессии - {session}", self.red)
        AccountsJson.write_json_file(accounts, "accounts.json")

    def read_channels_from_txt(self, is_name=False):
        with open(self.path_to_channels, "r", encoding="utf-8") as file_with_channels_read:
            lines = file_with_channels_read.readlines()
            counter = 1
            for line in lines:
                line_split = line.strip().split(";")
                try:
                    if is_name:
                        channel_users = line_split
                        if len(channel_users) > 0:
                            self.channels.append([channel_name, channel_users])
                        else:
                            Logger.info(
                                f"Не указаны пользователи в строке - {counter}, проверьте введенные данные",
                                self.red)
                    else:
                        channel_name = line_split[0]
                        channel_users = line_split[1:]
                        if len(channel_users) > 0:
                            self.channels.append([channel_name, channel_users])
                        else:
                            Logger.info(f"Не указаны пользователи у канала - {channel_name}, проверьте введенные данные", self.red)
                except Exception as ex:
                    Logger.info(f"Не удалось считать канал на строке - {counter}, проверьте введенные данные!", self.red)
                counter += 1

class AccountsJson:

    @staticmethod
    def check_exists_json_accounts():
        if not os.path.exists("accounts.json"):
            with open("accounts.json", "w") as json_file:
                json_file.write(json.dumps({"flood": [], "active": [], "bad": [], "limited": []}))

    @staticmethod
    def read_json_file(file):
        with open(file, "r") as json_file:
            return json.loads(json_file.read())

    @staticmethod
    def write_json_file(data, file):
        with open(file, "w") as json_file:
            json_file.write(json.dumps(data))

