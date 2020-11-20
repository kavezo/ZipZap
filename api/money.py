import json
import flask

from util import dataUtil

# wow bold of you to let me handle money
def handleMoney(endpoint):
    if endpoint.startswith('shop/list'):
        return flask.jsonify({'userCommonMoneyList': dataUtil.readJson('data/commonMoneyList.json'), 'resultCode': 'success'})
    elif endpoint.startswith('process'):
        return '{}'
    else:
        flask.abort(501, description='Not implemented')