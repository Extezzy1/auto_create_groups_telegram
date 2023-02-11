# -*- coding: utf-8 -*
import json
import os

counter = 0
dirname = "sessions"
listdir = os.listdir(dirname)
for item in listdir:
    if item.split(".")[1] == "json":
        with open(f"{dirname}/{item}", 'r') as json_file:
            json_: dict = json.loads(json_file.read())
        if json_.pop("ProxyAccount", False):
            with open(f"{dirname}/{item}", "w") as json_write:
                json_write.write(json.dumps(json_))
                counter += 1

print(f"Отвязал {counter} прокси!")
input("нажмите enter")