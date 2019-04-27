import requests


def delete_image_id_foto(image_id):
    # удаляем ненужную картинку из Диалогов, чтобы не перегружать память
    search_trans = "https://dialogs.yandex.net/api/v1/skills/db785827-dacc-4d88-841e-3f61bca30577/images/" + image_id

    search_headers = {
        "Authorization": "OAuth AQAAAAAgQc1jAAT7o2Vw_5izXEPNsKYrX_kqAEw",
    }

    response = requests.delete(search_trans, headers=search_headers)

    json_response = response.json()
    print(json_response)

    return json_response


if __name__ == "__main__":
    delete_image_id_foto('213044/a675dc431e12f99165a2')
