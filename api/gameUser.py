import json
from mitmproxy import http

with open('data/user/gameUser.json', encoding='utf-8') as f:
    gameUser = json.load(f)
with open('data/user/user.json', encoding='utf-8') as f:
    user = json.load(f)

def saveGameUser():
    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        json.dump(gameUser, f, ensure_ascii=False)

def changeLeader(flow):
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    body = json.loads(flow.request.text)
    gameUser['leaderId'] = body['userCardId']
    saveGameUser()

    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': user
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})

def editComment(flow):
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)

    body = json.loads(flow.request.text)
    gameUser['comment'] = body['comment']
    saveGameUser()

    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': user
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})

def setBackground(flow):
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    body = json.loads(flow.request.text)
    gameUser['bgItemId'] = body['itemId']

    with open('data/user/userItemList.json', encoding='utf-8') as f:
        itemList = json.load(f)
    for item in itemList:
        if item['itemId'] == body['itemId']:
            gameUser['bgItem'] = item['item']

    saveGameUser()
    
    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})
    
def handleGameUser(flow):
    endpoint = flow.request.path.replace('/magica/api/gameUser', '')
    if endpoint.endswith('/changeLeader'):
        changeLeader(flow)
    elif endpoint.endswith('/editComment'):
        editComment(flow)
    elif endpoint.endswith('/setBackground'):
        setBackground(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})