# импортируем библиотеки
from flask import Flask, request
import logging
import random
# import pygame
import sys
import csv
import requests
import os

# импортируем функции из других файлов
from scale import scale_object
# from map_foto import Map_image_id
from image_id_foto import image_id_map
from delete_image_id import delete_image_id_foto

# библиотека, которая нам понадобится для работы с JSON
import json

# создаём приложение
# мы передаём __name__, в нём содержится информация,
# в каком модуле мы находимся.
# В данном случае там содержится '__main__',
# так как мы обращаемся к переменной из запущенного модуля.
# если бы такое обращение, например, произошло внутри модуля logging,
# то мы бы получили 'logging'
app = Flask(__name__)

# Устанавливаем уровень логирования

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

# Создадим словарь, чтобы для каждой сессии общения с навыком хранились
# подсказки, которые видел пользователь.
# Это поможет нам немного разнообразить подсказки ответов
# (buttons в JSON ответа).
# Когда новый пользователь напишет нашему навыку, то мы сохраним
# в этот словарь запись формата
# sessionStorage[user_id] = {'question':('Черное море', 'море', 'easy',
#                                        '213044/09506ef2ef23e47e5cec',
#                                        '965417/a0758a57cd67d5bb5a0e')}

sessionStorage = {}


@app.route('/geo_test', methods=['POST'])
def geo_test():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog8(response, request.json)
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog8(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        # созда\м словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None,
            'choice': True,
            'choice_level': True,
            'start': None,
            'level': None,
            'bool': True,
            'answers': 0,
            'right_answers': 0,
            'wrong_answers': 0,
            'question': []
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь ещё не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name8(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
            # res['response']["tts"] = 'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
            first_name = get_first_name8(req)
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' + first_name.title() \
                          + '. Я - Алиса.\n Хочешь пройти географический тест?\n \
                        Если не хочешь проходить тест, то \
                        нажми или набери "нет".'
            res['response']["tts"] = 'Приятно познакомиться, ' + \
                                     first_name.title() \
                                     + '. Я - Алиса.\n Хочешь пройти географический тест?\n \
                        Если не хочешь проходить тест, то \
                        нажми или набери "нет".'

            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
        return

    if sessionStorage[user_id]['choice']:

        if 'да' in req['request']['nlu']['tokens']:
            res['response']['text'] = sessionStorage[user_id][
                                          'first_name'].title() + '! Для того, чтобы выбрать \
                    уровень сложности теста, необходимо нажать \
                    на одну из кнопок "Легкий" или "Трудный"'
            res['response']["tts"] = sessionStorage[user_id][
                                         'first_name'].title() + '! Для того, чтобы выбрать \
                    уровень сложности теста, необходимо нажать \
                    на одну из кнопок "Легкий" или "Трудный".'
            sessionStorage[user_id]['choice'] = False
            res['response']['buttons'] = [
                {
                    'title': 'Легкий',
                    'hide': True
                },
                {
                    'title': 'Трудный',
                    'hide': True
                }
            ]
            return

        elif 'нет' in req['request']['nlu']['tokens']:
            sessionStorage[user_id]['choice'] = False

            # прощаемся и заканчиваем сессию (можно картинку)
            res['response']['text'] = 'Спасибо за внимание'
            res['response']["tts"] = 'Спасибо за внимание'
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['image_id'] = '1540737/4c57cb876e3f41f7cef2'

            res['response']['end_session'] = True

            return


        else:
            res['response']['text'] = sessionStorage[user_id][
                                          'first_name'].title() + '! Ты не сказал ни да, ни нет!'

            res['response']["tts"] = sessionStorage[user_id][
                                         'first_name'].title() + '! Ты не сказал ни да, ни нет!'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]

    if sessionStorage[user_id]['choice_level']:

        if 'легкий' in req['request']['nlu']['tokens']:
            file_name = os.path.join('mysite', 'base1.csv')
            sessionStorage[user_id]['question'] = open_file(file_name, 'easy')

            sessionStorage[user_id]['level'] = 'easy'
            sessionStorage[user_id]['choice_level'] = False

        elif 'трудный' in req['request']['nlu']['tokens']:
            file_name = os.path.join('mysite', 'base1.csv')
            sessionStorage[user_id]['question'] = open_file(file_name, 'hard')

            sessionStorage[user_id]['level'] = 'hard'
            sessionStorage[user_id]['choice_level'] = False

        else:
            res['response']['text'] = sessionStorage[user_id][
                                          'first_name'].title() + '! Ты не выбрал сложность теста!'

            res['response']["tts"] = sessionStorage[user_id][
                                         'first_name'].title() + '! Ты не выбрал сложность теста!'
            res['response']['buttons'] = [
                {
                    'title': 'Легкий',
                    'hide': True
                },
                {
                    'title': 'Трудный',
                    'hide': True
                }
            ]

    if not sessionStorage[user_id]['bool']:
        # если согласился продолжить тест, выбираем уровень
        if get_answer(req) == 'да':
            sessionStorage[user_id]['bool'] = False
            if sessionStorage[user_id]['level'] == 'hard':
                sessionStorage[user_id]['level'] = 'easy'
            else:
                sessionStorage[user_id]['level'] = 'hard'

            file_name = os.path.join('mysite', 'base1.csv')
            sessionStorage[user_id]['question'] = open_file(file_name, \
                                                            sessionStorage[user_id]['level'])

        if get_answer(req) == 'нет':
            # прощаемся и заканчиваем сессию (можно картинку)
            res['response']['text'] = 'Спасибо за внимание'
            res['response']["tts"] = 'Спасибо за внимание'
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['image_id'] = '1540737/4c57cb876e3f41f7cef2'

            res['response']['end_session'] = True

            return

    if get_search_word(req, 'конец'):
        # прощаемся и заканчиваем сессию (можно картинку)
        res['response']['text'] = 'Спасибо за внимание'
        res['response']["tts"] = 'Спасибо за внимание'
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = '1540737/4c57cb876e3f41f7cef2'
        # если преждевременный выход, то показываем результат
        if sessionStorage[user_id]['question']:
            res['response']['card']['title'] = 'Количество вопросов : ' + \
                                               str(sessionStorage[user_id]['answers']) + \
                                               '\nКоличество правильных ответов : ' + \
                                               str(sessionStorage[user_id]['right_answers']) + \
                                               '\nКоличество не правильных ответов : ' + \
                                               str(sessionStorage[user_id]['wrong_answers'])

        sessionStorage[user_id]['bool'] = False
        sessionStorage[user_id]['question'] = []
        res['response']['end_session'] = True

        return

    if get_search_word(req, 'старт') or get_search_word(req, 'Продолжить'):
        sessionStorage[user_id]['start'] = True

    if sessionStorage[user_id]['start'] is None:
        res['response']['text'] = sessionStorage[user_id][
                                      'first_name'].title() + \
                                  '. Я буду показывать карту,\n а ты напишешь название объекта.\n' \
                                  'Для завершения игры нажми Конец игры.\n' \
                                  'Для начала игры нажми Старт'

        res['response']["tts"] = sessionStorage[user_id][
                                     'first_name'].title() + \
                                 '. Я буду показывать карту,\n а ты напишешь название объекта.\n' \
                                 'Для завершения игры нажми Конец игры.\n' \
                                 'Для начала игры нажми Старт'
        res['response']['buttons'] = [
            {
                'title': 'СТАРТ',
                'hide': True
            },
            {
                'title': 'Конец игры',
                'hide': True
            }
        ]
        return

    if sessionStorage[user_id]['question']:
        #  список вопросов не пустой, задаем вопросы
        if sessionStorage[user_id]['start']:
            # задаем первый вопрос (можно картинку)
            res['response']['text'] = 'Что это за ' + sessionStorage[user_id] \
                ['question'][0][1] + ' ?'

            res['response']["tts"] = 'Что это за ' + sessionStorage[user_id] \
                ['question'][0][1] + ' ?'
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'

            res['response']['card']['image_id'] = sessionStorage[user_id] \
                ['question'][0][2]

            res['response']['card']['title'] = 'Что это за ' + \
                                               sessionStorage[user_id]['question'][0][1] + '?'
            sessionStorage[user_id]['start'] = False

            return

        else:

            # Прверяем правильность ответа
            if get_search_word(req, sessionStorage[user_id]['question'][0][0]):
                # Если правильный, то удаляем первый вопрос и
                # прибавляем балл за ответ
                word = random.choice(['Правильно! ', 'Молодец! ', 'Угадал! '])
                res['response']['text'] = word + 'Следующий вопрос, ' + \
                                          sessionStorage[user_id]['first_name'].title() + '.'

                res['response']["tts"] = word + 'Следующий вопрос, ' + \
                                         sessionStorage[user_id]['first_name'].title() + '.'
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['image_id'] = sessionStorage[user_id] \
                    ['question'][0][3]
                res['response']['card']['title'] = word + \
                                                   sessionStorage[user_id]['first_name'].title() + '.'

                res['response']['buttons'] = [
                    {
                        'title': 'Продолжить',
                        'hide': True
                    },
                    {
                        'title': 'Конец игры',
                        'hide': True
                    }
                ]
                sessionStorage[user_id]['start'] = True
                del sessionStorage[user_id]['question'][0]
                sessionStorage[user_id]['answers'] += 1
                sessionStorage[user_id]['right_answers'] += 1

            else:
                # Если неправильный, то удаляем первый вопрос и
                # прибавляем балл за ответ
                word = \
                    random.choice(['Неправильно. ', 'Неверно. ', 'Ну ты и лох. '])
                res['response']['text'] = word + 'Следующий вопрос, ' + \
                                          sessionStorage[user_id]['first_name'].title() + '.'

                res['response']["tts"] = word + 'Следующий вопрос, ' + \
                                         sessionStorage[user_id]['first_name'].title() + '.'
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['image_id'] = sessionStorage[user_id] \
                    ['question'][0][3]
                res['response']['card']['title'] = word + 'Это ' + \
                                                   sessionStorage[user_id]['question'][0][0] + ', ' + \
                                                   sessionStorage[user_id]['first_name'].title() + '.'

                res['response']['buttons'] = [
                    {
                        'title': 'Продолжить',
                        'hide': True
                    },
                    {
                        'title': 'Конец игры',
                        'hide': True
                    }
                ]
                sessionStorage[user_id]['start'] = True
                del sessionStorage[user_id]['question'][0]
                sessionStorage[user_id]['answers'] += 1
                sessionStorage[user_id]['wrong_answers'] += 1

            return
    # если вопросы закончились, выходим из теста, показывая результат
    else:
        if sessionStorage[user_id]['bool']:
            sessionStorage[user_id]['bool'] = False

            res['response']['text'] = 'Спасибо за внимание'
            res['response']["tts"] = 'Спасибо за внимание'
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['image_id'] = '1540737/4c57cb876e3f41f7cef2'

            res['response']['title'] = 'Количество вопросов : ' + \
                                       str(sessionStorage[user_id]['answers']) + \
                                       '\nКоличество правильных ответов : ' + \
                                       str(sessionStorage[user_id]['right_answers']) + \
                                       '\nКоличество не правильных ответов : ' + \
                                       str(sessionStorage[user_id]['wrong_answers']) + \
                                       '\nХочешь пройти другой уровень'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]

            # return

        else:
            res['response']['text'] = 'Количество вопросов : ' + \
                                      str(sessionStorage[user_id]['answers']) + \
                                      '\nКоличество правильных ответов : ' + \
                                      str(sessionStorage[user_id]['right_answers']) + \
                                      '\nКоличество не правильных ответов : ' + \
                                      str(sessionStorage[user_id]['wrong_answers'])
            res['response']["tts"] = 'Количество вопросов : ' + \
                                     str(sessionStorage[user_id]['answers']) + \
                                     '\nКоличество правильных ответов : ' + \
                                     str(sessionStorage[user_id]['right_answers']) + \
                                     '\nКоличество не правильных ответов : ' + \
                                     str(sessionStorage[user_id]['wrong_answers'])
            res['response']['end_session'] = True


def get_first_name8(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def get_search_word(req, word):
    # ищем в ответе да или нет
    for token in req['request']['nlu']['tokens']:
        if token == word.split()[0].lower():
            return True
    return False


def open_file(file_name, difficulty):
    with open(file_name) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        events = [(x['name_object'], x['object'], x['question'], x['answer'])
                  for x in reader if x['difficult'] == difficulty]
    return events


def get_answer(req):
    # ищем в ответе да или нет
    for token in req['request']['nlu']['tokens']:
        if token.lower() in ['да', 'ага', 'давай']:
            return 'да'
        elif token.lower() in ['нет', 'не']:
            return 'нет'
