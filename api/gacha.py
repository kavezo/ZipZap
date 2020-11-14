import flask
import os
import numpy as np
import random
from datetime import datetime
from uuid import uuid1

from util import dataUtil, newUserObjectUtil

cardsByRarity = [[],[],[],[],[]]
for chara in dataUtil.masterCards.values():
    idx = int(chara['cardList'][0]['card']['rank'][-1])-1
    cardsByRarity[idx].append(chara)

piecesByRarity = [[],[],[],[],[]]
for piece in dataUtil.masterPieces.values():
    idx = int(piece['rank'][-1])-1
    piecesByRarity[idx].append(piece)

enhanceGems = [item for item in dataUtil.masterItems.values() if item['itemCode'].startswith('COMPOSE')]

def drawOneNormal():
    itemType = np.random.choice(['g', 'm3', 'm2', 'm1', 'm0'], p=[0.5, 0.05, 0.1, 0.15, 0.2])
    if itemType == 'g':
        result = np.random.choice(enhanceGems)
        return [result], 'g'
    else:
        result = np.random.choice(piecesByRarity[int(itemType[-1])])
        return [result], itemType

def drawTenNormal():
    results = []
    itemTypes = []
    for _ in range(10):
        result, itemType = drawOneNormal()
        results += result
        itemTypes.append(itemType)
    return results, itemTypes

def getGachaRates():
    return dataUtil.readJson('data/gacha_rates.json')

def drawOnePremium(pity, probs=None):
    allRates = getGachaRates()
    if probs is None:
        probs = allRates["normal"]
    if pity == 99:
        return [np.random.choice(cardsByRarity[3])], 'p3', 0
    else:
        itemType = np.random.choice(['p3', 'p2', 'p1', 'm3', 'm2', 'm1'], p=probs) # indices are one lower than rarity
        if itemType.startswith('p'):
            return [np.random.choice(cardsByRarity[int(itemType[-1])])], itemType, 0 if itemType=='p3'else pity+1
        else:
            return [np.random.choice(piecesByRarity[int(itemType[-1])])], itemType, pity+1

def drawTenPremium(pity):
    allRates = getGachaRates()

    # highest rarity meguca to lowest, then highest rarity meme to lowest
    normal = allRates["normal"]
    meguca = allRates["meguca"]
    threestar = allRates["threestar"]

    gotMeguca = False
    got3s = False

    results = []
    resultItemTypes = []
    for _ in range(8):
        result, itemType, pity = drawOnePremium(pity, normal)
        results += result
        resultItemTypes.append(itemType)
        gotMeguca = gotMeguca or itemType.startswith('p')
        got3s = got3s or int(itemType[-1]) > 1

    if not got3s and pity != 100:
        result, itemType, pity = drawOnePremium(pity, threestar)
        gotMeguca = gotMeguca or itemType.startswith('p')
        results += result
        resultItemTypes.append(itemType)
    if not gotMeguca and pity != 100:
        result, itemType, pity = drawOnePremium(pity, meguca)
        results += result
        resultItemTypes.append(itemType)

    for _ in range(10-len(results)):
        result, itemType, pity = drawOnePremium(pity, normal)
        results += result
        resultItemTypes.append(itemType)
    
    return results, resultItemTypes, pity

def setUpPity(groupId, pity=None):
    pityGroup = dataUtil.getUserObject('userGachaGroupList', groupId)
    if pityGroup is not None:
        if pity is None:
            return pityGroup, pityGroup['count']
        else:
            pityGroup['count'] = pity
            dataUtil.setUserObject('userGachaGroupList', groupId, pityGroup)
            return pityGroup, None

    # didn't find matching group
    newPity = newUserObjectUtil.createUserGachaGroup(groupId)
    dataUtil.setUserObject('userGachaGroupList', groupId, newPity)
    return newPity, 0

def spend(itemId, amount, preferredItemId = None, preferredItemAmount = 1):
    getItem = lambda x: dataUtil.getUserObject('userItemList', x)
    setItem = lambda x, y: dataUtil.setUserObject('userItemList', x, y)
    
    updatedItems = []
    foundPreferred = False
    if preferredItemId is not None:
        item = getItem(preferredItemId)
        if item['quantity'] >= preferredItemAmount:
            print("Spending " + str(preferredItemAmount) + " " + preferredItemId)
            item['quantity'] -= preferredItemAmount
            foundPreferred = True
            updatedItems.append(item)
            setItem(preferredItemId, item)
    
    if not foundPreferred:
        if itemId != 'MONEY':
            item = getItem(itemId)
            print("Spending " + str(amount) + " " + itemId)
            item['quantity'] -= amount
            updatedItems.append(item)
            setItem(itemId, item)

        else: # spend paid gems after free gems, and also the ID is different
            print("Spending " + str(amount) + " " + itemId)
            freeItem = getItem('PRESENTED_MONEY')
            paidItem = getItem('MONEY')

            remainder = amount - freeItem['quantity']
            freeItem['quantity'] -= min(freeItem['quantity'], amount)
            if remainder > 0:
                paidItem['quantity'] -= remainder

            updatedItems += [freeItem, paidItem]

            setItem('PRESENTED_MONEY', freeItem)
            setItem('MONEY', paidItem)

    return updatedItems

