from mitmproxy import http
import json
from datetime import datetime

def save(flow):
    body = json.loads(flow.request.text)

    with open('data/user/userPieceSetList.json', encoding='utf-8') as f:
        userPieceSetList = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)

    targetUserPieceSet = {}
    targetUserPieceSetIdx = 0
    for i, userPieceSet in enumerate(userPieceSetList):
        if userPieceSet['setNum'] == body['setNum']:
            targetUserPieceSet = userPieceSet
            targetUserPieceSetIdx = i

    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    if targetUserPieceSet == {}:
        targetUserPieceSet = {
            "createdAt": nowstr,
            'userId': user['id'],
            'setNum': body['setNum']
        }
        userPieceSetList.append(targetUserPieceSet)

    targetUserPieceSet['name'] = body['name']
    for i, id in enumerate(body['userPieceIdList']):
        targetUserPieceSet['userPieceId'+str(i+1)] = id
    userPieceSetList[targetUserPieceSetIdx] = targetUserPieceSet

    with open('data/user/userPieceSetList.json', 'w+', encoding='utf-8') as f:
        json.dump(userPieceSetList, f, ensure_ascii=False)

    response = {
        'resultCode': 'success',
        'userPieceSetList': [targetUserPieceSet]
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

def handleUserPieceSet(flow):
    endpoint = flow.request.path.replace('/magica/api/userPieceSet', '')
    if endpoint.endswith('/save'):
        save(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})