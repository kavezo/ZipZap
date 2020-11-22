import json
import flask

from util import dataUtil

def process():
    # get gems
    response = {
        "resultCode": "success",
        "userItemList": [dataUtil.getUserObject('userItemList', 'PRESENTED_MONEY')]
    }

    money = dataUtil.getUserObject('userItemList', 'MONEY')
    if money is not None:
        response['userItemList'].append(money)
    return flask.jsonify(response)

# wow bold of you to let me handle money
def handleMoney(endpoint):
    if endpoint.startswith('shop/list'):
        return flask.jsonify({'userCommonMoneyList': dataUtil.readJson('data/commonMoneyList.json'), 'resultCode': 'success'})
    elif endpoint.startswith('process'):
        return process()
    else:
        flask.abort(501, description='Not implemented')