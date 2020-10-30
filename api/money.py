from mitmproxy import http
import json

# wow bold of you to let me handle money
def handleMoney(flow):
    endpoint = flow.request.path.replace('/magica/api/money', '')
    if endpoint.startswith('/shop/list'):
        with open('data/commonMoneyList.json', encoding='utf-8') as f:
            userCommonMoneyList = json.load(f)
        flow.response = http.HTTPResponse.make(200, json.dumps({'userCommonMoneyList': userCommonMoneyList, 'resultCode': 'success'}), {})
    else:
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})