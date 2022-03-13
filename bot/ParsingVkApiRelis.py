#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from fuzzywuzzy import fuzz
import vk_api
import csv


class VKparserBot:
    def __init__(self, login: str, password: str):
        if login is None or password is None or type(login) != str or type(password) != str:
            raise Exception("Login and password must str")
        self.vk_session = vk_api.VkApi(login, password)
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()
        
    def prepareForParsing(self):
        self.similarityOfWords = 75
        self.user_friend_list = []
        self.users_dict = dict()
        self.keywords = []
        self.result_users = dict()
        self.close_words = dict()
        self.added_words = []

        # loading close words
        try:
            with open("words.csv", encoding="windows-1251") as file:
                reader = csv.reader(file)
                for row in reader:
                    # row = [word, closeToThatWord]
                    word, close_word = row[0].strip().lower(), row[1].strip().lower()
                    if word in self.close_words:
                        self.close_words[word].add(close_word)
                    else:
                        self.close_words[word] = {close_word}
        except FileNotFoundError:
            with open("words.csv", "w", encoding="windows-1251") as file:
                pass

    def findUserFriends(self, user_id=None, counter=0, depth=2, keywords=None, limiter=100):
        if user_id is None:
            raise Exception("user_id must int")
        if keywords is None:
            raise Exception("keywords must be list or set")
        if counter <= depth:
            try:
                if user_id not in self.users_dict:
                    self.users_dict[user_id] = []

                self.groupAnalysis(user_id, keywords=keywords)

                if counter < depth:
                    # Getting a list of friends
                    self.user_friend_list = self.vk.friends.get(user_id=user_id, order="hints")
                    counter_limiter = 0
                    for user_friend in self.user_friend_list["items"]:
                        counter_limiter += 1
                        user_info = self.vk.users.get(user_id=user_friend, extended=1)

                        try:
                            print(f"{counter_limiter}. {user_friend}({user_id})", user_info[0]["first_name"], user_info[0]["last_name"],
                                  f"({counter}/{depth})")
                        except UnicodeEncodeError as e:
                            print(e)


                        # users_dict = {user: [list_of_his_"parent"]}
                        if user_friend in self.users_dict:
                            self.users_dict[user_friend].append(user_id)
                        else:
                            self.users_dict[user_friend] = [user_id]

                            # There is no user, so we haven't processed it yet
                            self.findUserFriends(user_id=user_friend, counter=counter + 1, depth=depth, keywords=keywords, limiter=limiter)
                        if counter_limiter >= limiter:
                            break
            except vk_api.exceptions.ApiError as e:
                print(e)
                # the user has been deleted or banned
                pass

    # Word comparison
    def word_comparison(self, word, text):
        result = []
        counter = 0
        for el in text:
            result.append(fuzz.ratio(word, el))
        for el in result:
            if el >= self.similarityOfWords:
                counter += 1
        return counter

    def groupAnalysis(self, user_id, keywords=None, max_keyword_counter=0, max_groups_len=0, max_counter=100):
        if keywords is None:
            raise Exception("keywords mas be list of set")
        keywords = list(keywords)
        try:
            result = {"count": 0, "groups_id": []}
            groups_list = self.vk.groups.get(user_id=user_id, extended=1,
                                             fields=["id", "name", "status", "description"])
            groups_counter = 0
            for group in groups_list["items"]:
                groups_counter += 1
                keywordCounter = 0
                group_id = group["id"]
                group_name = group["name"].lower()
                group_screen_name = group["screen_name"].lower()
                try:
                    group_status = group["status"].lower()
                except Exception:
                    group_status = ""

                try:
                    group_description = group["description"].lower()
                except Exception:
                    group_description = ""
                for keyword in keywords:

                    if (self.word_comparison(keyword, group_name.split()) > 0) or \
                            (self.word_comparison(keyword, group_screen_name.split()) > 0) or \
                            (self.word_comparison(keyword, group_status.split()) > 0) or \
                            (self.word_comparison(keyword, group_description.split()) > 0):
                        keywordCounter += 1
                if keywordCounter > max_keyword_counter:
                    result["count"] += 1
                    result["groups_id"].append(group_id)

                if groups_counter >= max_counter:
                    break

            if result["count"] > max_groups_len:
                self.result_users[user_id] = result

        except Exception as e:
            pass


class wordFindHelper:
    def __init__(self):
        self.keywords = []
        self.added_words = []
        self.close_words = dict()
        try:
            with open("words.csv", encoding="windows-1251") as file:
                reader = csv.reader(file)
                for row in reader:
                    word, close_word = row[0].strip().lower(), row[1].strip().lower()
                    if word in self.close_words:
                        self.close_words[word].add(close_word)
                    else:
                        self.close_words[word] = {close_word}
        except Exception:
            with open("words.csv", "w", encoding="windows-1251") as file:
                pass

    # preparing keywords
    def getKeyWords(self, keywords):
        kw = []
        for i in range(len(keywords)):
            keywords[i] = keywords[i].strip()
            for word in keywords[i].split():
                kw.append(word)
        self.keywords = list(set(kw))
        return self.keywords

    # saving close words
    def saveCloseWords(self):
        with open("words.csv", "w", newline="", encoding="windows-1251") as file:
            writer = csv.writer(file)
            for el in self.close_words.items():
                # self.close_words.items() = [
                # (word1, [closeWord11, closeWord12]), (word2, [closeWord21, closeWord22]), ...
                # ]
                for el1 in el[1]:
                    writer.writerow([el[0], el1])

    def findCloseWords(self, word):
        if word in self.close_words:
            for el in list(self.close_words[word]):
                self.added_words.append(el)
        self.added_words = list(set(self.added_words))

    def addWordsToCloseWords(self):
        i, j, lkwrds = 0, 0, len(self.keywords)
        while i < lkwrds:
            word = self.keywords[i]
            while j < lkwrds:
                if i != j:
                    close_word = self.keywords[j]
                    if word in self.close_words:
                        self.close_words[word].add(close_word)
                    else:
                        self.close_words[word] = set()
                        self.close_words[word].add(close_word)
                j += 1
            i += 1
            j = 0

    def needToAddWords(self, keywords):
        self.getKeyWords(keywords)
        for el in self.keywords:
            self.findCloseWords(el)


if __name__ == "__main__":
    wfh = wordFindHelper()
    vkBot = VKparserBot(login="<LOGIN>", password="<PASSWORD>")

    # depth = 1  -  analise only one "layer" of friends
    depth = 1
    keywords = ["word1", "word2"]
    vk_start_user_id = vkBot.vk.utils.resolveScreenName(
        screen_name="https://vk.com/<user_vk_id>".replace("https://vk.com/", "").replace("vk.com/", ""))["object_id"]
    vkBot.findUserFriends(user_id=vk_start_user_id, counter=0, depth=depth, keywords=wfh.getKeyWords(keywords))
    # returns a tuple:
    # ((needed_user1_id, {'count': user1 number of matches, 'groups_id': list of user1's groups where was the match}),
    # (needed_user2_id, {'count': user2 number of matches, 'groups_id': list of user2's groups where was the match})
    # ...)
    # print(vkBot.result_users.items())
