import json
from mitmproxy import http

def setLive2d(flow):
    body = json.loads(flow.request.text)
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)

    response = {
        "resultCode": "success"
    }
    for i in range(len(userCharaList)):
        if userCharaList[i]['charaId'] == body['charaId']:
            userCharaList[i]['live2dId'] = body['live2dId']
            response['userCharaList'] = [userCharaList[i]]

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCharaList, f, ensure_ascii=False)

    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

def handleUserLive2d(flow):
    endpoint = flow.request.path.replace('/magica/api/userLive2d', '')
    if endpoint.endswith('/set'):
        setLive2d(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})