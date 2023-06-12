import PySimpleGUI as sg
from Extractor import Extractor

layout = [[sg.Text("PDF Extractor")],
          [sg.Text("Choose a pdf file: "), sg.Input(), sg.FileBrowse(key='PDF File')],
          [sg.Text("Choose a folder: "), sg.Input(), sg.FolderBrowse(key='Output Folder')],
          [sg.Button("Extract Images"), sg.Button("Extract Text"), sg.Button("Presentation Text"), sg.Button("Exit")],
          [sg.Text(s=(30,1), k='-STATUS-')]]

window = sg.Window("PDF_Extractor", layout)

while True:
    event, values = window.read()

    if event == "Extract Images":
        extractor = Extractor([values['PDF File']], values['Output Folder'])
        extractor.extract_images()
        sg.popup("Images Extracted")
    if event == "Extract Text":
        extractor = Extractor([values['PDF File']], values['Output Folder'])
        extractor.extract_text()
        sg.popup("Text Extracted")
    if event == "Presentation Text":
        window['-STATUS-'].update('Processing...')
        extractor = Extractor([values['PDF File']], values['Output Folder'])
        window.perform_long_operation(lambda: extractor.make_presentation(extractor.extract_text(1)), "-END KEY-")
    if event == "-END KEY-":
        window['-STATUS-'].update('')
        sg.popup("Presentation Text Generated")
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
