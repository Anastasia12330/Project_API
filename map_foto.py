import sys
import requests
import pygame, os
from scale import scale_object


def Map_image_id(toponym_to_find, bool=False):
    # запрос к геокодеру формируется следующим образом:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {"geocode": toponym_to_find, "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        # обработка ошибочной ситуации
        # Произошла ошибка выполнения запроса. Обрабатываем http-статус.
        print("Ошибка выполнения запроса:")
        print(geocoder_api_server)
        print("Http статус:", response.status_code, "(", response.reason, ")")

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    # Координаты углов объекта
    toponym_coodrinates_lowerCorner = toponym["boundedBy"]['Envelope']['lowerCorner']
    toponym_coodrinates_upperCorner = toponym["boundedBy"]['Envelope']['upperCorner']

    delta_l, delta_r = scale_object(toponym_coodrinates, toponym_coodrinates_lowerCorner)

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta_l, delta_r]),
        "l": "sat,skl",
        "size": "400,250"
    }

    if bool:
        if float(delta_l) < float(delta_l):
            delta_l1, delta_r1 = float(delta_r) / 3, float(delta_l) / 13
        else:
            delta_l1, delta_r1 = float(delta_l) / 3, float(delta_r) / 13
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([delta_l, delta_r]),
            "l": "sat,skl",
            "size": "600,450",
            "pl": "f:FFFFFFFF," + str(float(toponym_longitude) - delta_l1) + "," + str(
                float(toponym_lattitude) - delta_r1) + ","
                  + str(float(toponym_longitude) - delta_l1) + "," + str(
                float(toponym_lattitude) + delta_r1) + ","
                  + str(float(toponym_longitude) + delta_l1) + "," + str(
                float(toponym_lattitude) + delta_r1) + ","
                  + str(float(toponym_longitude) + delta_l1) + "," + str(
                float(toponym_lattitude) - delta_r1) + ","
                  + str(float(toponym_longitude) - delta_l1) + "," + str(
                float(toponym_lattitude) - delta_r1),
            "pt": ",".join([toponym_longitude, toponym_lattitude]) + ",pm2dgl"
        }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Удаляем за собой файл с изображением.
    # os.remove(map_file)


if __name__ == "__main__":
    Map_image_id('стокгольм')
