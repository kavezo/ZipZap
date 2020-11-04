import flask
import json
from datetime import datetime

def save():
    body = flask.request.json

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
    return flask.jsonify(response)

def handleUserPieceSet(endpoint):
    if endpoint.startswith('save'):
        return save()
    else:
        print('userPieceSet/'+endpoint)
        flask.abort(501, description="Not implemented")