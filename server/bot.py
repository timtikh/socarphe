from fuzzywuzzy import fuzz
import vk_api
import time
import csv


class VK:
    def __init__(self):
        self.vk_session = vk_api.VkApi('89850305757', 'Cgbhbljyjd01021979')
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

        self.counter = 0
        self.similarityOfWords = 75
        self.graph_users_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
        self.user_friend_list = []
        self.start_user = 0
        self.users_dict = dict()
        self.keywords = []
        self.result_users = dict()

        self.close_words = dict()
        self.added_words = []
        with open("words.csv", encoding="windows-1251") as file:
            reader = csv.reader(file)
            for row in reader:
                word, close_word = row[0].strip().lower(), row[1].strip().lower()
                if word in self.close_words:
                    self.close_words[word].add(close_word)
                else:
                    self.close_words[word] = {close_word}
        print(self.close_words.items())

    def getUrl(self):
        print("Введите адрес страницы, по которой нужно провести поиск")
        while True:
            user_URL = input("Ввод: ")
            if "https://vk.com" in user_URL or "vk.com" in user_URL:
                user_id = self.vk.utils.resolveScreenName(
                    screen_name=user_URL.replace("https://vk.com/", "", 1).replace("vk.com/", "", 1))
                if user_id["type"] == "user":
                    print("Произвожу поиск пользователей...")
                    return user_id["object_id"]
                else:
                    print("Ты ввел ссылку не на пользователя Вконтакте\n[Type = {}]".format(user_id["type"]))
            else:
                print("Что-то не так, попробуй ещё раз\n\n")

    def getKeyWords(self):
        print("Поиск человека происходит по определенным ключевым словам. Введи их через запятую")
        try:
            self.keywords = input().lower().split(",")
            for i in range(len(self.keywords)):
                self.keywords[i] = self.keywords[i].strip().lower()
            self.keywords = list(set(self.keywords))
            print("need To Add Words")
            self.needToAddWords()
            print("adding Words To Close Words")
            self.addWordsToCloseWords()

        except Exception as e:
            print("[get key words ERROR]", e)

    def saveCloseWords(self):
        with open("words.csv", "w", newline="", encoding="windows-1251") as file:
            writer = csv.writer(file)
            for el in self.close_words.items():
                print(el[0], el[1])
                for el1 in el[1]:
                    print(el[0], el1)
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

    def needToAddWords(self):
        for el in self.keywords:
            self.findCloseWords(el)
        print(f'Найдены схожие слова, введи их, если хочешь расширить поиск, иначе нажми "Enter"\n'
              f"Схожие слова: {', '.join(self.added_words)}")
        choose = input().strip().lower().split(",")
        for i in range(len(choose)):
            choose[i] = choose[i].strip().lower()
            if choose[i] != '':
                self.keywords.append(choose[i].strip().lower())
        self.keywords = list(set(self.keywords))

    def findUserFriends(self, user_id, counter, limiter=100, depth=1):
        if counter < depth:
            try:
                print(user_id)
                if user_id not in self.users_dict:
                    self.users_dict[user_id] = []
                self.groupAnalysis(user_id)

                self.user_friend_list = self.vk.friends.get(user_id=user_id, order="hints")
                counter_limiter = 0
                for user_friend in self.user_friend_list["items"]:
                    counter_limiter += 1

                    if user_friend in self.users_dict:
                        self.users_dict[user_friend].append(user_id)
                    else:
                        self.users_dict[user_friend] = [user_id]
                        # Пользователя нет, значит, мы ещё не обрабатывали его
                        self.findUserFriends(user_friend, counter + 1, limiter)
                    if counter_limiter >= limiter:
                        break
                self.counter += 1
            except vk_api.exceptions.ApiError:
                pass
                # пользователь был удален либо забанен

    def getUserGroups(self):
        pass

    # Сравнение слов
    def word_comparison(self, word, text):
        result = []
        counter = 0
        for el in text:
            result.append(fuzz.ratio(word, el))
        for el in result:
            if el >= self.similarityOfWords:
                counter += 1
        return counter

    def groupAnalysis(self, user_id, max_keyword_counter=0, max_groups_len=0, max_counter=100):
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
                for keyword in self.keywords:
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
            print(e)
            # if "This profile is private" in e:
            #     pass
            # else:
            #     print("[group analysis ERROR]", e)
            # print("[ERROR]", e)
            pass
