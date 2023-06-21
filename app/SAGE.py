import json
import requests
import config

url = "https://www.promoplace.com/ws/ws.dll/ConnectAPI"
key = config.SAGE_KEY


def SAGE_search(keyword, color=""):
    # "suppID":52344,"supplier":"PCNA"

    request = {
        "serviceId": 103,
        "apiVer": 130,
        "auth": {
            "acctId": 23811,
            "key": key
        },
        "search": {
            "keywords": keyword,
            "color": color,
            "thumbPicRes": "1800",
            "suppId": 52344,
            "extraReturnFields": "DESCRIPTION,SUPPID,SUPPLIER"
        }
    }
    res = requests.request("post", url, json=request)
    search_results = []
    i = 0
    for x in res.json()["products"]:
        product = {'product name': x["name"],
                   'product description': x["description"],
                   'product picture link': x["thumbPic"]}
        if i < 10:
            search_results.append(product)
            i += 1
        else:
            break
    return json.dumps(search_results)
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

# test
# print(SAGE_search(keyword="football"))
