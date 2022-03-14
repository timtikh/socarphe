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
                    try:
                        requestId, tg_id, user_status, users_res_list = int(row[0]), row[1], row[2], row[3].split(";")
                        error_code = None
                    except IndexError:
                        requestId, tg_id, error_code = int(row[0]), row[1], row[2]
                    if requestId in trash:
                        continue
                    else:
                        trash.add(requestId)
                    if error_code is None:
                        if user_status == "default":
                            counter = 2
                        else:
                            counter = 5
                        try:
                            text = "*Найдены нужные пользователи!*\n\n\n"
                            for el in users_res_list:
                                user_vk_info = el.split("-")
                                vk_id, match, first_name, last_name = user_vk_info[0], user_vk_info[1], user_vk_info[2], user_vk_info[3]
                                if counter > 0:
                                    text += "{} {}\nСовпадений: {}\nСслыка: https://vk.com/id{}\n\n".format(first_name, last_name, match, vk_id)
                                    counter += 1
                                else:
                                    break
                        except IndexError:
                            text = "*Произошла ошибка при поиске пользователей!*\n\nВозможно, ты кинул ссылку на группу или на закрытый аккаунт. Попробуй повторить запрос."
                    else:
                        if error_code == "NOT_USER_ERROR":
                            text = "*Произошла ошибка при поиске пользователей!*\n\nВозможно, ты кинул ссылку на группу или на закрытый аккаунт. Попробуй повторить запрос."
                        elif error_code == "PRIVATE_USER_ERROR":
                            text = "*Произошла ошибка при поиске пользователей!*\n\nВозможно, ты кинул ссылку на удаленный или закрытый аккаунт. Попробуй повторить запрос."
                        else:
                            text = "*Произошла ошибка при поиске пользователей!*\n\nКажется. Ты кинул ссылку на сторонний сайт.\n\nПопробуй повторить запрос."
                    if tg_id is not None:
                        bot.send_message(int(tg_id), text, parse_mode='Markdown')
        except FileNotFoundError:
            pass
