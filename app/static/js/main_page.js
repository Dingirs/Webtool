var host = 'http://127.0.0.1:6060';

async function extractText() {
    let formData = new FormData();
    let pdfFile = document.getElementById('pdfFile').files[0];
    formData.append('pdf', pdfFile);
    let url = host + '/extract_text';
    let response = await fetch(url , {
        method: 'POST',
        body: formData
    });

    let data = await response.json();
    document.getElementById('result_text').innerText = data.text;
}

async function extractImages() {
    let minWidth = document.getElementById("minWidth").value;
    let minHeight = document.getElementById("minHeight").value;
    let formData = new FormData();
    let pdfFile = document.getElementById('pdfFile').files[0];
    formData.append('pdf', pdfFile);
    formData.append('minWidth', minWidth);
    formData.append('minHeight', minHeight);
    let url = host + '/extract_images';
    let response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    let data = await response.json();

    let resultDiv = document.getElementById('result_image');
    resultDiv.innerHTML = '';
    for (let filename of data.image_filenames) {
        let a = document.createElement('a');
        a.href = `${host}/images/${filename}`;
        a.download = filename;
        a.textContent = `Download ${filename}`;
        resultDiv.appendChild(a);
        resultDiv.appendChild(document.createElement('br'));
        let b = document.createElement('img');
        b.src = `${host}/images/${filename}`;
        b.alt = filename;
        resultDiv.appendChild(b);
        resultDiv.appendChild(document.createElement('br'));
    }
}

async function createPresentation(){
    let formData = new FormData();
    let pdfFile = document.getElementById('pdfFile').files[0];
    let page = document.getElementById('page').value;
    let prompt = document.getElementById('prompt').value;
    formData.append('pdf', pdfFile);
    formData.append('page', page);
    formData.append('prompt', prompt);
    let url = host + '/create_presentation';
    let response = await fetch(url, {
        method: 'POST',
        body: formData
    });

    let data = await response.json();
    let resultDiv = document.getElementById('result_presentation')
    let filename = data.presentation_file_name;
    let  a = document.createElement('a');
    a.href = `${host}/presentations/${filename}`;
    a.download = filename;
    a.textContent = `Download ${filename}`;
    resultDiv.appendChild(a);
}

async function upload(){
    let formData = new FormData();
    let pptxFile = document.getElementById('pptxFile').files[0];
    formData.append('pptx', pptxFile);
    let url = host + '/upload';
    let response = await fetch(url, {
        method: 'POST',
        body: formData
    });
    let data = await response.json();
    if (data.text == 'login'){
        window.location.href = host + "/login";
    }
    else{
        document.getElementById('result_upload').innerText = 'Upload success';
    }



}