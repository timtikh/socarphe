
# socarphe - быстрый поиск эксперта.


## Введение
в данном документе cодержится описание проекта, его архитектура, частичный "Domain Analysis" и другие особенности

## Содержание

## Проблема

в небольшой проект/startup сложно найти подходящего специалиста-энтузиаста,

## Решение

сервис по нахождению чувака через нетворкинг в соцсетях и анализ аккаунта пользователя


## (Не-)Функциональные требования


### Функциональные требования
#### F-0.0 Система должна получать от пользователя набор ключевых слов для поиска специалиста
#### F-0.1 Система должна проводить анализ друзей по переданной ссылке на аккаунт в соц. сети ВК на наличие людей с ключевыми словами
#### F-1. Система должна проводить поиск и анализ кандидатов от 5 до 20 минут(в зависимости от указанной глубины поиска)
#### F-2. Система должна выдавать результаты анализа в течечение 10 секунд после проведения поиска и анализа
#### F-3. Система должна запоминать кодовые слова, чтобы в дальнейшем предлагать пользователю дополнительные определения при вводе им кодовых слов
#### F-4. Система должна создавать 2 (две) очереди запросов на анализ пользователей

### Нефункциональные требования 
#### NF-0.1 Система должна обслуживать до 2 (двух) одновременных пользователей 
#### NF-0.2 Система должна быть горизонтально масштабируемой для увеличения числа одновременных пользователей 
#### NF-0.3 При большой нагрузке на систему(количество одновременно пользователей первышает максимально расчитаную планку), она не должна прекращать свою работу, а уведомлять пользователя, что на данный момент сервера перегружены и выводить пользователю предполагаемое время ожидания.
#### NF-1. Система должна быть доступна для просмотра с компьютера и со смартфона
#### NF-2. Новая учетная запись пользователя должна быть создана менее чем за 2000 ms

## Архитектура

Выбрали MVVM, потому что решили разделить проект на три самодостаточных блока - Сайт, БД и сервер поиска. Блоки коммуницируют только с соседним. Это сделано для того, чтобы далее расширять блоки View - сайт, TG-бот, VK-бот. 

 ### Компонентная модель (Model-View-ViewModel)
 
 ![alt text](GeneralArchitecture.png "GeneralArchitecture")

Блоки коммуницируют только с "соседом". У сайта нет доступа к сервверу поиска. База данных является прокладкой между сайтом и поиском. В ней сохраняются все результаты запросов, отображаются новые запросы.

 #### View (сайт)
 
 ![alt text](ViewAlg.png "ViewAlg")
 
 Сайт сделан с помощью стандартных фреймворков, от пользователя требуется только авторизация и данные по поиску. Сайт также используется для приобретения премиум-статуса. На БД запросы посылаются на PHP языке.
 
 ![alt text](ViewUser.png "ViewUser")
 
 для чего пользователь использует сайт
 
 ![alt text](ViewFramework.png "ViewUser")

основные используемые фреймворки

 #### ViewModel (БД)
 
 ![alt text](ViewModel.png "ViewModel")
 
 БД является относительно пассивным элементом. В ней хранятся учетные записи пользователей, прошлые запросы на поиск, запросы на новый поиск.
 
 #### Model (сервер поиска)
 
 Ниже подробное описание алгоритма поиска кандидатов
 
 ![alt text](ModelAlg.png "View")
 
 Ниже подробное описание проверки статуса пользователя для определения параметров поиска.
 
 ![alt text](ViewModelToModel.png "View")
 
 ## Референсные модели
 ## Осуществление доступа пользователя
 ## Use-Cases
 
 ### **Регистрация пользователя**
 #### 1. Пользователь заходит на сайт
 #### 2. Пользователь выбирает способ регистрации:
 ##### - 2FA по номеру телефона
 ##### - email + пароль
 ##### - авторизация через ВК
 #### 3. Система проверяет корректность данных
 #### 4. Система вносит пользователя в список
 #### 5. Система выдает пользователю сообщение об успешной авторизации
 #### **Результат**: пользователь успешно зарегистрирован, авторизован и может работать с системой.
 #### **Возможные ошибки**: некорректные данные для регистрации, недоступность БД;
 
 ### **Авторизация пользователя**
 #### 1. Пользователь заходит на сайт
 #### 2. Пользователь выбирает способ авторизации:
 ##### - 2FA по номеру телефона
 ##### - email + пароль
 ##### - авторизация через ВК
 #### 3. Система проверяет корректность данных
 #### 4. Система проверяет в БД существует ли такой пользователь
 #### 5. Система возвращает пользователю сообщение об успешной аввторизации
 #### **Результат**: пользователь успешно авторизован и может работать с системой.
 #### **Возможные ошибки**: некорректные данные входа, отсутствие пользователя в БД, недоступность БД;
 
 ### **Повышение статуса пользователя**
 #### 1. Пользователь успешно авторизуется
 #### 2. Пользователь выбирает доступные опции для повышения статуса:
 ##### - предоставление дополнительных личных данных
 ##### - выбор тарифного плана и оплата на странице банка
 #### 3. Система проверяет корректны ли данные или прошла ли оплата
 #### 4. Система вносит учетную запись пользователя пометку о повышении статуса
 #### 5. Система выдает пользователю сообщение об успешном повышении статуса и предлагает произвести улучшенный поиск
 #### **Результат**: пользователь успешно произвел апгрейд статуса и имеет дополнительные поисковые возможности
 #### **Возможные ошибки**: некорректные предоставленные данные, не произошла оплата, недоступность БД;
 
 ### **Оформление поискового запроса**
 #### 1. Пользователь успешно авторизуется
 #### 2. Пользователю предлагаются в зависимости от его статуса опции поиска:
 ##### - поик 3-ех кандидатов по ключевым словам
 ##### - поиск 20-ти кандидатов по ключевым словам
 ##### - поиск 100 кандидатов по ключевым словам
 #### 3. Система вносит в БД запрос на поиск нужной глубины
 #### 4. Система выводит пользователю предполагаемое время ожидания и предлагает прислать уведомление по окончанию поиска
 #### 5. Система выдает пользователю список подходящих кандидатур с ссылками на их страницы
 #### 6. Система предлагает пользователю попробовать повторный поиск по ключевым словам, которые она считает более актуальными для поиска
 #### **Результат**: пользователь произвел поиск и получил список кандидатов в проект/startup.
 #### **Возможные ошибки**: недоступность БД;
 
 
 ## Конкуренты
 
 ## Клиенты и пользователи

