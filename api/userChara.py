import json
from mitmproxy import http

def sale(flow):
    body = json.loads(flow.request.text)
    charaId = body['charaId']
    amount = body['num']

    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)

    rarity = 0
    saleItemId = None
    responseCharaList = []
    for i in range(len(userCharaList)):
        if userCharaList[i]['charaId'] == charaId:
            userCharaList[i]['lbItemNum'] -= amount
            rarity = userCharaList[i]['chara']['defaultCard']['rank'][-1]
            saleItemId = userCharaList[i]['chara']['maxSaleItemId'] if 'maxSaleItemId' in userCharaList[i]['chara'] \
                else userCharaList[i]['chara']['saleItemId']
            responseCharaList.append(userCharaList[i])
            break
        if userCharaList[i]['lbItemNum'] < 0:
            flow.response = http.HTTPResponse.make(400, '{"errorTxt": "You don\'t have that many gems to sell >:(","resultCode": "error","title": "Error"}', {})
            return

    gemsReceived = [1, 1, 3, 1]
    responseItemList = []
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        itemList = json.load(f)
    for i in range(len(itemList)):
        if itemList[i]['itemId'] == saleItemId:
            itemList[i]['quantity'] += amount * gemsReceived[rarity]
            responseItemList.append(itemList[i])

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCharaList, f, ensure_ascii=False)
    with open('data/user/userItemList.json', 'w+', encoding='utf-8') as f:
        json.dump(itemList, f, ensure_ascii=False)
    
    response = {
        "resultCode": "success",
        'userCharaList': responseCharaList,
        'userItemList': responseItemList
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})

def visualize(flow):
    body = json.loads(flow.request.text)
    response = {
        "resultCode": "success"
    }

    with open('data/user/userCardList.json', encoding='utf-8') as f:
        userCardList = json.load(f)
    
    for i in range(len(userCardList)):
        if userCardList[i]['card']['charaNo'] == body['charaId']:
            userCardList[i]['displayCardId'] = body['displayCardId']
            response['userCardList'] = userCardList

    with open('data/user/userCardList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCardList, f, ensure_ascii=False)

    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)

    for i in range(len(userCharaList)):
        if userCharaList[i]['charaId'] == body['charaId']:
            userCharaList[i]['commandVisualId'] = body['commandVisualId']
            userCharaList[i]['commandVisualType'] = body['commandVisualType']
            response['userCharaList'] = [userCharaList[i]]

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCharaList, f, ensure_ascii=False)

    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

    
def handleUserChara(flow):
    endpoint = flow.request.path.replace('/magica/api/userChara', '')
    if endpoint.endswith('/sale'):
        sale(flow)
    elif endpoint.endswith('/visualize'):
        visualize(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})