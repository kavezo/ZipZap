import flask
import os
import numpy as np
import random
from datetime import datetime
from uuid import uuid1
import logging

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr, beforeToday

logger = logging.getLogger('app.gacha')

cardsByRarity = [[],[],[],[],[]]
for chara in dt.masterCards.values():
    idx = int(chara['cardList'][0]['card']['rank'][-1])-1
    cardsByRarity[idx].append(chara)

piecesByRarity = [[],[],[],[],[]]
for piece in dt.masterPieces.values():
    idx = int(piece['rank'][-1])-1
    piecesByRarity[idx].append(piece)

enhanceGems = [item for item in dt.masterItems.values() if item['itemCode'].startswith('COMPOSE')]

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
    return dt.readJson('data/gacha_rates.json')

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
    pityGroup = dt.getUserObject('userGachaGroupList', groupId)
    if pityGroup is not None:
        if pity is None:
            return pityGroup, pityGroup['count']
        else:
            pityGroup['count'] = pity
            dt.setUserObject('userGachaGroupList', groupId, pityGroup)
            return pityGroup, None

    # didn't find matching group
    newPity = newtil.createUserGachaGroup(groupId)
    dt.setUserObject('userGachaGroupList', groupId, newPity)
    return newPity, 0

def spend(itemId, amount, preferredItemId = None, preferredItemAmount = 1):
    getItem = lambda x: dt.getUserObject('userItemList', x)
    setItem = lambda x, y: dt.setUserObject('userItemList', x, y)

    if itemId == 'PURCHASED_MONEY': itemId = 'MONEY'
    if preferredItemId == 'PURCHASED_MONEY': preferredItemId = 'MONEY'
    
    updatedItems = []
    foundPreferred = False
    if preferredItemId is not None:
        item = getItem(preferredItemId)
        if item['quantity'] >= preferredItemAmount:
            logger.info("Spending " + str(preferredItemAmount) + " " + preferredItemId)
            item['quantity'] -= preferredItemAmount
            foundPreferred = True
            updatedItems.append(item)
            setItem(preferredItemId, item)
    
    if not foundPreferred:
        if itemId != 'MONEY':
            item = getItem(itemId)
            logger.info("Spending " + str(amount) + " " + itemId)
            item['quantity'] -= amount
            updatedItems.append(item)
            setItem(itemId, item)

        else: # spend paid gems after free gems, and also the ID is different
            logger.info("Spending " + str(amount) + " " + itemId)
            freeItem = getItem('PRESENTED_MONEY')
            paidItem = getItem('MONEY')

            remainder = amount - freeItem['quantity']
            freeItem['quantity'] -= min(freeItem['quantity'], amount)
            if remainder > 0:
                paidItem['quantity'] -= remainder

            updatedItems.append(freeItem)
            if paidItem is not None:
                updatedItems.append(paidItem)

            setItem('PRESENTED_MONEY', freeItem)
            setItem('MONEY', paidItem)

    return updatedItems

def addGem(gem):
    item = dt.getUserObject('userItemList', gem['itemCode'])
    item['quantity'] += 1
    dt.setUserObject('userItemList', gem['itemCode'], item)
    return item

def addStory(charaId):
    existingSections = dt.listUserObjectKeys('userSectionList')
    validSections = dt.masterSections.keys()
    userSectionDict = {}
    for i in range(4):
        sectionId = int('3{0}{1}'.format(charaId, i+1))
        if sectionId in existingSections: continue
        if sectionId in validSections:
            userSectionDict[sectionId] = {
                "userId": dt.userId,
                "sectionId": sectionId,
                "section": dt.masterSections[sectionId],
                "canPlay": str(sectionId).endswith('1'),
                "cleared": False,
                "createdAt": nowstr()
            }

    existingBattles = dt.listUserObjectKeys('userQuestBattleList')
    validBattles = dt.masterBattles.keys()
    userQuestBattleDict = {}
    for i in range(4):
        for j in range(3):
            battleId = int('3{0}{1}{2}'.format(charaId, i+1, j+1))
            if battleId in existingBattles: continue
            if battleId in validBattles:
                userQuestBattleDict[battleId] = {
                    "userId": dt.userId,
                    "questBattleId": battleId,
                    "questBattle": dt.masterBattles[battleId],
                    "cleared": False,
                    "missionStatus1": "NON_CLEAR",
                    "missionStatus2": "NON_CLEAR",
                    "missionStatus3": "NON_CLEAR",
                    "rewardDone": False,
                    "createdAt": nowstr()
                }
    
    dt.batchSetUserObject('userSectionList', userSectionDict)
    dt.batchSetUserObject('userQuestBattleList', userQuestBattleDict)
    return list(userSectionDict.values()), list(userQuestBattleDict.values())

