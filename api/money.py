import json
import flask

from util import dataUtil as dt

def process():
    # get gems
    gems = dt.getUserObject('userItemList', 'PRESENTED_MONEY')
    gems['item']['itemType'] = 'MONEY'
    response = {
        "resultCode": "success",
        "userItemList": [gems]
    }

    money = dt.getUserObject('userItemList', 'MONEY')
    if money is not None:
        money['item']['itemType'] = 'MONEY'
        response['userItemList'].append(money)
    return flask.jsonify(response)

# wow bold of you to let me handle money
def handleMoney(endpoint):
    if endpoint.startswith('shop/list'):
        return flask.jsonify({'userCommonMoneyList': dt.readJson('data/commonMoneyList.json'), 'resultCode': 'success'})
    elif endpoint.startswith('process'):
        return process()
    else:
        flask.abort(501, description='Not implemented')