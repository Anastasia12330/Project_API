import requests


def image_id_map(this_file):
    # получаем image_id картинки для Диалога
    search_trans = "https://dialogs.yandex.net/api/v1/skills/db785827-dacc-4d88-841e-3f61bca30577/images"

    search_headers = {
        "Authorization": "OAuth AQAAAAAgQc1jAAT7o2Vw_5izXEPNsKYrX_kqAEw",
        # "Content-Type": "multipart/form-data"
    }

    # this_file = 'Mountain.jpg'
    files = {'file': (this_file, open(this_file, 'rb'))}

    response = requests.post(search_trans, headers=search_headers, files=files)

    json_response = response.json()

    return json_response['image']['id']


if __name__ == "__main__":
    print(image_id_map("map.png"))
