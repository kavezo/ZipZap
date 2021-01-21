import json
import flask
import logging

from util import dataUtil as dt
from util import newUserObjectUtil as newtil

logger = logging.getLogger('app.userChara')

def sale():
    body = flask.request.json
    charaId = body['charaId']
    amount = body['num']

    rarity = 0
    responseCharaList = []
    userChara = dt.getUserObject('userCharaList', charaId)
    chara = userChara['chara']
    userChara['lbItemNum'] -= amount
    rarity = int(chara['defaultCard']['rank'][-1])
    responseCharaList.append(userChara)
    if userChara['lbItemNum'] < 0:
        flask.abort(400, description='{"errorTxt": "You don\'t have that many gems to sell >:(","resultCode": "error","title": "Error"}')
        return
    
    dt.setUserObject('userCharaList', charaId, userChara)
    responseItemList = []
    
    if chara['saleItemId'] == 'PRISM':
        gemsReceived = [1, 1, 3, 10]    
        userItem = dt.getUserObject('userItemList', 'PRISM')
        userItem['quantity'] += amount * gemsReceived[rarity-1]
        responseItemList.append(userItem)
        
        dt.setUserObject('userItemList', 'PRISM', userItem)

    if 'maxSaleItemId' in chara and chara['maxSaleItemId'] == 'DESTINY_CRYSTAL':
        logger.info('selling for crystal')
        userCrystal = dt.getUserObject('userItemList', 'DESTINY_CRYSTAL')
        if userCrystal is None:  
            userCrystal = newtil.createUserItem(dt.masterItems['DESTINY_CRYSTAL'])        
        userCrystal['quantity'] += amount 
        responseItemList.append(userCrystal)

        dt.setUserObject('userItemList', 'DESTINY_CRYSTAL', userCrystal)
    
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

    userChara = dt.getUserObject('userCharaList', body['charaId'])
    userChara['commandVisualId'] = body['commandVisualId']
    userChara['commandVisualType'] = body['commandVisualType']
    response['userCharaList'] = [userChara]
    dt.setUserObject('userCharaList', body['charaId'], userChara)

    return flask.jsonify(response)
    
def handleUserChara(endpoint):
    if endpoint.startswith('sale'):
        return sale()
    elif endpoint.startswith('visualize'):
        return visualize()
    else:
        logger.error('Missing implementation: userChara/'+endpoint)
        flask.abort(501, description="Not implemented")