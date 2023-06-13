import os
import configparser
import requests
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT


class MSG:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        azure_setting = config['azure']
        APP_ID = azure_setting['clientId']
        SCOPE = [azure_setting['graphUserScopes']]
        self.access_token = generate_access_token(APP_ID, SCOPE)

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

        return response.json()

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

        return response.json()


#msg = MSG()
#print(msg.upload_file_from_path("upload/presentations/Holiday Vending Items 2021_presentation.pptx"))