def addGem(gem):
    item = dataUtil.getUserObject('userItemList', gem['itemCode'])
    item['quantity'] += 1
    dataUtil.setUserObject('userItemList', gem['itemCode'], item)
    return item

def addMeguca(charaId):
    # TODO: get the story of the meguca
    userChara = dataUtil.getUserObject('userCharaList', charaId)
    foundExisting = userChara is not None

    if not foundExisting:
        userCard, userChara, userLive2d = newUserObjectUtil.createUserMeguca(charaId)
        dataUtil.setUserObject('userCardList', userCard['id'], userCard)
        dataUtil.setUserObject('userCharaList', charaId, userChara)

        live2dPath = 'data/user/userLive2dList.json'
        dataUtil.saveJson('data/user/userLive2dList.json', dataUtil.readJson(live2dPath) + [userLive2d])
    else:
        userChara['lbItemNum'] += 1
        dataUtil.setUserObject('userCharaList', userChara['userCardId'], userChara)

        userCard = dataUtil.getUserObject('userCardList', userChara['userCardId'])
        userLive2d = dataUtil.getUserObject('userLive2dList', int(str(charaId)+'00'))

    return userCard, userChara, userLive2d, foundExisting

def addPiece(pieceId):
    userPiece, foundExisting = newUserObjectUtil.createUserMemoria(pieceId)
    
    if not foundExisting:
        newPieceColle = {
            "createdAt": userPiece['createdAt'],
            "maxLbCount": 0,
            "maxLevel": 1,
            "piece": piece,
            "pieceId": pieceId,
            "userId": dataUtil.userId
        }
        dataUtil.setUserObject('userPieceCollectionList', pieceId, newPieceColle)
    return userPiece, foundExisting
    
