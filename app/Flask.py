import io
import shutil
import subprocess
import threading

import webbrowser

from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
from PyPDF2 import PdfReader
import fitz
import os
from PIL import Image
import ast
import identity.web

import ChatGPT_post
from flask_session import Session
from ChatGPT_post import ChatGPT
from MSG import MSG
import config


class ThreadWithReturnValue(threading.Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        threading.Thread.join(self)
        return self._return


app = Flask(__name__)
app.config.from_object(config)
Session(app)
auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    pdf = request.files['pdf']
    file_name = pdf.filename
    reader = PdfReader(pdf)
    text = ''

    for page in range(len(reader.pages)):
        temp = reader.pages[page].extract_text()
        with open(f"{app.static_folder}/texts/{file_name}_page{page + 1}_text.txt", "w") as file:
            file.write(temp)
        text += temp

    return jsonify({'text': text})


@app.route('/extract_images', methods=['POST'])
def extract_images():
    if 'minWidth' or 'minHeight' not in request.form:
        min_width = 100
        min_height = 100
    else:
        min_width = request.form['minWidth']
        min_height = request.form['minHeight']
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    os.remove("temp.pdf")
    pdf = request.files['pdf']
    pdf.save("temp.pdf")
    file_name = pdf.filename.replace(".pdf", "")
    doc = fitz.open("temp.pdf")
    image_list = []
    for i in range(len(doc)):
        y = 0
        for img in doc.get_page_images(i):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            image = Image.open(io.BytesIO(image_data))
            # Save the image data to a file
            if image.width >= min_width and image.height >= min_height:
                y += 1
                image_filename = f"{file_name}_page{i + 1}_picture{y}.png"
                image_filename_path = f"{app.static_folder}/images/" + image_filename
                with open(image_filename_path, "wb") as file:
                    file.write(image_data)
                image_list.append(image_filename)

    return jsonify({'image_filenames': image_list})


@app.route('/create_presentation', methods=['POST'])
def create_presentation():
    # extract texts from pdf
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    # get pdf file
    pdf = request.files['pdf']
    # get file name
    file_name = pdf.filename.replace(".pdf", "_presentation")
    # get pdf content
    reader = PdfReader(pdf)
    # page default value is -1, which means all pages
    page = -1
    # addition prompt for ChatGPT
    prompt = ""
    # get page and prompt from request
    if 'page' in request.form and request.form['page'] != "":
        page = int(request.form['page'])
    if 'prompt' in request.form:
        prompt = request.form['prompt']
    # create threads for each page
    threads = []
    slides = {}
    presentation = []
    errors = {}
    text = ""
    # create threads for each page, and each thread will invoke ChatGPT to create presentation texts for each page
    # Chatgpt 4.0 has a limit of 8k tokens, so we need to split the text into several parts
    for p in range(len(reader.pages)):
        if page == -1 or page == p:
            text = reader.pages[p].extract_text()
            th = ThreadWithReturnValue(target=ChatGPT().create_presentation,
                                       args=(text, f"page{p}", f"upload/presentations", p, prompt))
            threads.append(th)
            th.start()
    # get the result from each thread
    for th in threads:
        # key is the page number, value is the result from ChatGPT(json format)
        key, value = th.join()
        if value == "error":
            errors[key] = value
        else:
            # convert json to dictionary. There are several slides for each page
            value = ast.literal_eval(value)
            slides[key] = value
    for page in sorted(slides):
        for slide in slides[page]:
            # add each slide to the presentation in order
            presentation.append(slides[page][slide])
    # create presentation code
    presentation_code = ChatGPT_post.create_presentation_code(file_name, presentation)
    # save presentation code to a file
    with open(f"upload/presentations/{file_name}.py", "w",
              encoding='utf-8') as f:
        f.write(presentation_code)
    # run the presentation code to create a pptx file
    if os.path.exists(f"upload/presentations/{file_name}.py"):
        subprocess.run(['python', f'upload/presentations/{file_name}.py'], shell=True)
    return jsonify({'presentation_file_name': f'{file_name}.pptx'})


@app.route('/login')
def login():
    return render_template("login.html", **auth.log_in(
        scopes=config.SCOPE,  # Have user consent to scopes during log-in
        redirect_uri='http://localhost:6060/authorized',
        # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
    ))


@app.route('/authorized')
def authorized():
    result = auth.complete_log_in(request.args)
    if 'error' in result:
        return render_template('auth_error.html', result=result)
    return redirect(url_for('root'))


@app.route('/upload', methods=['POST'])
def upload():
    if not auth.get_user():
        return jsonify({'text': 'login'})
    if 'pptx' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    pptx = request.files['pptx']
    file_name = pptx.filename
    token = auth.get_token_for_user(config.SCOPE)
    if "error" in token:
        return jsonify({'text': 'No token'}), 400
    msg = MSG(token)
    text = msg.upload_file(pptx, file_name)
    webbrowser.open('https://onedrive.live.com/')
    # msg = MSG()
    # text = msg.upload_file(pptx, file_name)
    return jsonify({'text': text})


@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(app.static_folder + "/images/", filename)


@app.route('/presentations/<filename>', methods=['GET'])
def get_presentation(filename):
    return send_from_directory("upload/presentations/", filename)


@app.route('/')
def root():
    return render_template('App.html')


def delete_files_in_folder(folder_path):
    for folder_root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(folder_root, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    # folder = app.static_folder
    # delete_files_in_folder(folder+"/images")
    # delete_files_in_folder(folder+"/texts")
    app.run(host='localhost', port=6060, debug=True)

'''
with open("temp.pdf", 'rb') as f:
    reader = PdfReader(f)
    page = -1
    prompt = ""
    threads = []
    slides = {}
    errors = {}
    presentation = []
    text = ""
    for p in range(len(reader.pages)):
        if page == -1 or page == p:
            text = reader.pages[p].extract_text()
            th = ThreadWithReturnValue(target=ChatGPT().create_presentation,
                                       args=(text, f"page{p}", f"{app.static_folder}/presentations", p, prompt,))
            threads.append(th)
            th.start()
    value = {}
    for th in threads:
        key, value = th.join()
        if value == "error":
            errors[key] = value
        else:
            value = ast.literal_eval(value)
            slides[key] = value
    for page in sorted(slides):
        for slide in slides[page]:
            presentation.append(slides[page][slide])
    print(presentation)
    presentation_code = create_presentation_code("presentation", presentation)
    with open(f"{app.static_folder}/presentations/test_presentation.py", "w",
              encoding='utf-8') as f:
        f.write(presentation_code)
    if os.path.exists(f"{app.static_folder}/presentations/test_presentation.pptx"):
        subprocess.run(['python', f'static/presentations/{file_name}.py'], shell = True)
'''
