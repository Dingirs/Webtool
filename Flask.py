import io
import shutil
import subprocess
import threading

import webbrowser

from flask import Flask, request, jsonify, render_template, send_from_directory, session
from PyPDF2 import PdfReader
import fitz
import os
from PIL import Image
import ast
import identity.web
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
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    pdf = request.files['pdf']
    file_name = pdf.filename.replace(".pdf", "_presentation")
    reader = PdfReader(pdf)
    page = -1
    prompt = ""
    if 'page' in request.form and request.form['page'] != "":
        page = int(request.form['page'])
    if 'prompt' in request.form:
        prompt = request.form['prompt']
    threads = []
    slides = {}
    presentation = []
    errors = {}
    text = ""
    for p in range(len(reader.pages)):
        if page == -1 or page == p:
            text = reader.pages[p].extract_text()
            th = ThreadWithReturnValue(target=ChatGPT().create_presentation,
                                       args=(text, f"page{p}", f"upload/presentations", p, prompt))
            threads.append(th)
            th.start()
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
    presentation_code = ChatGPT.create_presentation_code(file_name, presentation)
    with open(f"upload/presentations/{file_name}.py", "w",
              encoding='utf-8') as f:
        f.write(presentation_code)
    if os.path.exists(f"upload/presentations/{file_name}.py"):
        subprocess.run(['python', f'upload/presentations/{file_name}.py'], shell=True)
    return jsonify({'presentation_file_name': f'{file_name}.pptx'})


@app.route('/upload', methods=['POST'])
def upload():
    if 'pptx' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    pptx = request.files['pptx']
    file_name = pptx.filename.replace(".pptx", "")
    webbrowser.open(auth.log_in(scopes=config.SCOPE,
                redirect_uri='https://onedrive.live.com/')['auth_uri'])
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
    # delete_files_in_folder(folder)
    app.run(debug=True)

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