def draw():
    # TODO: give a destiny gem if there's a dupe in the same multi-pull
    # TODO: get stories

    # handle different types of gachas
    body = flask.request.json

    chosenGacha = None
    for gacha in dataUtil.readJson('data/gachaScheduleList.json'):
        if gacha['id'] == body['gachaScheduleId']:
            chosenGacha = gacha
            break
    if chosenGacha is None:
        flask.abort(404, description="Tried to pull on a gacha that doesn't exist...")

    if 'gachaGroupId' in chosenGacha.keys():
        _, pity = setUpPity(chosenGacha['gachaGroupId'])
    else:
        pity = 0

    # draw
    draw10 = body['gachaBeanKind'].endswith('10') or body['gachaBeanKind'] == 'SELECTABLE_TUTORIAL'
    results = []
    itemTypes = []
    if body['gachaBeanKind'].startswith('NORMAL'):
        if draw10:
            results, itemTypes = drawTenNormal()
        else:
            results, itemTypes = drawOneNormal()
    else:
        if draw10:
            results, itemTypes, pity = drawTenPremium(pity)
        else:
            results, itemTypes, pity = drawOnePremium(pity)

    if 'gachaGroupId' in chosenGacha.keys():
        pityGroup, _ = setUpPity(chosenGacha['gachaGroupId'], pity)
    else:
        pityGroup = None
    
    # sort into lists
    userCardList = []
    userCharaList = []
    userPieceList = []
    userLive2dList = []
    userItemList = []

    responseList = []

    for result, itemType in zip(results, itemTypes):
        if itemType.startswith('g'):
            userItemList.append(addGem(result))
            responseList.append({
                "direction": 5,
                "displayName": result['name'],
                "isNew": False,
                "itemId": result['itemCode'],
                "rarity": 'RANK_'+str(result['name'].count('+')+1),
                "type": "ITEM"
            })
        if itemType.startswith('p'):
            card, chara, live2d, foundExisting = addMeguca(result['charaId'])
            if not foundExisting:
                userCardList.append(card)
                userLive2dList.append(live2d)
            userCharaList.append(chara)
            directionType = 3
            if result['cardList'][0]['card']['rank'][-1] == "4":
                # give it the rainbow swirlies
                directionType = 4
            responseList.append({
                "type": "CARD",
                "rarity": result['cardList'][0]['card']['rank'],
                "maxRarity": result['cardList'][-1]['card']['rank'],
                "cardId": result['cardList'][0]['cardId'],
                "attributeId": result['chara']['attributeId'],
                "charaId": result['charaId'],
                "direction": directionType,
                "displayName": result['chara']['name'],
                "isNew": not foundExisting
            })
            if foundExisting:
                responseList[-1]["itemId"] = "LIMIT_BREAK_CHARA"
        if itemType.startswith('m'):
            userPiece, foundExisting = addPiece(result['pieceId'])
            userPieceList.append(userPiece)
            directionType = 1
            if result['rank'][-1] == "4":
                # give it the memoria equivalent of the rainbow swirlies
                directionType = 2
            responseList.append({
                "type": "PIECE",
                "rarity": result['rank'],
                "pieceId": result['pieceId'],
                "direction": directionType,
                "displayName": result['pieceName'],
                "isNew": not foundExisting
            })

    # spend items
    gachaKind = None
    for kind in chosenGacha['gachaKindList']:
        if kind['beanKind'] == body['gachaBeanKind']:
            gachaKind = kind

    userItemList += \
        spend(gachaKind['needPointKind'], gachaKind['needQuantity'], gachaKind['substituteItemId'] if 'substituteItemId' in gachaKind else None)

    # create response
    gachaAnimation = {
            "live2dDetail": gachaKind['live2dDetail'],
            "messageId": gachaKind['messageId'],
            "message": gachaKind['message'],
            # Determines which picture to show in the intro animation
            #
            # first picture
            # 1 = flower thingy (default, no real meaning)
            # 2 = inverted flower thingy (should mean at least 1 3+ star CARD (not necessarily meguca, could be memoria))
            "direction1": 1,
            #
            # second picture
            # 1 = mokyuu (default, no real meaning)
            # 2 = attribute (specified with "direction2AttributeId")
            "direction2": 1,
            #
            # third picture
            # 1 = spear thingy (default, no real meaning)
            # 2 = iroha (should mean at least 1 3+ star)
            # 3 = mikazuki villa (at least 1 4 star)
            "direction3": 1,
            "gachaResultList": responseList
        }

    high_rarity_pulled = [thingy for thingy in responseList if thingy["rarity"] == "RANK_3" or thingy["rarity"] == "RANK_4"]
    cards_pulled = [thingy for thingy in responseList if thingy["type"] == "CARD"]
    any_3stars_pulled = [card for card in cards_pulled if card["rarity"] == "RANK_3"]
    any_4stars_pulled = [card for card in cards_pulled if card["rarity"] == "RANK_4"]

    # if any high rarity thingies pulled, set direction1
    if len(high_rarity_pulled) >= 1:
        gachaAnimation["direction1"] = 2

    # 50-50 chance of displaying a random card's attribute symbol instead of mokyuu
    # but only if cards were pulled (i.e. not for FP gacha)
    if len(cards_pulled) >= 1 and random.randint(1, 2) == 2:
        random_card = random.choice(cards_pulled)
        gachaAnimation["direction2"] = 2
        gachaAnimation["direction2AttributeId"] = random_card["attributeId"]

    if len(any_4stars_pulled) >= 1:
        # show mikazuki villa if any 4 stars were pulled
        gachaAnimation["direction3"] = 3
    elif len(any_3stars_pulled) >= 1:
        # show iroha if any 3 stars were pulled
        gachaAnimation["direction3"] = 2

    if pityGroup is not None:
        gachaAnimation["userGachaGroup"] = pityGroup
    response = {
        "resultCode": "success",
        "gachaAnimation": gachaAnimation,
        "userCardList": userCardList,
        "userCharaList": userCharaList,
        "userLive2dList": userLive2dList,
        "userItemList": userItemList,
        "userPieceList": userPieceList
    }

    # add to user history
    pullId = str(uuid1())
    if not os.path.exists('data/user/gachaHistory'):
        os.mkdir('data/user/gachaHistory')
    dataUtil.saveJson('data/user/gachaHistory/'+pullId+'.json', {'gachaAnimation': gachaAnimation})
    newHistory = {
        "id": pullId,
        "userId": dataUtil.userId,
        "gachaScheduleId": body['gachaScheduleId'],
        "gachaSchedule": chosenGacha,
        "gachaBeanKind": body['gachaBeanKind'],
        "bonusTimeFlg": False,
        "createdAt": (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    }
    print(gachaAnimation)
    dataUtil.setUserObject('gachaHistoryList', pullId, newHistory)
    return flask.jsonify(response)

def getHistory(endpoint):
    pullId = endpoint.split('/')[-1]
    if os.path.exists('data/user/gachaHistory/'+pullId+'.json'):
        response = dataUtil.readJson('data/user/gachaHistory/'+pullId+'.json')
        response['resultCode'] = 'success'
        return flask.jsonify(response)
    else:
        flask.abort(404, description='Could not find specified history.')

def getProbability():
    return dataUtil.readJson('data/gachaProbability.json')

def handleGacha(endpoint):
    if endpoint.startswith('draw'):
        return draw()
    elif endpoint.startswith('result'):
        return getHistory(endpoint)
    elif endpoint.startswith('probability'):
        return getProbability()
    else:
        print('gacha/'+endpoint)
        flask.abort(501, description='Not implemented')
