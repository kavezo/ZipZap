from mitmproxy import http
import json
from datetime import datetime
from api import userPiece, gacha
from uuid import uuid1

# This will only get you the lowest rarity card, but that's what all shop megucas have been...
def getCard(charaNo):
    with open('data/cards.json', encoding='utf-8') as f:
        cards = json.load(f)

    for card in cards:
        if card['charaId'] == charaNo:
            userCard, userChara, userLive2d, _ = gacha.addMeguca(card)
    return {'userCardList': [userCard], 'userCharaList': [userChara], 'userLive2dList': [userLive2d]}

def getFormation(formationId):
    with open('data/formationSheetList.json', encoding='utf-8') as f:
        formationSheetList = json.load(f)
    with open('data/user/userFormationSheetList.json', encoding='utf-8') as f:
        userFormations = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')

    for formation in userFormations:
        if formation['formationSheetId'] == formationId: # if already exists, do nothing
            return {}
    
    chosenFormation = {}
    for formation in formationSheetList:
        if formation['id'] == formationId:
            chosenFormation = formation
    
    userFormation = {
        "userId": userId,
        "formationSheetId": formationId,
        "createdAt": nowstr,
        "formationSheet": chosenFormation
    }
    with open('data/user/userFormationSheetList.json', 'w+', encoding='utf-8') as f:
        json.dump(userFormations+[userFormation], f, ensure_ascii=False)
    return {'userFormationSheetList': [userFormation]}

def getGift(giftId, amount):
    with open('data/user/userGiftList.json', encoding='utf-8') as f:
        gifts = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')

    foundGift = False
    responseGift = None
    for i in range(len(gifts)):
        if gifts[i]['giftId'] == giftId:
            gifts[i]['quantity'] += amount
            responseGift = gifts[i]
            foundGift = True
    if not foundGift:
        with open('data/giftList.json', encoding='utf-8') as f:
            allGifts = json.load(f)
        for exampleGift in allGifts:
            if exampleGift['id'] == giftId:
                responseGift = exampleGift
                responseGift['rankGift'] = 'RANK_'+str(responseGift['rank'])
        responseGift = {
            "userId": userId,
            "giftId": giftId,
            "quantity": amount,
            "createdAt": nowstr,
            "gift": responseGift
        }
        gifts.append(responseGift)

    with open('data/user/userGiftList.json', 'w+', encoding='utf-8') as f:
        json.dump(gifts, f, ensure_ascii=False)
    return {'userGiftList': [responseGift]}

def getItem(itemCode, amount, item=None):
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        items = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    
    foundItem = False
    responseItem = None
    for i in range(len(items)):
        if items[i]['itemId'] == itemCode:
            items[i]['quantity'] += amount
            responseItem = items[i]
            foundItem = True
    if not foundItem: # assumes only backgrounds and stuff
        items.append({
            "userId": userId,
            "itemId": itemCode,
            "environmentId": "COMMON",
            "quantity": 1,
            "total": 0,
            "item": item,
            "createdAt": nowstr
        })

    with open('data/user/userItemList.json', 'w+', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False)
    return {'userItemList': [responseItem]}

def getLive2d(charaId, live2dId, live2dItem):
    with open('data/user/userLive2dList.json', encoding='utf-8') as f:
        live2dList = json.load(f)
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    
    alreadyHas = False
    for live2d in live2dList:
        if live2d['charaId'] == charaId and live2d['live2dId'] == live2dId:
            alreadyHas = True

    args = {}
    if not alreadyHas:
        userLive2d = {
            "userId": userId,
            "charaId": charaId,
            "live2dId": live2dId,
            "live2d": live2dItem,
            "createdAt": nowstr
        }
        live2dList.append(userLive2d)
        with open('data/user/userLive2dList.json', 'w+', encoding='utf-8') as f:
            json.dump(live2dList, f, ensure_ascii=False)
        args['userLive2dList'] = [userLive2d]
    return args

def getPiece(piece, isMax, num):
    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        userPieceList = json.load(f)
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    
    newPieces = []
    for _ in range(num):
        userPieceList.append({
            "id": str(uuid1()),
            "userId": userId,
            "pieceId": piece['pieceId'],
            "piece": piece,
            "level": 1,
            "experience": 0,
            "lbCount": 0,
            "attack": piece['attack'],
            "defense": piece['defense'],
            "hp": piece['hp'],
            "protect": False,
            "archive": False,
            "createdAt": nowstr
        })
        if isMax:
            userPieceList[-1]['level'] = userPiece.getMaxLevel(piece['rank'], 4)
            userPieceList[-1]['lbcount'] = 4
            stats = userPiece.getStats(userPieceList[-1], userPieceList[-1]['level'])
            for key in stats.keys():
                userPieceList[-1][key] = stats[key]
        newPieces.append(userPieceList[-1])
    
    with open('data/user/userPieceList.json', 'w+', encoding='utf-8') as f:
        json.dump(userPieceList, f, ensure_ascii=False)
    return {'userPieceList': newPieces}

