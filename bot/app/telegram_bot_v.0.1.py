#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

import csv
import time
import telebot
from ParsingVkApiRelis import *


# для полноценной работы бота нужно запустить три программы:
# parseBotRes.py
# SendResults.py
# telegram_bot_v.0.1.py

class User:
    def __init__(self, user_id, user_name, status, user_condition, keywords):
        self.id = user_id
        self.name = user_name
        # default/prime/
        self.status = status
        # chatting/enteringKeywords/addingKeywords/enteringId
        self.condition = user_condition
        self.keywords = keywords


def readFile():
    with open("tgusersStatus.csv") as file:
        csvReader = csv.reader(file)
        for row in csvReader:
            tgUsers[int(row[0])] = {"status": row[1], "condition": row[2], "keywords": row[3].split(";")}


def writeFile():
    with open("tgusersStatus.csv", "w", newline='') as file:
        csvWriter = csv.writer(file)
        for userInfo in tgUsers.items():
            csvWriter.writerow([str(userInfo[0]), str(userInfo[1]["status"]), str(userInfo[1]["condition"]), ";".join(userInfo[1]["keywords"])])


def addArequestToTheQueue(finderId, user_id, user_status, keywords, link):
    with open("queue.csv", "a", newline='') as file:
        csvWriter = csv.writer(file)
        csvWriter.writerow([finderId, user_id, user_status, ";".join(keywords), link])


with open("settings.txt") as file:
    data = file.readlines()

token = data[2].strip()
bot = telebot.TeleBot(token)
tgUsers = dict()
depth_depends_on_the_status = {"default": 2, "prime": 3, "superPrime": 4}

readFile()
writeFile()

with open("queue.csv", "w", newline='') as file:
    pass


# Проверка на то, есть ли пользователь в системе
def isRegistered(user_id):
    # Обращение к дб
    # Пока что стоит заглушка

    # Если польщзователь есть в системе, возвращает кортеж (True, "статус")
    # Иначе возвращает кортеж (False, None)
    return True, "default"


def registration(user_id):
    # Регистрация и сохрание пользователя в дб
    # Пока что стоит заглушка
    return True, "default"


def registrationOrAuthorisation(user_id):
    userInfo = isRegistered(user_id)
    is_user_registered = userInfo[0]
    user_status = userInfo[1]
    if is_user_registered:
        pass
    else:
        userInfo = registration(user_id)
        is_user_registered = userInfo[0]
        user_status = userInfo[1]
    return user_status


@bot.message_handler(content_types=["text"])
def send_welcome(message):
    text = message.text
    user_name = message.from_user.username
    user_id = message.from_user.id
    user_status = registrationOrAuthorisation(user_id)
    if user_id not in tgUsers:
        tgUsers[user_id] = {"status": "default", "condition": "chatting", "keywords": ""}
    user_status = tgUsers[user_id]["status"]
    user_condition = tgUsers[user_id]["condition"]
    user_keywords = tgUsers[user_id]["keywords"]
    #                user_id, user_name, status, user_condition, keywords):
    userClass = User(user_id, user_name, user_status, user_condition, user_keywords)

    splited_text = text.split(" ", 1)
    if splited_text[0] == "/start" and len(splited_text) == 1:
        result = "Добро пожаловать в *Socarphe.*\n\n" \
                 "• Хочешь посмотреть все доступные команды? Отправь мне */info*.\n" \
                 "• Хочешь начать поиск человека? Отправь мне */find*\n" \
                 "• Хочешь поменять свой статус? Отправь мне */changeStatus*"
        bot.send_message(message.from_user.id, result, parse_mode='Markdown')
    elif splited_text[0] == "/info" and len(splited_text) == 1:
        result = "• Хочешь посмотреть все доступные команды? Отправь мне */info*.\n" \
                 "• Хочешь начать поиск человека? Отправь мне */find*\n" \
                 "• Хочешь поменять свой статус? Отправь мне */changeStatus*"
        bot.send_message(message.from_user.id, result, parse_mode='Markdown')
    elif splited_text[0] == "/find" and len(splited_text) == 1:
        userClass.condition = "enteringKeywords"
        result = "Введи ключевые слова через запятую, по которым хочешь осуществить поиск"
        bot.send_message(message.from_user.id, result, parse_mode='Markdown')
    elif splited_text[0] == "/changeStatus" and len(splited_text) == 1:
        if userClass.status == "default":
            userClass.status = "prime"
            now_status = "Премиум"
        else:
            userClass.status = "default"
            now_status = "Обычный"
        result = 'Ты поменял свой статус на *"{}"*'.format(now_status)
        bot.send_message(message.from_user.id, result, parse_mode='Markdown')

    else:
        result = "Извини, я вряд ли могу как-то ответить тебе🙁"
        if userClass.condition == "enteringKeywords":
            userClass.keywords = text.lower().split(",")
            wordFH = wordFindHelper()
            wordFH.needToAddWords(userClass.keywords)
            if len(wordFH.added_words) > 0:
                result = 'Найдены схожие слова, введи их, если хочешь расширить поиск, иначе отправь "Нет"\nСхожие слова: {}'.format(', '.join(wordFH.added_words))
                userClass.condition = "addingKeywords"
            else:
                result = "Осталось только отправить мне ссылку на страницу ВК, откуда начнешь поиск."
                userClass.condition = "enteringId"
        elif userClass.condition == "addingKeywords":
            if text.lower() != "нет":
                for word in text.lower().split(";"):
                    userClass.keywords.append(word)
                userClass.keywords = list(set(userClass.keywords))

            result = "Осталось только отправить мне ссылку на страницу ВК, откуда начнешь поиск."
            userClass.condition = "enteringId"
        elif userClass.condition == "enteringId":
            result = "Ты добавлен в очередь. Загляни сюда позже"
            t = time.time()
            addArequestToTheQueue(str(int(t)) + str(t - int(t))[2:], userClass.id, userClass.status, userClass.keywords,
                                  text)
            userClass.condition = "chatting"

        bot.send_message(message.from_user.id, result, parse_mode='Markdown')
        

    tgUsers[userClass.id] = {"status": userClass.status, "condition": userClass.condition, "keywords": userClass.keywords}
    writeFile()


if __name__ == "__main__":
    bot.polling()
