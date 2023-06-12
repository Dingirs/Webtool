import os
import fitz  # PyMuPDF
import io
from PIL import Image # pillow
import threading
from ChatGPT_post import ChatGPT


class Extractor:
    def __init__(self, file_paths, output_dir):
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.file_names = []
        for file in self.file_paths:
            file_name = os.path.splitext(os.path.basename(file))[0]
            self.file_names.append(file_name)

    def extract_images(self):
        # Output directory for the extracted images
        output_dir = self.output_dir
        # Desired output image format
        output_format = "png"
        # Minimum width and height for extracted images
        min_width = 100
        min_height = 100
        # Create the output directory if it does not exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # file path you want to extract images from
        for file in self.file_paths:
            file_name = os.path.splitext(os.path.basename(file))[0]
            # open the file
            pdf_file = fitz.open(file)
            # Iterate over PDF pages
            for page_index in range(len(pdf_file)):
                # Get the page itself
                page = pdf_file[page_index]
                # Get image list
                image_list = page.get_images(full=True)
                # Print the number of images found on this page
                if image_list:
                    print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
                else:
                    print(f"[!] No images found on page {page_index}")
                # Iterate over the images on the page
                for image_index, img in enumerate(image_list, start=1):
                    # Get the XREF of the image
                    xref = img[0]
                    # Extract the image bytes
                    base_image = pdf_file.extract_image(xref)
                    image_bytes = base_image["image"]
                    # Get the image extension
                    image_ext = base_image["ext"]
                    # Load it to PIL
                    image = Image.open(io.BytesIO(image_bytes))
                    # Check if the image meets the minimum dimensions and save it
                    if image.width >= min_width and image.height >= min_height:
                        image.save(
                            open(os.path.join(output_dir,
                                              f"{file_name}_image{page_index + 1}_{image_index}.{output_format}"),
                                 "wb"),
                            format=output_format.upper())
                    else:
                        print(f"[-] Skipping image {image_index} on page {page_index} due to its small size.")

    def extract_text(self, switch = 0):
        output_dir = self.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        files_text = []
        for file in self.file_paths:
            file_name = os.path.splitext(os.path.basename(file))[0]
            pdf_file = fitz.open(file)
            file_pages_text = []
            for page_index in range(len(pdf_file)):
                page = pdf_file[page_index]
                if(switch == 0 or switch == 2):
                    with open(output_dir + f"/{file_name}_page{page_index+1}_text.txt", "w", encoding='utf-8') as f:
                        f.write(page.get_text())
                file_pages_text.append(page.get_text())
        files_text.append(file_pages_text)
        if switch == 1 or switch == 2:
            return(files_text)

    def make_presentation(self, files_text):
        threads = []
        for file_index in range(len(files_text)):
            for file_page_index in range(len(files_text[file_index])):
                print(file_page_index + 1)
                th = threading.Thread(target=ChatGPT().getpresentation, args=(files_text[file_index][file_page_index], self.file_names[file_index], self.output_dir, file_page_index, ))
                threads.append(th)
                th.start()
        for th in threads:
            th.join()



'''
    Extractor = Extractor(["Test/Holiday Vending Items 2021.pdf"], "Test")
    #Extractor.extract_images()
    Extractor.make_presentation(Extractor.extract_text(1))
'''