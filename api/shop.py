import flask
import json
from datetime import datetime
from api import userPiece, gacha
from uuid import uuid1

from util import dataUtil, newUserObjectUtil

# This will only get you the lowest rarity card, but that's what all shop megucas have been...
def getCard(charaNo):
    userCard, userChara, userLive2d, foundExisting = gacha.addMeguca(charaNo)
    response = {'userCardList': [userCard], 'userCharaList': [userChara], 'userLive2dList': [userLive2d]}

    if not foundExisting:
        userSectionList, userQuestBattleList = gacha.addStory(charaNo)
        response['userSectionList'] = userSectionList
        response['userQuestBattleList'] = userQuestBattleList
        
    return response

def getFormation(formationId):
    userFormation, exists = newUserObjectUtil.createUserFormation(formationId)
    if exists: return {}
    dataUtil.setUserObject('userFormationSheetList', formationId, userFormation)
    return {'userFormationSheetList': [userFormation]}

def getGift(giftId, amount):
    userGift = dataUtil.getUserObject('userGiftList', giftId)
    if userGift is None:
        newGift = dataUtil.masterGifts[giftId]
        newGift['rankGift'] = 'RANK_'+str(newGift['rank'])
        userGift = {
            "userId": dataUtil.userId,
            "giftId": giftId,
            "quantity": amount,
            "createdAt": newUserObjectUtil.nowstr(),
            "gift": newGift
        }
    userGift['quantity'] += amount
    dataUtil.setUserObject('userGiftList', giftId, userGift)
    return {'userGiftList': [userGift]}

def getGems(charaNo, amount):
    userChara = dataUtil.getUserObject('userCharaList', charaNo)
    userChara['lbItemNum'] += amount
    dataUtil.setUserObject('userCharaList', charaNo, userChara)
    return {'userCharaList': [userChara]}

def getItem(itemCode, amount, item=None):
    userItem = dataUtil.getUserObject('userItemList', itemCode)
    if userItem is None: # assumes only backgrounds and stuff
        if item is None:
            flask.abort(500, description='Item is None, but userItem doesn\'t already exist...')
        userItem, _ = newUserObjectUtil.createUserItem(item)
    userItem['quantity'] += amount
    dataUtil.setUserObject('userItemList', itemCode, userItem)
    return {'userItemList': [userItem]}

def getLive2d(charaId, live2dId, live2dItem):
    idx = int(str(charaId)+str(live2dId))
    userLive2d = dataUtil.getUserObject('userLive2dList', idx)
    if userLive2d is None:
        userLive2d, _ = newUserObjectUtil.createUserLive2d(charaId, live2dId, live2dItem['description'])
        dataUtil.setUserObject('userLive2dList', idx, userLive2d)
        return {'userLive2dList': [userLive2d]}
    return {} 

def getPiece(piece, isMax, num):
    newPieces = []
    for _ in range(num):
        newUserPiece, _ = newUserObjectUtil.createUserPiece(piece['pieceId'])
        if isMax:
            newUserPiece['level'] = userPiece.getMaxLevel(piece['rank'], 4)
            newUserPiece['lbcount'] = 4
            stats = userPiece.getStats(newUserPiece, newUserPiece['level'])
            for key in stats.keys():
                newUserPiece[key] = stats[key]
        newPieces.append(newUserPiece)
        dataUtil.setUserObject('userPieceList', newUserPiece['id'], newUserPiece)
    return {'userPieceList': newPieces}

def getCC(amount):
    gameUser = dataUtil.setGameUserValue('riche', dataUtil.getGameUserValue('riche')+amount)
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
    elif item['shopItemType'] == 'GEM':
        args.update(getGems(int(item['genericId']), body['num']))
    elif item['shopItemType'] == 'GIFT':
        newGifts = getGift(int(item['gift']['rewardCode'].split('_')[1]), body['num']*int(item['rewardCode'].split('_')[-1]))
        args['userGiftList'] = args.get('userGiftList', []) + newGifts['userGiftList']
    elif item['shopItemType'] == 'ITEM':
        newItems = getItem(item['item']['itemCode'], body['num']*int(item['rewardCode'].split('_')[-1]) if 'rewardCode' in item else 1, item['item'])
        args['userItemList'] = args.get('userItemList', []) + newItems['userItemList']
    elif item['shopItemType'] == 'LIVE2D':
        args.update(getLive2d(item['chara']['id'], item['live2d']['live2dId'], item['live2d']))
    elif item['shopItemType'] in ['MAXPIECE', 'PIECE']:
        args.update(getPiece(item['piece'], item['shopItemType']=='MAXPIECE', body['num']))
    return args

# TODO: handle cases where it's a meguca sent to the present box
def buy():
    body = flask.request.json
    shopList = dataUtil.readJson('data/shopList.json')

    currShop = {}
    for shop in shopList:
        if shop['shopId'] == body['shopId']:
            currShop = shop
            break
    if currShop == {}:
        flask.abort(400, description='{"errorTxt": "Trying to buy from a nonexistent shop","resultCode": "error","title": "Error"}')
    
    item = {}
    for shopItem in shop['shopItemList']:
        if shopItem['id'] == body['shopItemId']:
            item = shopItem
            break
    if item == {}:
        flask.abort(400, description='{"errorTxt": "Trying to buy something not in this shop","resultCode": "error","title": "Error"}')

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

    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    userShopItem = {
            "createdAt": nowstr,
            "num": body['num'],
            "shopItemId": body['shopItemId'],
            "userId": dataUtil.userId
        }
    args['userShopItemList'] = [userShopItem]
    path = 'data/user/userShopItemList.json'
    dataUtil.saveJson(path, dataUtil.readJson(path) + [userShopItem])

    return flask.jsonify(args)
    

def handleShop(endpoint):
    if endpoint.startswith('buy'):
        return buy()
    else:
        flask.abort(501, description="Not implemented")