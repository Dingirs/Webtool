import os
import requests

GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'


class MSG:
    def __init__(self, token):
        self.access_token = token

    def upload_file_from_path(self, file_path):
        headers = {
            'Authorization': 'Bearer ' + self.access_token['access_token'],
            'content-type': 'multipart/form-data'
        }

        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as upload:
            media_content = upload.read()

        response = requests.put(
            GRAPH_API_ENDPOINT + f'/me/drive/items/root:/{file_name}:/content',
            headers=headers,
            data=media_content
        )

        return response.text

    def upload_file(self, file, file_name):
        headers = {
            'Authorization': 'Bearer ' + self.access_token['access_token'],
            'content-type': 'multipart/form-data'
        }

        response = requests.put(
            GRAPH_API_ENDPOINT + f'/me/drive/items/root:/{file_name}:/content',
            headers=headers,
            data=file
        )

        return response.text

# msg = MSG()
# print(msg.upload_file_from_path("upload/presentations/Holiday Vending Items 2021_presentation.pptx"))
