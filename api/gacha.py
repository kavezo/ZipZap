import flask
import json
import os
import numpy as np
import random
from datetime import datetime
from uuid import uuid1

with open('data/cards.json', encoding='utf-8') as f:
    allCards = json.load(f)
cardsByRarity = [[],[],[],[],[]]
for chara in allCards:
    idx = int(chara['cardList'][0]['card']['rank'][-1])-1
    cardsByRarity[idx].append(chara)

with open('data/pieces.json', encoding='utf-8') as f:
    allPieces = json.load(f)
piecesByRarity = [[],[],[],[],[]]
for piece in allPieces:
    idx = int(piece['rank'][-1])-1
    piecesByRarity[idx].append(piece)

with open('data/itemList.json', encoding='utf-8') as f:
    allItems = json.load(f)
enhanceGems = [item for item in allItems if item['itemCode'].startswith('COMPOSE')]

with open('data/user/user.json', encoding='utf-8') as f:
    userInfo = json.load(f)
userId = userInfo['id']

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
    with open('data/gacha_rates.json', encoding='utf-8') as f:
        return json.load(f)

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
    with open('data/user/userGachaGroupList.json', encoding='utf-8') as f:
        pityList = json.load(f)

    for i in range(len(pityList)):
        pityGroup = pityList[i]
        if pityGroup['gachaGroupId'] == groupId and pity is None:
            return pityGroup, pityGroup['count']
        else:
            pityGroup['count'] = pity
            pityList[i] = pityGroup
            with open('data/user/userGachaGroupList.json', 'w', encoding='utf-8') as f:
                json.dump(pityList, f, ensure_ascii=False)
            return pityGroup, None
    # didn't find matching group
    newPity = {
        "userId": userId,
        "gachaGroupId": groupId,
        "count": 0,
        "paid": 0,
        "totalCount": 0,
        "dailyCount": 0,
        "weeklyCount": 0,
        "monthlyCount": 0,
        "currentScheduleId": 20,
        "resetCount": 0,
        "createdAt": str(datetime.now()).split('.')[0].replace('-', '/')
    }
    pityList.append(newPity)
    with open('data/user/userGachaGroupList.json', 'w', encoding='utf-8') as f:
        json.dump(pityList, f, ensure_ascii=False)
    return newPity, 0

def spend(itemId, amount, preferredItemId = None, preferredItemAmount = 1):
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        userItems = json.load(f)
    
    updatedItems = []
    foundPreferred = False
    if preferredItemId is not None:
        for i in range(len(userItems)):
            item = userItems[i]
            if item['itemId'] == preferredItemId and item['quantity'] >= preferredItemAmount:
                print("Spending " + str(preferredItemAmount) + " " + preferredItemId)
                item['quantity'] -= preferredItemAmount
                userItems[i] = item
                foundPreferred = True
                updatedItems.append(item)
                break
    
    if not foundPreferred:
        if itemId != 'MONEY':
            for i in range(len(userItems)):
                item = userItems[i]
                if item['itemId'] == itemId:
                    print("Spending " + str(amount) + " " + itemId)
                    item['quantity'] -= amount
                    userItems[i] = item
                    updatedItems.append(item)
                    break
        else: # spend paid gems after free gems, and also the ID is different
            print("Spending " + str(amount) + " " + itemId)
            paidIdx = 0
            freeIdx = 0
            for i in range(len(userItems)):
                item = userItems[i]
                if item['itemId'] == 'MONEY':
                    paidIdx = i
                if item['itemId'] == 'PRESENTED_MONEY':
                    freeIdx = i
            
            numFreeStones = userItems[freeIdx]['quantity']
            userItems[freeIdx]['quantity'] -= amount
            if userItems[freeIdx]['quantity'] < 0:
                userItems[freeIdx]['quantity'] = 0
                amount -= numFreeStones
                userItems[paidIdx]['quantity'] -= amount

            updatedItems += [userItems[freeIdx], userItems[paidIdx]]

    
    with open('data/user/userItemList.json', 'w', encoding='utf-8') as f:
        json.dump(userItems, f, ensure_ascii=False)
    return updatedItems

def addGem(gem):
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        userItems = json.load(f)

    for i in range(len(userItems)):
        if userItems[i]['itemId'] == gem['itemCode']:
            userItems[i]['quantity'] += 1
            break
    with open('data/user/userItemList.json', 'w', encoding='utf-8') as f:
        json.dump(userItems, f, ensure_ascii=False)
    return userItems[i]

