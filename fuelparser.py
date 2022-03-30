from bs4 import BeautifulSoup
import requests
import csv
from alive_progress import alive_bar
import time
import datetime
from pprint import pprint

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email import encoders
from email.mime.base import MIMEBase

import os


class Core:
    headers = {"UserAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.2.773 Yowser/2.5 Safari/537.36'
               }

    token = "AQAAAABeXGbRAADLW7WU-AHo70SInN8fGZa6Yxo"
    url = "https://fuelprices.ru/ceny-na-benzin-v-gorodah-rossii"

    def __init__(self, bar):
        self.response = requests.get(url=self.url, headers=self.headers)
        self.data = []
        self.bar = bar
        self.for_bar = ()

        self.smtp = {"host": "smtp.yandex.com",
                     "password": "83ec2657",
                     "login": "metox73work@yandex.ru"}

    def __str__(self):
        print(f'{self.__class__.__name__}')

    def show_bar(self):
        process = self.for_bar[0]
        items = self.for_bar[1]

        with alive_bar(items, force_tty=True, manual=False, title=f'{process}') as bar:
            for i in range(items):
                time.sleep(0.01)
                bar()

    @staticmethod
    def console_had():
        print("\033[33m{}".format("________Welcome to the fuel-parser by metox73________"), "\033[0m")
        print()

    @staticmethod
    def info():
        print("|===================================================|")
        print("| 1. send on email - 'send on email'                |")
        print("| 2. save table in csv file - 'save'                |")
        print("| 3. show connection status code - 'status code'    |")
        print("| 4. output the data to the console - 'print data'  |")
        print("| 5. exit the parser - 'exit'                       |")
        print("|===================================================|")
        print()

    def status_resp(self):
        rsc = self.response.status_code

        if self.bar == "on":
            self.for_bar = ("getting the status code", rsc)
            self.show_bar()

        if rsc == 200:
            print("\033[32m{}".format("status code: " + str(rsc)), "\033[0m")

        else:
            print("\033[33m{}".format("status code:", str(rsc)), "\033[0m")

    def get_data(self):
        soup = BeautifulSoup(self.response.text, "lxml")
        table = soup.find("table", id="prices")
        data_td = table.find_all("tr")

        for row in data_td:
            row.find_all("row")
            table_body = (row.text.strip().split("\n"))
            srt_tb = []

            for el in table_body:
                srt_tb.append(el.replace("\xa0\xa0", ""))

            self.data.append(srt_tb)

        if self.bar == "on":
            self.for_bar = ("data mining", len(data_td))
            self.show_bar()

    def print_data(self):
        pprint(self.data)

    def save_on_file(self):
        now = datetime.datetime.now()
        path = os.getcwd()

        if os.path.exists('data'):
            print("data directory exists...")
        else:
            os.mkdir(path + "/data")

        with open(file="data/data"+f"({now.strftime('%d-%m-%y')})"+".csv", mode="w", encoding="cp1251", errors="ignore") as file:
            writer = csv.writer(file, delimiter=";")

            for row in self.data:
                writer.writerow(row)

        if self.bar == "on":
            self.for_bar = ("saving", len(self.data))
            self.show_bar()

    def send_on_email(self, address_to, f_type):

        msg = MIMEMultipart()
        msg["From"] = self.smtp["login"]
        msg["To"] = address_to
        msg["Subject"] = "FUEL-PARSER"
        msg.preamble = "Csv file with data on gasoline prices in the Russian Federation"

        if f_type == "csv":

            path = os.getcwd()
            files = os.listdir(f"{path}/data")
            files_map = {}

            for i in range(len(files)):
                files_map[i] = files[i]

            for i in files_map:
                print(f"{i}: {files_map[i]}")

            choose = int(input("Enter number one of the files: "))

            file_to_send = f"data/{files_map[choose]}"

            ctype, encoding = mimetypes.guess_type(file_to_send)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            fp = open(file_to_send, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=file_to_send)
            msg.attach(attachment)

        if f_type == "html_table":

            table = self.data
            result = ''
            body = "table with data on the cost of gasoline in the regions of the russian federation"

            msg = MIMEMultipart()  # Создаем сообщение
            msg['From'] = self.smtp["login"]  # Адресат
            msg['To'] = address_to  # Получатель
            msg['Subject'] = 'FUEL-PARSER'  # Тема сообщения

            msg.attach(MIMEText(body, 'plain'))  # Добавляем в сообщение текст

            for i in table:
                result += f"<tr><td>{i[0]}</td><td>{i[1]}</td><td>{i[2]}</td><td>{i[3]}</td><td>{i[4]}</td></tr>"

            html = f"""\
            <html>
              <head></head>
              <body>
                    <table border="1">
                        {result}
                    </table>
              </body>
            </html>
            """

            msg.attach(MIMEText(html, 'html', 'utf-8'))  # Добавляем в сообщение HTML-фрагмент

        server = smtplib.SMTP(self.smtp["host"])
        server.starttls()
        server.login(self.smtp["login"], self.smtp["password"])
        server.sendmail(self.smtp["login"], address_to, msg.as_string())
        server.quit()

        if self.bar == "on":
            self.for_bar = ("sending", len(self.data))
            self.show_bar()

        print("\033[32m{}".format("successful..."), "\033[0m")


if __name__ == "__main__":

    parser = Core(bar="on")

    parser.console_had()
    parser.info()

    parser.get_data()

    flag = True

    while flag is True:

        tmp = input("Enter one is the command: ")

        if tmp == "send on email":
            email = input("Enter email address: ")
            _type_ = input('Enter the format ("csv" or "html_table"): ')
            parser.send_on_email(email, _type_)

        elif tmp == "save":
            parser.save_on_file()

        elif tmp == "print data":
            parser.print_data()

        elif tmp == "status code":
            parser.status_resp()

        elif tmp == "exit":
            flag = False
        else:
            print("\033[33m{}".format("ERROR...", "\033[0m"))