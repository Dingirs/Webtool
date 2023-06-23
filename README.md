# Webtool
pip install -r requirements.txt

Change the name of config_template.py to config.py, and add CLIENT_ID, CLIENT_SECRET, CHATGPT_API_KEY, SECRET_KEY.


docker build -t web_tool .
docker run -dp 127.0.0.1:6060:6060 web_tool