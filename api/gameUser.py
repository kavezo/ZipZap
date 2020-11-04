import json
import flask

with open('data/user/gameUser.json', encoding='utf-8') as f:
    gameUser = json.load(f)
with open('data/user/user.json', encoding='utf-8') as f:
    user = json.load(f)

def saveGameUser():
    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        json.dump(gameUser, f, ensure_ascii=False)

def changeLeader():
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    body = flask.request.json
    gameUser['leaderId'] = body['userCardId']
    saveGameUser()

    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': user
    }
    return flask.jsonify(response)

def editComment():
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)

    body = flask.request.json
    gameUser['comment'] = body['comment']
    saveGameUser()

    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': user
    }
    return flask.jsonify(response)

def setBackground():
    global gameUser, user
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    body = flask.request.json
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
    return flask.jsonify(response)
    
def handleGameUser(endpoint):
    if endpoint.endswith('changeLeader'):
        return changeLeader()
    elif endpoint.endswith('editComment'):
        return editComment()
    elif endpoint.endswith('setBackground'):
        return setBackground()
    else:
        print('gameUser' + endpoint)
        flask.abort(501, description="Not implemented")