import flask

from util import dataUtil as dt
from util import homuUtil as homu

def use():
    body = flask.request.json
    itemId = body['itemId']

    # spend items
    userItem = dt.getUserObject('userItemList', itemId)
    userItem['quantity'] -= body['num']
    if userItem['quantity'] < 0:
        flask.abort(400, '{"errorTxt": "You don\'t have enough.","resultCode": "error","title": "Error"}')
    
    # add AP/BP
    capPoint = float('inf')
    if itemId == 'CURE_BP':
        apType = 'BTP'
        recoverPoint = dt.getUserObject('userStatusList', 'MAX_BTP')['point']
        capPoint = dt.getUserObject('userStatusList', 'MAX_BTP')['point']
    elif itemId == 'CURE_AP_50':
        apType = 'ACP'
        recoverPoint = 50
    else:
        apType = 'ACP'
        recoverPoint = dt.getUserObject('userStatusList', 'MAX_ACP')['point']

    apStatus = homu.getStatus(apType)
    apStatus['point'] = min(capPoint, apStatus['point']+recoverPoint)

    dt.setUserObject('userItemList', itemId, userItem)
    dt.setUserObject('userStatusList', apType, apStatus)

    response = {
        "resultCode": "success",
        'userItemList': [userItem],
        'userStatusList': [apStatus]
    }
    return flask.jsonify(response)

def handleUserItem(endpoint):
    print(endpoint)
    if endpoint.startswith('use'):
        return use()
    else:
        print(flask.request.path)
        flask.abort(501, description='Not implemented')
