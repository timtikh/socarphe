#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import csv
import telebot


if __name__ == "__main__":
    with open("resultQueue.csv", "w") as file:
        pass
    with open("settings.txt") as file:
        data = file.readlines()

    token = data[2].strip()
    bot = telebot.TeleBot(token)
    trash = set()
    while True:
        try:
            with open("resultQueue.csv") as file:
                reader = csv.reader(file)
                tg_id, user_status, users_res_list = None, None, None
                for row in reader:
                    requestId, tg_id, user_status, users_res_list = int(row[0]), row[1], row[2], row[3].split(";")
                    if requestId in trash:
                        continue
                    else:
                        trash.add(requestId)

                    if user_status == "default":
                        counter = 2
                    else:
                        counter = 5
                    text = "*Найдены нужные пользователи!*\n\n\n"
                    for el in users_res_list:
                        user_vk_info = el.split("-")
                        vk_id, match, first_name, last_name = user_vk_info[0], user_vk_info[1], user_vk_info[2], user_vk_info[3]
                        if counter > 0:
                            text += "{} {}\nСовпадений: {}\nСслыка: https://vk.com/id{}\n\n".format(first_name, last_name, match, vk_id)
                            counter += 1
                        else:
                            break
                    if tg_id is not None:
                        bot.send_message(int(tg_id), text, parse_mode='Markdown')
        except FileNotFoundError:
            pass