def addDuoLive2d(chara):
    charaId = chara['id']
    if '&' in chara['name']:
        name1, name2 = ['Magical Girl ({0})'.format(name) for name in chara['name'].split(' & ')]
    else:
        name1, name2 = chara['name'], chara['name']
    userLive2d1, _ = newtil.createUserLive2d(charaId, '01', name1)
    userLive2d2, _ = newtil.createUserLive2d(charaId, '02', name2)
    return [userLive2d1, userLive2d2]

def addMeguca(charaId):
    userChara = dt.getUserObject('userCharaList', charaId)
    foundExisting = userChara is not None

    live2ds = []
    if not foundExisting:
        userCard, userChara, userLive2d = newtil.createUserMeguca(charaId)
        dt.setUserObject('userCardList', userCard['id'], userCard)
        dt.setUserObject('userCharaList', charaId, userChara)

        live2ds = [userLive2d] + addDuoLive2d(userChara['chara'])
        live2dPath = 'data/user/userLive2dList.json'
        dt.saveJson(live2dPath, dt.readJson(live2dPath) + live2ds)
    else:
        userChara['lbItemNum'] += 1
        dt.setUserObject('userCharaList', charaId, userChara)

        userCard = dt.getUserObject('userCardList', userChara['userCardId'])
        userLive2d = dt.getUserObject('userLive2dList', int(str(charaId)+'00'))
        live2ds = [userLive2d]

    return userCard, userChara, live2ds, foundExisting

def addPiece(pieceId):
    foundExisting = False
    for userPiece in dt.readJson('data/user/userPieceCollectionList.json'):
        foundExisting = foundExisting or (userPiece['pieceId'] == pieceId)
    
    userPiece = newtil.createUserMemoria(pieceId)
    
    if not foundExisting:
        newPieceColle = {
            "createdAt": userPiece['createdAt'],
            "maxLbCount": 0,
            "maxLevel": 1,
            "piece": userPiece['piece'],
            "pieceId": pieceId,
            "userId": dt.userId
        }
        dt.setUserObject('userPieceCollectionList', pieceId, newPieceColle)
    return userPiece, foundExisting
    
def draw():
    # handle different types of gachas
    body = flask.request.json

    chosenGacha = None
    for gacha in dt.readJson('data/gachaScheduleList.json'):
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
    isFreePull = False
    results = []
    itemTypes = []
    if body['gachaBeanKind'].startswith('NORMAL'):
        if draw10:
            results, itemTypes = drawTenNormal()
            isFreePull = beforeToday(dt.getGameUserValue('freeGachaAt'))
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
    userSectionList = []
    userQuestBattleList = []

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
            card, chara, live2ds, foundExisting = addMeguca(result['charaId'])
            if not foundExisting:
                userCardList.append(card)
                userLive2dList += live2ds
                newSectionList, newQuestBattleList = addStory(result['charaId'])
                userSectionList += newSectionList
                userQuestBattleList += newQuestBattleList
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

    if not isFreePull:
        userItemList += \
            spend(gachaKind['needPointKind'], 
                gachaKind['needQuantity'], 
                gachaKind['substituteItemId'] if 'substituteItemId' in gachaKind else None)

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

    if isFreePull:
        response['gameUser'] = dt.setGameUserValue('freeGachaAt', nowstr())

    if len(userSectionList) > 0: response['userSectionList'] = userSectionList
    if len(userQuestBattleList) > 0: response['userQuestBattleList'] = userQuestBattleList

    # add to user history
    pullId = str(uuid1())
    if not os.path.exists('data/user/gachaHistory'):
        os.mkdir('data/user/gachaHistory')
    dt.saveJson('data/user/gachaHistory/'+pullId+'.json', {'gachaAnimation': gachaAnimation})
    newHistory = {
        "id": pullId,
        "userId": dt.userId,
        "gachaScheduleId": body['gachaScheduleId'],
        "gachaSchedule": chosenGacha,
        "gachaBeanKind": body['gachaBeanKind'],
        "bonusTimeFlg": False,
        "createdAt": nowstr()
    }
    dt.setUserObject('gachaHistoryList', pullId, newHistory)
    return flask.jsonify(response)

def getHistory(endpoint):
    pullId = endpoint.split('/')[-1]
    if os.path.exists('data/user/gachaHistory/'+pullId+'.json'):
        response = dt.readJson('data/user/gachaHistory/'+pullId+'.json')
        response['resultCode'] = 'success'
        return flask.jsonify(response)
    else:
        flask.abort(404, description='Could not find specified history.')

def getProbability():
    return dt.readJson('data/gachaProbability.json')

def handleGacha(endpoint):
    if endpoint.startswith('draw'):
        return draw()
    elif endpoint.startswith('result'):
        return getHistory(endpoint)
    elif endpoint.startswith('probability'):
        return getProbability()
    else:
        logger.error('Missing implementation: gacha/'+endpoint)
        flask.abort(501, description='Not implemented')
