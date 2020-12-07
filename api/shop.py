import flask
import json
from datetime import datetime
from api import userPiece, gacha
from uuid import uuid1
import logging

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr

logger = logging.getLogger('app.shop')

# This will only get you the lowest rarity card, but that's what all shop megucas have been...
def getCard(charaNo, amount):
    userCard, userChara, userLive2d, foundExisting = gacha.addMeguca(charaNo)

    if amount > 1:
        userChara['lbItemNum'] += amount - 1
        dt.setUserObject('userCharaList', charaNo, userChara)

    response = {'userCharaList': [userChara]}

    if not foundExisting:
        userSectionList, userQuestBattleList = gacha.addStory(charaNo)
        response['userSectionList'] = userSectionList
        response['userQuestBattleList'] = userQuestBattleList
        response['userLive2dList'] = [userLive2d]
        response['userCardList'] = [userCard]
        
    return response

def getFormation(formationId):
    userFormation, exists = newtil.createUserFormation(formationId)
    if exists: return {}
    dt.setUserObject('userFormationSheetList', formationId, userFormation)
    return {'userFormationSheetList': [userFormation]}

def getGift(giftId, amount):
    userGift = dt.getUserObject('userGiftList', giftId)
    if userGift is None:
        newGift = dt.masterGifts[giftId]
        newGift['rankGift'] = 'RANK_'+str(newGift['rank'])
        userGift = {
            "userId": dt.userId,
            "giftId": giftId,
            "quantity": amount,
            "createdAt": nowstr(),
            "gift": newGift
        }
    userGift['quantity'] += amount
    dt.setUserObject('userGiftList', giftId, userGift)
    return {'userGiftList': [userGift]}

def getGems(charaNo, amount):
    userChara = dt.getUserObject('userCharaList', charaNo)
    userChara['lbItemNum'] += amount
    dt.setUserObject('userCharaList', charaNo, userChara)
    return {'userCharaList': [userChara]}

def getItem(itemCode, amount, item=None):
    userItem = dt.getUserObject('userItemList', itemCode)
    if userItem is None: # assumes only backgrounds and stuff
        if item is None:
            flask.abort(500, description='Item is None, but userItem doesn\'t already exist...')
        userItem, _ = newtil.createUserItem(item)
    userItem['quantity'] += amount
    dt.setUserObject('userItemList', itemCode, userItem)
    return {'userItemList': [userItem]}

def getLive2d(charaId, live2dId, live2dItem):
    idx = int(str(charaId)+str(live2dId))
    userLive2d = dt.getUserObject('userLive2dList', idx)
    if userLive2d is None:
        userLive2d, _ = newtil.createUserLive2d(charaId, live2dId, live2dItem['description'])
        dt.setUserObject('userLive2dList', idx, userLive2d)
        return {'userLive2dList': [userLive2d]}
    return {} 

def getPiece(piece, isMax, num):
    newPieces = []
    for _ in range(num):
        newUserPiece, _ = newtil.createUserPiece(piece['pieceId'])
        if isMax:
            newUserPiece['level'] = userPiece.getMaxLevel(piece['rank'], 4)
            newUserPiece['lbcount'] = 4
            stats = userPiece.getStats(newUserPiece, newUserPiece['level'])
            for key in stats.keys():
                newUserPiece[key] = stats[key]
        newPieces.append(newUserPiece)
        dt.setUserObject('userPieceList', newUserPiece['id'], newUserPiece)
    return {'userPieceList': newPieces}

def getCC(amount):
    gameUser = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+amount)
    return {'gameUser': gameUser}

def obtainSet(item, body, args):
    for code in item['rewardCode'].split(','):
        itemType = code.split('_')[0]
        if itemType == 'ITEM':
            args = dt.updateJson(args, getItem('_'.join(code.split('_')[1:-1]), int(code.split('_')[-1])*body['num']))
        elif itemType == 'RICHE':
            args = dt.updateJson(args, getCC(int(code.split('_')[-1])*body['num']))
        elif itemType == 'GIFT':
            args = dt.updateJson(args, getGift(int(code.split('_')[1]), int(code.split('_')[-1])*body['num']))

def obtain(item, body, args):
    if item['shopItemType'] == 'CARD':
        args = dt.updateJson(args, getCard(item['card']['charaNo'], body['num']))
    elif item['shopItemType'] == 'FORMATION_SHEET':
        args = dt.updateJson(args, getFormation(item['formationSheet']['id']))
    elif item['shopItemType'] == 'GEM':
        args = dt.updateJson(args, getGems(int(item['genericId']), body['num']))
    elif item['shopItemType'] == 'GIFT':
        newGifts = getGift(int(item['gift']['rewardCode'].split('_')[1]), body['num']*int(item['rewardCode'].split('_')[-1]))
        args['userGiftList'] = args.get('userGiftList', []) + newGifts['userGiftList']
    elif item['shopItemType'] == 'ITEM':
        newItems = getItem(item['item']['itemCode'], body['num']*int(item['rewardCode'].split('_')[-1]) if 'rewardCode' in item else 1, item['item'])
        args['userItemList'] = args.get('userItemList', []) + newItems['userItemList']
    elif item['shopItemType'] == 'LIVE2D':
        args = dt.updateJson(args, getLive2d(item['chara']['id'], item['live2d']['live2dId'], item['live2d']))
    elif item['shopItemType'] in ['MAXPIECE', 'PIECE']:
        args = dt.updateJson(args, getPiece(item['piece'], item['shopItemType']=='MAXPIECE', body['num']))
    return args

# TODO: handle cases where it's a meguca sent to the present box
def buy():
    body = flask.request.json
    shopList = dt.readJson('data/shopList.json')

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
            args = dt.updateJson(args, spendArgs)
    elif item['consumeType'] == 'MONEY':
        itemList = gacha.spend('MONEY', item['needNumber']*body['num'])
        if 'userItemList' in args:
            args['userItemList'] += itemList
        else:
            args['userItemList'] = itemList

    userShopItem = {
            "createdAt": nowstr(),
            "num": body['num'],
            "shopItemId": body['shopItemId'],
            "userId": dt.userId
        }
    args['userShopItemList'] = [userShopItem]
    path = 'data/user/userShopItemList.json'
    dt.saveJson(path, dt.readJson(path) + [userShopItem])

    return flask.jsonify(args)
    

def handleShop(endpoint):
    if endpoint.startswith('buy'):
        return buy()
    else:
        logger.error('Missing implementation: shop/'+endpoint)
        flask.abort(501, description="Not implemented")