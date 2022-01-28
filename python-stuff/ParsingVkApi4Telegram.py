import vk_api
import time


class VK:
    def __init__(self):
        self.vk_session = vk_api.VkApi('login', 'password')
        self.vk_session.auth()
        self.vk = self.vk_session.get_api()

        self.counter = 0
        self.graph_users_dict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
        self.user_friend_list = []
        self.start_user = 0
        self.users_dict = dict()
        self.keywords = []
        self.result_users = dict()

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
            for el in range(len(self.keywords)):
                self.keywords[el] = self.keywords[el].strip().lower()
        except Exception as e:
            print("[get key words ERROR]", e)

    def test(self):
        pass

    def findUserFriends(self, user_id, counter, limiter=100, depth=3):
        # print(self.users_dict)
        if counter < depth:
            # print(user_id, counter)
            try:
                print(user_id)
                self.users_dict[user_id] = []
                self.groupAnalysis(user_id)
                # print(user_id)

                self.user_friend_list = self.vk.friends.get(user_id=user_id, order="hints")
                counter_limiter = 0
                for user_friend in self.user_friend_list["items"]:
                    counter_limiter += 1
                    # users_dict = {user: [list_of_his_"parent"]}
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

    def groupAnalysis(self, user_id, max_keyword_counter=0, max_groups_len=0, max_counter=100):
        try:
            # print(user_id)
            result = {"count": 0, "groups_id": []}
            groups_list = self.vk.groups.get(user_id=user_id, extended=1,
                                             fields=["id", "name", "status", "description"])
            # print(groups_list)
            groups_counter = 0
            for group in groups_list["items"]:
                groups_counter += 1
                # print(group)
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
                    if (keyword in group_name) or (keyword in group_screen_name) or (keyword in group_status) or \
                            (keyword in group_description):
                        keywordCounter += 1
                if keywordCounter > max_keyword_counter:
                    result["count"] += 1
                    result["groups_id"].append(group_id)

                if groups_counter >= max_counter:
                    break
            # print(groups_list)

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


# print(vk.wall.post(message='тест'))

if __name__ == "__main__":
    vk = VK()
    # vk.test()
    vk.getKeyWords()
    user_URL = vk.getUrl()
    startTime = time.time()
    # print(startTime)
    vk.findUserFriends(user_URL, 0, 150)
    endTime = time.time()
    # print(endTime)
    print("Время работы(в секундах) =", endTime - startTime)
    print("\n\n")
    k = -1
    print(vk.result_users)
    print("Найдено пользователей:", vk.counter)
