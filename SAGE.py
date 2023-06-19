import json
import tiktoken
import requests
import config

class SAGE:

    def __init__(self):
        self.url = "https://www.promoplace.com/ws/ws.dll/ConnectAPI"
        self.tokenizer = tiktoken.get_encoding('cl100k_base')
        self.key = config.SAGE_KEY

    def search(self, keyword, color = ""):
        #"suppID":52344,"supplier":"PCNA"
        request = {
            "serviceId": 103,
            "apiVer": 130,
            "auth": {
                "acctId": 23811,
                "key": self.key
            },
            "search": {
                "keywords": keyword,
                "color": color,
                "thumbPicRes": "1800",
                "suppId": 52344,
                "extraReturnFields": "DESCRIPTION,SUPPID,SUPPLIER"
            }
        }
        res = requests.request("post", self.url, json=request)
        search_results = []
        for x in res.json()["products"]:
            product = []
            product.append('product name: ' + x["name"])
            product.append('product description: ' + x["description"])
            product.append('product picture link: ' + x["thumbPic"])
            search_results.append(", ".join(product))
        print(". ".join(search_results))
        '''
        #write res to the end of result.txt
        with open("result.txt", "a", encoding='utf-8') as f:
            lines=[]
            for x in res.json()["products"]:
                lines.append('product name: ' + x["name"] + ': ')
                print(x["name"])
                lines.append(x["description"]+'\n')
                print(x["description"])
                #lines.append(x["thumbPic"]+'\n')
                #print(x["thumbPic"])
                #print(x["suppID"])
                #print(x["supplier"])
            f.writelines(lines)
'''

    # create the length function
    def tiktoken_len(self, text,):

        tokens = self.tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

#test
#SAGE_test = SAGE()
#SAGE_test.search(keyword="football")