def getCC(amount):
    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        gameUser = json.load(f)
        gameUser['riche'] += amount
        json.dump(gameUser, f, ensure_ascii=False)
    return {'gameUser': gameUser}

def obtainSet(item, body, args):
    for code in item['rewardCode'].split(','):
        itemType = code.split('_')[0]
        if itemType == 'ITEM':
            args.update(getItem('_'.join(code.split('_')[1:-1]), int(code.split('_')[-1])*body['num']))
        elif itemType == 'RICHE':
            args.update(getCC(int(code.split('_')[-1])*body['num']))
        elif itemType == 'GIFT':
            args.update(getGift(int(code.split('_')[1]), int(code.split('_')[-1])*body['num']))

def obtain(item, body, args):
    if item['shopItemType'] == 'CARD':
        args.update(getCard(item['card']['charaNo']))
    elif item['shopItemType'] == 'FORMATION_SHEET':
        args.update(getFormation(item['formationSheet']['id']))
    elif item['shopItemType'] == 'GIFT':
        args.update(getGift(int(item['gift']['rewardCode'].split('_')[1]), body['num']*int(item['rewardCode'].split('_')[-1])))
    elif item['shopItemType'] == 'ITEM':
        args.update(getItem(item['item']['itemCode'], body['num']*int(item['rewardCode'].split('_')[-1], item['item'])))
    elif item['shopItemType'] == 'LIVE2D':
        args.update(getLive2d(item['chara']['id'], item['live2d']['live2dId'], item['live2d']))
    elif item['shopItemType'] in ['MAXPIECE', 'PIECE']:
        args.update(getPiece(item['piece'], item['shopItemType']=='MAXPIECE', body['num']))
    return args

# TODO: handle cases where it's a meguca sent to the present box
def buy(flow):
    body = json.loads(flow.request.text)
    with open('data/shopList.json', encoding='utf-8') as f:
        shopList = json.load(f)

    currShop = {}
    for shop in shopList:
        if shop['shopId'] == body['shopId']:
            currShop = shop
            break
    if currShop == {}:
        flow.response = http.HTTPResponse.make(400, '{"errorTxt": "Trying to buy from a nonexistent shop","resultCode": "error","title": "Error"}', {})
        return
    
    item = {}
    for shopItem in shop['shopItemList']:
        if shopItem['id'] == body['shopItemId']:
            item = shopItem
            break
    if item == {}:
        flow.response = http.HTTPResponse.make(400, '{"errorTxt": "Trying to buy something not in this shop","resultCode": "error","title": "Error"}', {})
        return

    # get the thing
    args = {}
    if item['shopItemType'] == 'SET':
        obtainSet(item, body, args)
    else:
        obtain(item, body, args)
    
    # spend items
    if item['consumeType'] == 'ITEM':
        spendArgs = getItem(item['needItemId'], -1*item['needNumber']*body['num'])
        if 'userItemList' in args:
            args['userItemList'] += spendArgs['userItemList']
        else:
            args.update(spendArgs)
    elif item['consumeType'] == 'MONEY':
        itemList = gacha.spend('MONEY', item['needNumber']*body['num'])
        if 'userItemList' in args:
            args['userItemList'] += itemList
        else:
            args['userItemList'] = itemList
    
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    userShopItem = {
            "createdAt": nowstr,
            "num": body['num'],
            "shopItemId": body['shopItemId'],
            "userId": userId
        }
    args['userShopItemList'] = [userShopItem]
    with open('data/user/userShopItemList.json', encoding='utf-8') as f:
        userShopItemList = json.load(f)
    with open('data/user/userShopItemList.json', 'w+', encoding='utf-8') as f:
        json.dump(userShopItemList+[userShopItem], f, ensure_ascii=False)

    flow.response = http.HTTPResponse.make(200, json.dumps(args, ensure_ascii=False), {})
    

def handleShop(flow):
    endpoint = flow.request.path.replace('/magica/api/shop', '')
    if endpoint.startswith('/buy'):
        buy(flow)
    else:
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})