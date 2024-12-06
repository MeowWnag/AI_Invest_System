
import requests
import json

url = 'http://localhost:8080/pos'

text = "清末，共有二十二省以及內蒙古、西套蒙古、外蒙古、科布多、阿爾泰、青海、西藏等區域。"
headers = {'Content-Type': 'application/json'}
def hanlp_pos_zh(text):
    myobj = {'text': text}
    x = requests.post(url, data=json.dumps(myobj), headers=headers)
    #print(x.text)
    result = eval(x.text)['result']
    result = result.split(' ')
    return result

def get_keywords(text):
    result = hanlp_pos_zh(text)
    keywords = []
    for i in result:
        if i == '':
            continue
        word = i.split('_')[0]
        part_of_speech = i.split('_')[1]
        if(part_of_speech == 't' or part_of_speech == 'ns' or part_of_speech == 'nr' 
           or part_of_speech == 'nz' or part_of_speech == 'nt' or part_of_speech == 'n'):
            keywords.append(word)

    return keywords