def addMeguca(chara):
    # TODO: get the story of the meguca
    with open('data/user/userLive2dList.json', encoding='utf-8') as f:
        live2dList = json.load(f)
    with open('data/user/userCardList.json', encoding='utf-8') as f:
        cardList = json.load(f)
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        charaList = json.load(f)

    foundExisting = False
    existingUserChara = None
    for i in range(len(charaList)):
        if charaList[i]['charaId'] == chara['charaId']:
            charaList[i]['lbItemNum'] += 1
            existingUserChara = charaList[i]
            foundExisting = True

    userCardId = str(uuid1()) if not foundExisting else existingUserChara['userCardId']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/') if not foundExisting else existingUserChara['createdAt']

    card = chara['cardList'][0]['card']
    userCard = {
        "id": userCardId,
        "userId": userId,
        "cardId": card['cardId'],
        "displayCardId": card['cardId'],
        "revision": 0,
        "attack": card['attack'],
        "defense": card['defense'],
        "hp": card['hp'],
        "level": 1,
        "experience": 0,
        "magiaLevel": 1,
        "enabled": True,
        "customized1": False,
        "customized2": False,
        "customized3": False,
        "customized4": False,
        "customized5": False,
        "customized6": False,
        "createdAt": nowstr,
        "card": card
    }
    userChara = {
        "userId": userId,
        "charaId": chara['charaId'],
        "chara": chara['chara'],
        "bondsTotalPt": 0,
        "userCardId": userCardId,
        "lbItemNum": 0 if not foundExisting else existingUserChara['lbItemNum'],
        "visualizable": True,
        "commandVisualType": "CHARA",
        "commandVisualId": chara['charaId'],
        "live2dId": "00",
        "createdAt": nowstr
    }
    userLive2d = {
        "userId": userId,
        "charaId": chara['charaId'],
        "live2dId": "00",
        "live2d": {
            "charaId": chara['charaId'],
            "live2dId": "00",
            "description": "Magical Girl",
            "defaultOpened": True,
            "voicePrefixNo": "00"
        },
        "createdAt": nowstr
    }

    if not foundExisting:
        live2dList.append(userLive2d)
        cardList.append(userCard)
        charaList.append(userChara)
        with open('data/user/userLive2dList.json', 'w', encoding='utf-8') as f:
            json.dump(live2dList, f, ensure_ascii=False)
        with open('data/user/userCardList.json', 'w', encoding='utf-8') as f:
            json.dump(cardList, f, ensure_ascii=False)
    with open('data/user/userCharaList.json', 'w', encoding='utf-8') as f:
        json.dump(charaList, f, ensure_ascii=False)

    return userCard, userChara, userLive2d, foundExisting

def addPiece(piece):
    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        pieceList = json.load(f)

    foundExisting = False
    for existingPiece in pieceList:
        if existingPiece['pieceId'] == piece['pieceId']:
            foundExisting = True
            break

    userPieceId = str(uuid1())
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')
    userPiece = {
        "id": userPieceId,
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
    }
    pieceList.append(userPiece)
    
    if not foundExisting:
        with open('data/user/userPieceCollectionList.json', encoding='utf-8') as f:
            pieceCollection = json.load(f)
        existingIds = [collPiece['pieceId'] for collPiece in pieceCollection]
        if not piece['pieceId'] in existingIds:
            pieceCollection.append({
                "createdAt": nowstr,
                "maxLbCount": 0,
                "maxLevel": 1,
                "piece": piece,
                "pieceId": piece['pieceId'],
                "userId": userId
            })
        with open('data/user/userPieceCollectionList.json', 'w+', encoding='utf-8') as f:
            json.dump(pieceCollection, f, ensure_ascii=False)

    with open('data/user/userPieceList.json', 'w', encoding='utf-8') as f:
        json.dump(pieceList, f, ensure_ascii=False)
    return userPiece, foundExisting
    
def draw():
    # TODO: give a destiny gem if there's a dupe in the same multi-pull
    # TODO: get stories

    # handle different types of gachas
    body = flask.request.json

    with open('data/gachaScheduleList.json', encoding='utf-8') as f:
        gachas = json.load(f)
    
    chosenGacha = None
    for gacha in gachas:
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
            card, chara, live2d, foundExisting = addMeguca(result)
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
            userPiece, foundExisting = addPiece(result)
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
        
    with open('data/user/gachaHistory/'+pullId+'.json', 'w+', encoding='utf-8') as f:
        json.dump({'gachaAnimation': response['gachaAnimation']}, f, ensure_ascii=False)

    with open('data/user/gachaHistoryList.json', encoding='utf-8') as f:
        historyList = json.load(f)
    historyList.append({
            "id": pullId,
            "userId": userId,
            "gachaScheduleId": body['gachaScheduleId'],
            "gachaSchedule": chosenGacha,
            "gachaBeanKind": body['gachaBeanKind'],
            "bonusTimeFlg": False,
            "createdAt": str(datetime.now()).split('.')[0].replace('-', '/')
        })
    with open('data/user/gachaHistoryList.json', 'w+', encoding='utf-8') as f:
        json.dump(historyList, f, ensure_ascii=False)
    return flask.jsonify(response)

def getHistory(endpoint):
    pullId = endpoint.split('/')[-1]
    if os.path.exists('data/user/gachaHistory/'+pullId+'.json'):
        with open('data/user/gachaHistory/'+pullId+'.json', encoding='utf-8') as f:
            response = json.load(f)
        response['resultCode'] = 'success'
        return flask.jsonify(response)
    else:
        flask.abort(404, description='Could not find specified history.')

def getProbability():
    with open('data/gachaProbability.json', encoding='utf-8') as f:
        probabilities = f.read()
    return probabilities

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
