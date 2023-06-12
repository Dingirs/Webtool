import os

import configparser
import requests

from Flask import app
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

config = configparser.ConfigParser()
config.read('config.cfg')
azure_setting = config['azure']
APP_ID = azure_setting['clientId']
SCOPE = [azure_setting['graphUserScopes']]

access_token = generate_access_token(APP_ID, SCOPE)
headers = {
    'Authorization': 'Bearer ' + access_token['access_token'],
    'content-type': 'multipart/form-data'
}

file_path = app.static_folder + '/presentations/Holiday Vending Items 2021_presentation.pptx'
file_name = os.path.basename(file_path)
with open(file_path, 'rb') as upload:
    media_content = upload.read()

response = requests.put(
    GRAPH_API_ENDPOINT + f'/me/drive/items/root:/{file_name}:/content',
    headers=headers,
    data=media_content
)
