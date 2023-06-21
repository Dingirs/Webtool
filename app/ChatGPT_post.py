import requests
import config
import SAGE
import json


class ChatGPT:
    def __init__(self, request={}):
        self.request = request
        # BEARER_TOKEN = os.environ.get("BEARER_TOKEN") or "BEARER_TOKEN_HERE"
        self.url = "https://api.openai.com/v1/chat/completions"
        api_key = config.CHATGPT_API_KEY
        self.headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        }

    def normal_chat(self, user_input):
        self.request["messages"].append({"role": "user", "content": user_input})
        res = requests.request("post", self.url, json=self.request, headers=self.headers)
        for x in res.json()["choices"]:
            print(x["message"]["content"])
        self.request["messages"].append({"role": "assistant", "content": x["message"]["content"]})

    def get_presentation(self, text, file_name, output_dir, file_page_index):
        print(f"{file_name}_page_{file_page_index + 1}")
        self.request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system",
                 "content": "You are a business assistance for SpecWroks company. You are helping to create"
                            " a presentation based on given text."
                 }
            ],
            "temperature": 0.0
        }
        self.request["messages"].append({"role": "user", "content": text})
        res = requests.request("post", self.url, json=self.request, headers=self.headers)
        try:
            presentation = []
            for x in res.json()["choices"]:
                presentation.append(x["message"]["content"])
            symbol = "\n"
            with open(output_dir + f"/{file_name}_page{file_page_index + 1}_presentation.txt", "w",
                      encoding='utf-8') as f:
                f.write(symbol.join(presentation))
            # request_presentation["messages"].append({"role": "assistant", "content": x["message"]["content"]})
        except:
            with open(output_dir + f"/{file_name}_page{file_page_index + 1}_presentation.txt", "w",
                      encoding='utf-8') as f:
                f.write(res.text)

    def create_presentation(self, text, file_name, output_dir, file_page_index, prompt=''):
        self.request = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a export assistance for creating presentations.\n"
                                              "You should only respond in JSON format as described below\n"
                                              "Response Format:\n"
                                              "{\n"
                                              "    \"Slide_index\": {\n"
                                              "         \"Title\": title text,\n"
                                              "         \"Content\": content text\n"
                                              "    }\n"
                                              "}\n"

                 }
            ],
            "temperature": 0.0
        }
        self.request["messages"].append({"role": "user",
                                         "content": text + "Create a presentation template about introducting "
                                                           "products in text, and use the above text to create a new "
                                                           "introduction text to fill in the presentation. The "
                                                           "presentation "
                                                           "should be easy to read and well structured. If tabular "
                                                           "data exists, use a table format to represent it. Each "
                                                           "product should only have one slide, and the table also "
                                                           "should be in the same slide." + prompt})
        res = requests.request("post", self.url, json=self.request, headers=self.headers)
        try:
            presentation_text = res.json()["choices"][0]["message"]["content"]
            return file_page_index, presentation_text
            # with open(output_dir + f"/{file_name}_presentation.py", "w",
            #          encoding='utf-8') as f:
            #    f.write(create_presentation_code(file_name, j))
        except:
            with open(output_dir + f"/{file_name}_presentation.txt", "w",
                      encoding='utf-8') as f:
                f.write(res.text)
            return file_page_index, "error"

    def function_calling(self, user_input):
        self.request = {
            "model": "gpt-4-0613",
            "messages": [{
                "role": "system",
                "content": "You are a export assistance for searching products from SAGE through API.\n"}
            ],
            "functions": [
                {
                    "name": "SAGE_search",
                    "description": "Search for SAGE products through SAGE API",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "The keyword to search for"
                            },
                            "color": {
                                "type": "string",
                                "description": "The color of the product"
                            },
                        },
                        "required": ["keyword"],
                    },
                }
            ],
            "function_call": "auto"
        }
        self.request["messages"].append({"role": "user", "content": user_input})
        response = requests.request("post", self.url, json=self.request, headers=self.headers)
        try:
            response_message = response.json()["choices"][0]["message"]
            if response_message.get("function_call"):
                available_functions = {
                    "SAGE_search": SAGE.SAGE_search
                }
                function_name = response_message["function_call"]["name"]
                fuction_to_call = available_functions[function_name]
                function_args = json.loads(response_message["function_call"]["arguments"])
                if not function_args.get("color"):
                    function_args["color"] = ""
                function_response = fuction_to_call(
                    keyword=function_args.get("keyword"),
                    color=function_args.get("color"),
                )
                self.request["messages"].append(response_message)
                self.request["messages"].append(
                    {"role": "function", "name": function_name, "content": function_response})
                second_response = requests.request("post", self.url, json=self.request, headers=self.headers)
                try:
                    return second_response.json()["choices"][0]["message"]["content"]
                except:
                    return second_response.json()
        except:
            return response.json()


# test
#user_input = "I want to give a present to my mom, can you give me some suggestions?"
#print(ChatGPT().function_calling(user_input))


# create a code template for creating a presentation
def create_presentation_code(file_name, slides):
    presentation = "from pptx import Presentation\nfrom pptx.util import Inches, Pt\nprs = Presentation()\n"
    for slide in slides:
        title = slide["Title"]
        title = title.replace("\"", "\\" + "\"")
        title = title.replace("\n", r"\n" + "\"" + " \\" + "\n" + "\"")
        title = title.replace("\'", "\\" + "\'")
        content = slide["Content"]
        content = content.replace("\"", "\\" + "\"")
        content = content.replace("\n", r"\n" + "\"" + " \\" + "\n" + "\"")
        content = content.replace("\'", "\\" + "\'")
        presentation += add_slide(title, content)
    presentation += f"\nprs.save('upload/presentations/{file_name}.pptx')"
    return presentation


def add_slide(title, content):
    slide = f"slide_layout = prs.slide_layouts[1]\nslide = prs.slides.add_slide(slide_layout)\ntitle = " \
            f"slide.shapes.title\ntitle.text = \"{title}\"\ncontent = slide.placeholders[1]\ncontent.text = \"{content}\"\n"
    return slide
