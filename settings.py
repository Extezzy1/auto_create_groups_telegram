# -*- coding: utf-8 -*
import json
import os
import random
import re
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

    def __init__(self, path_to_channels, path_to_admins,
                 path_to_undeleted_channels, type_of_proxy, path_to_only_sending, path_to_edit_photo,
                 path_to_edit_title, path_to_send_message, path_to_delete_posts):
        self.file_log = "logs.txt"
        self.type_of_proxy = type_of_proxy
        self.path_to_admins = path_to_admins
        self.path_to_undeleted_channels = path_to_undeleted_channels
        self.path_to_channels = path_to_channels
        self.path_to_only_sending = path_to_only_sending
        self.path_to_edit_photo = path_to_edit_photo
        self.path_to_edit_title = path_to_edit_title
        self.path_to_send_message = path_to_send_message
        self.path_to_delete_posts = path_to_delete_posts
        self.count_created_channels = 0
        self.channels = []
        self.undeleted_channels = []
        self.only_sending_chats = []
        self.edit_title_chats = []
        self.edit_photo_chats = []
        self.edit_title_about_chats = []
        self.send_message = []
        self.delete_posts_chats = []
        self.admins = []
        self.send_media = []
        self.descriptions = []
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
        self.avatars = []
        AccountsJson.check_exists_json_accounts()
        self.load_sessions()
        self.load_proxies_from_txt()
        # self.bind_proxy()
        # self.delete_used_proxies_from_txt()
        # self.load_accounts()
        self.load_data()

    def read_avatars(self):
        self.avatars = []
        listdir = os.listdir("avatars")
        for file in listdir:
            self.avatars.append(file)

    def load_data(self):
        if not os.path.exists("data.json"):
            AccountsJson.write_json_file({}, "data.json")

    def read_video_and_photo_for_send(self):
        listdir = os.listdir("files/for_posts")
        for file in listdir:
            self.send_media.append(file)

    def read_send_message_txt(self):
        self.send_message = []
        with open(self.path_to_send_message, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                try:
                    line_split = line.strip().split(";")
                    chat_link = line_split[0]
                    message_text = re.sub(r"{(.+?)}", lambda x: random.choice(x.group(1).split("|")), line_split[1])
                    self.send_message.append([chat_link, message_text])
                except Exception:
                    pass

    def read_only_sending_chats(self):
        self.only_sending_chats = []
        with open(self.path_to_only_sending, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.only_sending_chats.append(line.strip())

    def read_edit_title_chats(self):
        self.edit_title_chats = []
        with open(self.path_to_edit_title, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                try:
                    line_split = line.strip().split(";")
                    chat_link = line_split[0]
                    chat_name = re.sub(r"{(.+?)}", lambda x: random.choice(x.group(1).split("|")), line_split[1])
                    self.edit_title_chats.append([chat_link, chat_name])
                except Exception:
                    pass

    def read_edit_photo_chats(self):
        self.edit_photo_chats = []
        with open(self.path_to_edit_photo, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.edit_photo_chats.append(line.strip())

    # Загрузка сессий
    def load_sessions(self):
        accounts = AccountsJson.read_json_file("accounts.json")
        self.sessions = []
        listdir = os.listdir('sessions')
        for file in listdir:
            if os.path.isfile(f"sessions/{file}"):
                if file.split(".")[1] == "session":
                    if file not in accounts["bad"] and file not in \
                            accounts["limited"] and file not in accounts["flood"] and file not in accounts["active"]:
                        accounts["active"].append(file)
        AccountsJson.write_json_file(accounts, "accounts.json")

    # Загрузка проксей из тхт файла
    def load_proxies_from_txt(self):
        with open('proxy.txt', 'r', encoding='utf-8') as read_file:
            lines = read_file.readlines()
            for line in lines:
                try:
                    line_split = line.strip().split(":")
                    if len(line_split) == 4:
                        proxy_ip = line_split[0]
                        proxy_port = int(line_split[1])
                        proxy_login = line_split[2]
                        proxy_password = line_split[3]
                        if self.type_of_proxy == "HTTP":
                            proxy = (socks.HTTP, proxy_ip, proxy_port, True, proxy_login, proxy_password)
                        elif self.type_of_proxy == "SOCKS":
                            proxy = (socks.SOCKS5, proxy_ip, proxy_port, True, proxy_login, proxy_password)
                        self.proxies.append(proxy)
                except:
                    Logger.info(f"Прокси {line.strip()} неверного формата!", self.red)

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
        try:
            # proxy_ip = proxy.split(':')[0]
            # proxy_port = int(proxy.split(':')[1])
            # proxy_login = proxy.split(':')[2]
            # proxy_password = proxy.split(':')[3].split('\n')[0]
            if os.path.exists(f'sessions/{session.split(".")[0]}.json'):
                with open(f'sessions/{session.split(".")[0]}.json', 'r', encoding='utf-8') as config_account:
                    json_ = json.loads(config_account.read())
                if json_.get("app_id", False) and json_.get("app_hash", False) and json_.get("app_version", False) and \
                        json_.get("sdk", False) and json_.get("device", False) and json_.get("system_lang_pack", False):

                    lang_code = json_.get("lang_code", "ru")
                    # if self.type_of_proxy == "HTTP":
                    #     proxy = (socks.HTTP, proxy_ip, proxy_port, True, proxy_login, proxy_password)
                    # elif self.type_of_proxy == "SOCKS":
                    #     proxy = (socks.HTTP, proxy_ip, proxy_port, True, proxy_login, proxy_password)
                    client = TelegramClient(session=f"sessions/{session}", api_id=json_["app_id"], api_hash=json_["app_hash"],
                                        app_version=json_["app_version"], system_version=json_["sdk"],
                                        device_model=json_["device"], lang_code=lang_code, system_lang_code=json_["system_lang_pack"], proxy=proxy)
                else:
                    Logger.info(f'Подан неверный json - {session.split(".")[0]}.json, перемещаю аккаунт в bad',self.red, out_file=self.file_log)
                    client = False
            else:
                client = False
            return client
        except Exception as ex:
            print(ex)

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

    def read_channels_from_txt(self, channel=False):
        with open(self.path_to_channels, "r", encoding="utf-8") as file_with_channels_read:
            lines = file_with_channels_read.readlines()
            counter = 1
            for line in lines:
                try:
                    if channel:
                        channel_name = re.sub(r"{(.+?)}", lambda x: random.choice(x.group(1).split("|")), channel)
                        channel_about = line.strip()
                        self.channels.append([channel_name, channel_about])
                    else:
                        line_split = line.strip().split(";")
                        channel_name = re.sub(r"{(.+?)}", lambda x: random.choice(x.group(1).split("|")), line_split[0])
                        channel_about = line_split[1]
                        self.channels.append([channel_name, channel_about])
                except Exception as ex:
                    Logger.info(f"Не удалось считать канал на строке - {counter}, проверьте введенные данные!", self.red)
                counter += 1

    def read_undeleted_channels(self):
        self.undeleted_channels = []
        with open(self.path_to_undeleted_channels, "r", encoding="utf-8") as file:

            lines = file.readlines()
            for line in lines:
                self.undeleted_channels.append(line.strip())

    def read_admins(self):
        with open(self.path_to_admins, "r", encoding="utf-8") as file:
            counter = 1
            lines = file.readlines()
            for line in lines:
                try:
                    line_split = line.strip().split(";")
                    channel_id = line_split[0]
                    admin_bot = line_split[1]
                    self.admins.append([channel_id, admin_bot])
                except Exception as ex:
                    Logger.info(f"Не удалось считать данные на строке - {counter}, проверьте введенные данные!",
                                self.red)
                counter += 1

    def read_delete_posts(self):
        with open(self.path_to_delete_posts, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.delete_posts_chats.append(line.strip())


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

