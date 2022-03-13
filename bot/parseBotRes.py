#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import csv
from ParsingVkApiRelis import *

with open("settings.txt") as file:
    data = file.readlines()
    LOGIN = data[0].strip()
    PASSWORD = data[1].strip()
    depths = list(map(int, data[3].strip().split(',')))
    # depths = data[3].strip().split(',')
    counters = list(map(int, data[4].strip().split(',')))

vkBot = VKparserBot(login=LOGIN, password=PASSWORD)
wfh = wordFindHelper()
depth_depends_on_the_status = {"default": depths[0], "prime": depths[1], "superPrime": depths[2]}
count_of_friends = {"default": counters[0], "prime": counters[1], "superPrime": counters[2]}


def service(users_list, user_status):
    depth = int(depth_depends_on_the_status[user_status])
    for el in users_list:

        if el[0] not in trash:
            trash.add(el[0])
            tg_id = el[1]["tg_id"]
            keywords = wfh.getKeyWords(el[1]["keywords"])
            link = el[1]["link"]
            if "https://vk.com" in link or "vk.com" in link:
                vk_user_id = vkBot.vk.utils.resolveScreenName(
                    screen_name=link.replace("https://vk.com/", "", 1).replace("vk.com/", "", 1))
                if vk_user_id["type"] == "user":
                    vkBot.prepareForParsing()
                    vkBot.findUserFriends(user_id=vk_user_id["object_id"], counter=0, depth=depth, keywords=keywords)
                    result = []
                    for vkItEl in vkBot.result_users.items():
                        result.append((vkItEl[0], vkItEl[1]["count"], vkItEl[1]["first_name"], vkItEl[1]["last_name"]))
                    with open("resultQueue.csv", "a", newline='') as file:
                        writer = csv.writer(file)
                        res = ""
                        result.sort(key=lambda x: -x[1])
                        how_many_friends = count_of_friends[user_status]
                        # result = [(int(<vk_group1_id>), <int(number_of_matches_in_group1)>),
                        #           (int(<vk_group2_id>), <int(number_of_matches_in_group2)>), ...]
                        print("time_id", el[0])
                        for resEl in result:
                            if how_many_friends > 0:
                                res += str(resEl[0]) + "-" + str(resEl[1]) + "-" + str(resEl[2]) + "-" + str(resEl[3]) + ";"
                                how_many_friends -= 1
                            else:
                                break
                        print(tg_id, user_status, res[:-1])
                        print("--------------------------\n\n")
                        # print([el[0], tg_id, user_status, res[:-1]])
                        writer.writerow([el[0], tg_id, user_status, res[:-1]])
                    # print("result_users:", vkBot.result_users)
                    # return vk_user_id["object_id"]
                else:
                    # print("Ты ввел ссылку не на пользователя Вконтакте\n[Type = {}]".format(vk_user_id["type"]))
                    pass


def readQueue():
    with open("queue.csv") as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                users[row[2]][int(row[0])] = {"tg_id": int(row[1]), "keywords": row[3].split(";"), "link": row[4]}
            except KeyError:
                users[row[2]] = dict()
                users[row[2]][int(row[0])] = {"tg_id": int(row[1]), "keywords": row[3].split(";"), "link": row[4]}
    with open("queue.csv", "w") as file:
        pass


def saveQueue(users):
    with open("queue.csv", "w") as file:
        writer = csv.writer(file)
        if len(users["prime"]) > 0:
            for el in users["prime"].items():
                queue_time, tg_id, status, keywords, link = el[0], el[1]["tg_id"], "prime", \
                                                            ";".join(el[1]["keywords"]), el[1][link]
                writer.writerow([queue_time, tg_id, status, keywords, link])
        if len(users["default"]) > 0:
            for el in users["default"].items():
                queue_time, tg_id, status, keywords, link = el[0], el[1]["tg_id"], "default", \
                                                            ";".join(el[1]["keywords"]), el[1][link]
                writer.writerow([queue_time, tg_id, status, keywords, link])


if __name__ == "__main__":
    with open("queue.csv", "w") as file:
        pass
    trash = set()
    while True:
        users = {"default": dict(), "prime": dict()}

        with open("queue.csv") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    users[row[2]][int(row[0])] = {"tg_id": int(row[1]), "keywords": row[3].split(";"), "link": row[4]}
                except KeyError:
                    users[row[2]] = dict()
                    users[row[2]][int(row[0])] = {"tg_id": int(row[1]), "keywords": row[3].split(";"), "link": row[4]}

        # Обслуживаем премиум пользователей
        if len(users["prime"]) != 0:
            users_list = sorted(list(users["prime"].items()), key=lambda x: x[0])
            while len(users_list) > 0:
                service(users_list, "prime")
                # print(1, service(users_list, "prime"))
                del users["prime"][users_list[0][0]]
                try:
                    del users_list[0]
                except:
                    break
        # Обслуживаем обычных пользователей
        elif len(users["default"]) != 0:
            users_list = sorted(list(users["default"].items()), key=lambda x: x[0])
            while len(users_list) > 0:
                service(users_list, "default")
                # print(0, service(users_list, "default"))
                del users["default"][users_list[0][0]]
                try:
                    del users_list[0]
                except:
                    break
