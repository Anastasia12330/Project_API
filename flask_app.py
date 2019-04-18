# импортируем библиотеки
from flask import Flask, request
import logging

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


def get_first_name8(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)
