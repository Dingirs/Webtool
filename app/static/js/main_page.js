async function extractText() {
    let formData = new FormData();
    let pdfFile = document.getElementById('pdfFile').files[0];
    formData.append('pdf', pdfFile);

    let response = await fetch('http://localhost:6060/extract_text', {
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

    let response = await fetch('http://localhost:6060/extract_images', {
        method: 'POST',
        body: formData
    });

    let data = await response.json();

    let resultDiv = document.getElementById('result_image');
    resultDiv.innerHTML = '';
    for (let filename of data.image_filenames) {
        let a = document.createElement('a');
        a.href = `http://localhost:6060/images/${filename}`;
        a.download = filename;
        a.textContent = `Download ${filename}`;
        resultDiv.appendChild(a);
        resultDiv.appendChild(document.createElement('br'));
        let b = document.createElement('img');
        b.src = `http://localhost:6060/images/${filename}`;
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

    let response = await fetch('http://localhost:6060/create_presentation', {
        method: 'POST',
        body: formData
    });

    let data = await response.json();
    let resultDiv = document.getElementById('result_presentation')
    let filename = data.presentation_file_name;
    let  a = document.createElement('a');
    a.href = `http://localhost:6060/presentations/${filename}`;
    a.download = filename;
    a.textContent = `Download ${filename}`;
    resultDiv.appendChild(a);
}

async function upload(){
    let formData = new FormData();
    let pptxFile = document.getElementById('pptxFile').files[0];
    formData.append('pptx', pptxFile);
    let response = await fetch('http://localhost:6060/upload', {
        method: 'POST',
        body: formData
    });
    let data = await response.json();
    if (data.text == 'login'){
        window.location.href = "http://localhost:6060/login";
    }
    else{
        document.getElementById('result_upload').innerText = 'Upload success';
    }



}