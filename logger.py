import os.path
from datetime import datetime


class Logger:
    reset = "\033[0m"
    prefix = f"%d-%m-%Y %H:%M:%S"

    @classmethod
    def info(cls, data, color, out_file=""):
        out_string = f"{datetime.now().strftime(cls.prefix)} | {data}"
        print(f"{color}{out_string}{cls.reset}")
        if out_file:
            cls.write_file(out_file, out_string)

    @staticmethod
    def write_file(file, out_string):
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as file:
                pass

        with open(file, "a", encoding="utf-8") as output_file:
            output_file.write(f"{out_string}\n")

