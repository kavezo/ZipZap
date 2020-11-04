import json
import flask

# wow bold of you to let me handle money
def handleMoney(endpoint):
    if endpoint.startswith('shop/list'):
        with open('data/commonMoneyList.json', encoding='utf-8') as f:
            userCommonMoneyList = json.load(f)
        return flask.jsonify({'userCommonMoneyList': userCommonMoneyList, 'resultCode': 'success'})
    else:
        flask.abort(501, description='Not implemented')