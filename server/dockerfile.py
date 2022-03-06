Dockerfile

# установка базового образа (host OS)
FROM python:3.8

# установка рабочей директории в контейнере
WORKDIR /socarphe/server

# копирование файла зависимостей в рабочую директорию
COPY requirements.txt .

# установка зависимостей
RUN pip install -r requirements.txt
RUN python3 -m pip install vk_api
RUN pip install fuzzywuzzy

# копирование содержимого локальной директории src в рабочую директорию
COPY src/ .

# команда, выполняемая при запуске контейнера
CMD [ "python", "./ParsingVkApiRelis.py" ]