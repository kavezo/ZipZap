import json
import flask

from util import dataUtil as dt

def sale():
    body = flask.request.json
    charaId = body['charaId']
    amount = body['num']

    rarity = 0
    responseCharaList = []
    userChara = newtil.getUserObject('userCharaList', charaId)
    userChara['lbItemNum'] -= amount
    rarity = int(userChara['chara']['defaultCard']['rank'][-1])
    responseCharaList.append(userChara)
    if userChara['lbItemNum'] < 0:
        flask.abort(400, description='{"errorTxt": "You don\'t have that many gems to sell >:(","resultCode": "error","title": "Error"}')
        return
    
    newtil.setUserObject('userCharaList', charaId, userChara)
    
    gemsReceived = [1, 1, 3, 10]
    responseItemList = []
    userItem = newtil.getUserObject('userItemList', 'PRISM')
    userItem['quantity'] += amount * gemsReceived[rarity-1]
    responseItemList.append(userItem)

    newtil.setUserObject('userItemList', 'PRISM', userItem)

    if rarity == 4:
        print('selling for crystal')
        userCrystal = newtil.getUserObject('userItemList', 'DESTINY_CRYSTAL')
        userCrystal['quantity'] += amount
        responseItemList.append(userCrystal)

        newtil.setUserObject('userItemList', 'DESTINY_CRYSTAL', userCrystal)
    
    response = {
        "resultCode": "success",
        'userCharaList': responseCharaList,
        'userItemList': responseItemList
    }
    return flask.jsonify(response)

def visualize():
    body = flask.request.json
    response = {
        "resultCode": "success"
    }

    with open('data/user/userCardList.json', encoding='utf-8') as f:
        userCardList = json.load(f)
    
    for i in range(len(userCardList)):
        if userCardList[i]['card']['charaNo'] == body['charaId']:
            userCardList[i]['displayCardId'] = body['displayCardId']
            response['userCardList'] = [userCardList[i]]

    with open('data/user/userCardList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCardList, f, ensure_ascii=False)

    userChara = newtil.getUserObject('userCharaList', body['charaId'])
    userChara['commandVisualId'] = body['commandVisualId']
    userChara['commandVisualType'] = body['commandVisualType']
    response['userCharaList'] = [userChara]
    newtil.setUserObject('userCharaList', body['charaId'], userChara)

    return flask.jsonify(response)
    
def handleUserChara(endpoint):
    if endpoint.startswith('sale'):
        return sale()
    elif endpoint.startswith('visualize'):
        return visualize()
    else:
        print('userChara/'+endpoint)
        flask.abort(501, description="Not implemented")