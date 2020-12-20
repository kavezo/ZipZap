import flask
import copy
import numpy as np
import re
import json
from uuid import uuid1
import logging

from util import dataUtil as dt
from util import homuUtil as homu

logger = logging.getLogger('app.quest.get')

mirrorScenario = {
    "bgm": "bgm01_battle01",
    "bgmBoss": "bgm01_battle01",
    "difficulty": 0,
    "cost": 0,
    "missionList": [],
    "sheetType": 9,
    "auto": False
}

def extractArts(userCard, userPieceList):
    arts = []
    if userCard is not None:
        arts += [userCard['card']['cardMagia'][key] for key in userCard['card']['cardMagia'].keys() if key.startswith('art')
                 and not key.startswith('artId')]

        arts += [userCard['card']['cardSkill'][key] for key in userCard['card']['cardSkill'].keys() if key.startswith('art')
                 and not key.startswith('artId')]
        
        if 'doppelCardMagia' in userCard['card']:
            arts += [userCard['card']['doppelCardMagia'][key] for key in userCard['card']['doppelCardMagia'].keys() 
                    if key.startswith('art') and not key.startswith('artId')]
    for piece in userPieceList:
        skills = [piece['piece'][key] for key in piece['piece'].keys() if key.startswith('pieceSkill')]
        for skill in skills:
            arts += [skill[key] for key in skill.keys() if key.startswith('art')
                     and not key.startswith('artId')]

    finalArts = []
    translationDict = {
        'verbCode' : 'code',
        'effectCode' : 'sub',
        'targetId' : 'target',
        'effectValue' : 'effect',
        'probability' : 'rate',
        'enableTurn' : 'turn',
        'parameter' : 'param',
    }
    for art in arts:
        finalArt = {}
        for key in art.keys():
            if key in translationDict:
                finalArt[translationDict[key]] = art[key]
            else:
                finalArt[key] = art[key]
        finalArts.append(finalArt)
    return finalArts

def cardMagiaToMagia(userCard):
    cardMagia = userCard['card']['cardMagia']
    return {
        "magiaId": int(str(cardMagia['id'])+str(userCard['magiaLevel'])),
        "name": cardMagia['name'],
        "icon": cardMagia['groupId'],
        "level": userCard['magiaLevel'],
        "description": cardMagia['shortDescription'],
        "artList": [cardMagia[key] for key in cardMagia if key.startswith('artId')]
    }

def cardDoppelToDoppel(userCard):
    if 'doppelCardMagia' in userCard['card'] \
        and dt.getUserObject('userDoppelList', userCard['card']['doppelCharaNo']) is not None:
        cardDoppel = userCard['card']['doppelCardMagia']
    else:
        return None
    return {
            "artList": [cardDoppel[key] for key in cardDoppel if key.startswith('artId')],
            "description": cardDoppel['shortDescription'],
            "doppelId": userCard['card']['doppel']['id'],
            "icon": cardDoppel['groupId'],
            "level": 5,
            "name": cardDoppel['name'],
            "voice": 40 # what is this?
    }

def cardSkillToConnect(userCard):
    cardSkill = userCard['card']['cardSkill']
    return {
        "connectId": cardSkill['id'],
        "name": cardSkill['name'],
        "icon": cardSkill['groupId'],
        "description": cardSkill['shortDescription'],
        "artList": [cardSkill[key] for key in cardSkill if key.startswith('artId')]
    }

def piecesToMemoriae(userPieces):
    memoria = []
    for userPiece in userPieces:
        piece = userPiece['piece']
        skill = piece['pieceSkill']
        memoria.append({
            "memoriaId": int(str(piece['pieceId'])+'00'), # TODO: what does this 00 actually mean?
            "name": piece['pieceName'],
            "icon": skill['groupId'],
            "level": userPiece['level'],
            "cost": skill['intervalTurn'] if 'intervalTurn' in skill else 0,
            "description": skill['shortDescription'],
            "voice": 0, # TODO: how is this actually set?
            "artList": [skill[key] for key in skill.keys() if key.startswith('artId')],
            "type": piece['pieceType'],
            "displayType": "MEMORIA"
        })
    return memoria

def applyCustomizeBonuses(userCard, player):
    cardCustomize = userCard['card']['cardCustomize']
    bonuses = {}
    for i in range(1,7):
        stri = str(i)

        if 'bonusCode'+stri not in cardCustomize:
            continue
        if not userCard['customized'+stri]:
            continue

        bonusCode = cardCustomize['bonusCode'+stri]
        bonusNum = cardCustomize['bonusNum'+stri]
        bonuses[bonusCode] = bonusNum
    
    if 'ATTACK' in bonuses:
        player['attack'] *= 1+bonuses['ATTACK']/1000
    if 'DEFENSE' in bonuses:
        player['defence'] *= 1+bonuses['DEFENSE']/1000
    if 'HP' in bonuses:
        player['hp'] *= 1+bonuses['HP']/1000
    if 'ACCEL' in bonuses:
        player['mpup'] = bonuses['ACCEL']/10
    if 'BLAST' in bonuses:
        player['blast'] = bonuses['BLAST']/10
    if 'CHARGE' in bonuses:
        player['charge'] = bonuses['CHARGE']/10

def cardToPlayer(userCard, userChara, battleInfo):
    charaMessages = [message for message in userChara['chara']['charaMessageList']if 40<=message['messageId']<50]
    charaMessage = np.random.choice(charaMessages)

    player = {
        "diskId": 0,
        "helper": battleInfo['helper'],
        "friend": battleInfo['friend'],
        "endMessageId": charaMessage['messageId'],
        "endMessage": charaMessage['message'],
        "memoriaMax": 1,
        "cardId": userCard['cardId'],
        "charId": userChara['charaId'],
        "miniCharId": userCard['card']['miniCharaNo'],
        "miniMagiaId": userCard['card']['magiaCharaNo'],
        "pos": battleInfo['pos'],
        "name": userChara['chara']['name'],
        "level": userCard['level'],
        "align": userCard['card']['attributeId'],
        "rank": int(userCard['card']['rank'][-1]),
        "hpStart": userCard['hp'],
        "hp": userCard['hp'],
        "mpStart": 0,
        "maxMp": 1000,
        "attack": userCard['attack'],
        "defence": userCard['defense'],
        "speed": 0,
        "discType1": userCard['card']['commandType1'],
        "discType2": userCard['card']['commandType2'],
        "discType3": userCard['card']['commandType3'],
        "discType4": userCard['card']['commandType4'],
        "discType5": userCard['card']['commandType5'],
        "connectId": userCard['card']['cardSkill']['id'],
        "magiaId": int(str(userCard['card']['cardMagia']['id'])+str(userCard['magiaLevel'])),
        "blast": 0,
        "charge": 0,
        "mpup": 0,
        "rateGainMpAtk": userCard['card']['rateGainMpAtk'],
        "rateGainMpDef": userCard['card']['rateGainMpDef'],
        "leader": battleInfo['leader'],
        "ai": 3 if userChara['charaId']==1001 else 1, # TODO: figure out how this actually works
        "memoriaList": [memoria['memoriaId'] for memoria in battleInfo['memoriaList']]
    }

    if userCard['magiaLevel'] == 5:
        player['maxMp'] = 2000
        if 'doppel' in userCard['card']:
            # crossing fingers that these are the same...
            player['doppelId'] = userCard['card']['doppelCharaNo']
            player['miniDoppelId'] = userCard['card']['doppelCharaNo']
    
    applyCustomizeBonuses(userCard, player)

    return player

def battleTranslate(battleData, userCard = None, userPieces = []):
    battleData['artList'] += extractArts(userCard, userPieces)
    if userCard is not None:
        battleData['magiaList'].append(cardMagiaToMagia(userCard))
        battleData['connectList'].append(cardSkillToConnect(userCard))
        currDoppel = cardDoppelToDoppel(userCard)
        if currDoppel is not None:
            battleData['doppelList'].append(currDoppel)
    if len(userPieces) > 0:
        currMemoriae = piecesToMemoriae(userPieces)
        battleData['memoria'] += currMemoriae
        return currMemoriae
    return []

def separateEnemyInfo(enemy):
    response = {key: [] for key in ['artList', 'magiaList', 'doppelList', 'memoria']}
    newEnemy = copy.deepcopy(enemy)

    if 'magia' in newEnemy:
        response['artList'] += newEnemy['magia']['artList']
        newEnemy['magia']['artList'] = [art['artId'] for art in newEnemy['magia']['artList']]
        response['magiaList'].append(newEnemy['magia'])
        del newEnemy['magia']

    if 'doppel' in newEnemy:
        response['artList'] += newEnemy['doppel']['artList']
        newEnemy['doppel']['artList'] = [art['artId'] for art in newEnemy['doppel']['artList']]
        response['doppelList'].append(newEnemy['doppel'])
        del newEnemy['doppel']

    for i in range(len(newEnemy['memoriaList'])):
        response['artList'] += newEnemy['memoriaList'][i]['artList']
        newEnemy['memoriaList'][i]['artList'] = [art['artId'] for art in newEnemy['memoriaList'][i]['artList']]
    response['memoria'] += newEnemy['memoriaList']
    newEnemy['memoriaList'] = [mem['memoriaId'] for mem in newEnemy['memoriaList']]

    return newEnemy, response

dropItemPattern = re.compile(r'dropItem\d')
# TODO: is there a way to ensure a certain number of event drops?
# TODO: memoria that increase drops
def dropItems(battleId, waveList):
    # get list of enemyLists in waveList, then flatten
    flatEnemies = [enemy for enemyList in [wave['enemyList'] for wave in waveList] for enemy in enemyList]
    uniqueEnemyIds = {enemy['charId'] for enemy in flatEnemies}
    enemyCounts = {enemyId: len([enemy for enemy in flatEnemies if enemy['charId']==enemyId]) for enemyId in uniqueEnemyIds}
    enemyIdxs = {}
    for i, wave in enumerate(waveList):
        enemyList = wave['enemyList']
        for j, enemy in enumerate(enemyList):
            enemyId = enemy['charId']
            enemyIdxs[enemyId] = enemyIdxs.get(enemyId, []) + [(i, j)]
    
    battle = dt.masterBattles[battleId]
    possibleDropCodes = {}
    for key in battle.keys():
        if dropItemPattern.fullmatch(key):
            possibleDropCodes[battle[key]['dropItemId']] = [v for k, v in battle[key].items() if k.startswith('rewardCode')]

    # TODO: change rates to what they really are...
    dropRates = {drop: 2 for drop in possibleDropCodes}
    promisedDrops = {'questBattleId': battleId}

    # handle items that can only be dropped by particular enemies
    # get list of who can drop
    dropsToEnemies = {int(k): v for k, v in dt.readJson('data/enemyDrops.json').items()}
    extractGiftCode = lambda x: int(x.split('_')[1])
    # this can't handle dropItemIds that have both gifts and items as dropCodes, but maybe we don't need to
    possibleDropToEnemyIds = {}
    for dropItemId, dropCodes in possibleDropCodes.items():
        enemies = []
        for dropCode in dropCodes:
            if not dropCode.startswith('GIFT') or not extractGiftCode(dropCode) in dropsToEnemies:
                enemies = []
                break
            for enemyId in dropsToEnemies[extractGiftCode(dropCode)]:
                if enemyId in uniqueEnemyIds:
                    enemies.append(enemyId)
        if not len(enemies) == 0:
            possibleDropToEnemyIds[dropItemId] = enemies

    boxTypes = [None, 'BRONZE', 'SILVER', 'GOLD']
    availableIdxs = [enemyIdx for _, enemyIdxList in enemyIdxs.items() for enemyIdx in enemyIdxList]
    for dropId, enemyIds in possibleDropToEnemyIds.items():
        numDroppers = sum([enemyCounts[enemyId] for enemyId in enemyIds])
        if numDroppers == 0: continue 

        conditionalRate = min(1, dropRates[dropId]/numDroppers)
        for enemyId in enemyIds:
            if len(enemyIdxs[enemyId])==0:
                continue
            
            numDrops = np.random.binomial(enemyCounts[enemyId], conditionalRate)
            idxs = np.random.choice(len(enemyIdxs[enemyId]), numDrops, replace=False)
            removeIdxs = []
            for enemyIdx in idxs:
                giftId = extractGiftCode(np.random.choice(possibleDropCodes[dropId], 1)[0])
                rarity = dt.masterGifts[giftId]['rank']

                waveNo, idx = enemyIdxs[enemyId][enemyIdx]
                # this is going to change waveList, actually, because this list was created using references
                waveList[waveNo]['enemyList'][idx]['dropItemType'] = 'BOX_' + boxTypes[rarity]
                promisedDrops['GIFT_' + str(giftId) + '_1'] = promisedDrops.get('GIFT_' + str(giftId) + '_1', 0) + 1
                removeIdxs.append((waveNo, idx))
                availableIdxs.remove((waveNo, idx))
            for removeIdx in removeIdxs: enemyIdxs[enemyId].remove(removeIdx)

    # handle drops that can be dropped by anyone
    for dropItemId, codes in possibleDropCodes.items():
        numEnemies = len(availableIdxs)
        if numEnemies == 0: continue

        conditionalRate = min(1, dropRates[dropItemId]/numEnemies)
        numDrops = np.random.binomial(numEnemies, conditionalRate)
        idxs = np.random.choice(len(availableIdxs), numDrops, replace=False)
        removeIdxs = []
        for availableIdx in idxs:
            code = np.random.choice(codes, 1)[0]
            if code.startswith('RICHE'):
                rarityBox = 'BOX_BRONZE'
            elif code.startswith('ITEM'):
                itemId = '_'.join(code.split('_')[1:-1])
                rarityBox = 'BOX_'+dt.masterItems[itemId]['treasureChestColor']
            elif code.startswith('GIFT'):
                giftId = extractGiftCode(code)
                rarityBox = 'BOX_'+boxTypes[dt.masterGifts[giftId]['rank']]
                if extractGiftCode(code) in possibleDropToEnemyIds:
                    continue

            waveNo, enemyIdx = availableIdxs[availableIdx]
            waveList[waveNo]['enemyList'][enemyIdx]['dropItemType'] = rarityBox
            promisedDrops[code] = promisedDrops.get(code, 0) + 1
            removeIdxs.append((waveNo, enemyIdx))
        for removeIdx in removeIdxs: availableIdxs.remove(removeIdx)

    # first clear reward
    userQuestBattle = dt.getUserObject('userQuestBattleList', battleId)
    if 'cleared' not in userQuestBattle or not userQuestBattle['cleared'] and 'firstClearRewardCodes' in battle:
        code = battle['firstClearRewardCodes']
        if code.startswith('RICHE'):
            rarityBox = 'BOX_BRONZE'
        elif code.startswith('ITEM'):
            itemId = '_'.join(code.split('_')[1:-1])
            rarityBox = 'BOX_'+dt.masterItems[itemId]['treasureChestColor']
        elif code.startswith('GIFT'):
            giftId = extractGiftCode(code)
            rarityBox = 'BOX_'+boxTypes[dt.masterGifts[giftId]['rank']]

        if len(availableIdxs) != 0:
            waveNo, enemyIdx = availableIdxs[np.random.choice(len(availableIdxs), 1)[0]]
            waveList[waveNo]['enemyList'][enemyIdx]['dropItemType'] = rarityBox
        promisedDrops[code] = promisedDrops.get(code, 0) + 1
    
    dt.saveJson('data/user/promisedDrops.json', promisedDrops)
    return waveList

def getQuestData(battleId, args):
    waveList = copy.deepcopy(dt.masterWaves[battleId])
    allQuestEnemies = dt.readJson('data/uniqueQuestEnemies.json')
    for i, wave in enumerate(waveList):
        if not wave['boss']:
            enemyPool = []
            for enemyInfo in wave['enemyList']:
                charId, idx = enemyInfo.split('-')
                enemy, response = separateEnemyInfo(allQuestEnemies[charId][int(idx)])
                enemyPool.append(enemy)
                for key in response.keys():
                    args[key] = args.get(key, []) + response[key]

            # randomize
            numEnemies = max(3, np.random.binomial(9, 0.5))
            enemyPositions = np.random.choice(list(range(1, 10)), numEnemies, replace=False)
            finalEnemies = []

            for pos in enemyPositions:
                finalEnemy = np.random.choice(enemyPool)
                finalEnemy['pos'] = int(pos) # oBjEcT oF tYpE iNt32 iS NoT JsOn sErIaLiZaBLe
                finalEnemy['enemyKey'] = uuid1()
                finalEnemies.append(copy.deepcopy(finalEnemy)) # not sure why memory gets overwritten but...

            waveList[i]['enemyList'] = finalEnemies
        else:
            for j, enemyInfo in enumerate(wave['enemyList']):
                charId, idx = enemyInfo['id'].split('-')
                enemy, response = separateEnemyInfo(allQuestEnemies[charId][int(idx)])
                for key in response.keys():
                    args[key] = args.get(key, []) + response[key]
                enemy['pos'] = enemyInfo['pos']
                enemy['enemyKey'] = uuid1()
                if 'cutinId' in enemyInfo:
                    enemy['cutinId'] = enemyInfo['cutinId']
                waveList[i]['enemyList'][j] = copy.deepcopy(enemy)
    waveList = dropItems(battleId, waveList)
    return waveList

def dedupeDictList(dictlist, idx):
    idxs = set({})
    finalList = []
    for item in dictlist:
        if not item[idx] in idxs:
            finalList.append(item)
            idxs.add(item[idx])
    return finalList

def addUserToBattle(battleData, position, deck):
    currCardIdx = 0
    for i in range(4):
        if 'questPositionId'+str(i+1) in deck:
            if deck['questPositionId'+str(i+1)]==position:
                currCardIdx = i+1
    
    userCardId = deck['userCardId'+str(currCardIdx)]
    userCard = dt.getUserObject('userCardList', userCardId)
    if userCard is None:
        flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have: ' + userCardId + '","resultCode": "error","title": "Error"}')
    
    pieceIds = [deck[key] for key in deck.keys() if key.startswith('userPieceId0'+str(currCardIdx))]
    pieces = [dt.getUserObject('userPieceList', pieceId) for pieceId in pieceIds]
    currMemoriae = battleTranslate(battleData, userCard, pieces)

    userCharaId = userCard['card']['charaNo']
    userChara = dt.getUserObject('userCharaList', userCharaId)
    if userChara is None:
        flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have: ' + userCharaId + '","resultCode": "error","title": "Error"}')

    battleInfo = {
        'helper': False,
        'friend': False,
        'pos': position,
        'leader': deck['questEpisodeUserCardId'] == userCharaId,
        'memoriaList': currMemoriae
    }
    battleData['playerList'].append(cardToPlayer(userCard, userChara, battleInfo))

def spendAP(battle):
    apType, apDisplay = 'ACP', 'AP'
    if battle['battleType'] == 'ARENA':
        apType, apDisplay = 'BTP', 'BP'
        apAmount = 1
    elif battle['questBattle']['consumeType'] == 'NORMAL':
        apAmount = battle['scenario']['cost']
    elif battle['questBattle']['consumeType'] == 'FREE_AT_NOT_CLEAR':
        userQuestBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
        apAmount = battle['scenario']['cost'] if ('cleared' in userQuestBattle and userQuestBattle['cleared']) else 0
    else:
	apAmount = 1

    apStatus = homu.getStatus(apType)
    apStatus['point'] -= apAmount
    if apStatus['point'] < 0:
        flask.abort(400, '{"errorTxt": "Not enough ' + apDisplay + '.","resultCode": "error","title": "Error"}')
    dt.setUserObject('userStatusList', apType, apStatus)
    return apStatus

def get():
    body = flask.request.json
    battle = dt.readJson('data/user/userQuestBattleResult.json')
    isMirrors = battle['battleType']=="ARENA"

    if isMirrors:
        arenaBattle = dt.readJson('data/user/userArenaBattleResult.json')
        if not arenaBattle['userQuestBattleResultId'] == battle['id']:
            flask.abort(500, description='{"errorTxt": "Something weird happened with order of battles","resultCode": "error","title": "Error"}')

    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # grab team info
    deck = dt.getUserObject('userDeckList', battle['deckType'])
    battleData = {
        'playerList': [],
        'artList': [],
        'magiaList': [],
        'connectList': [],
        'doppelList': [],
        'memoria': []
    }
    for key in battle.keys():
        if key.startswith('userCardId'):
            addUserToBattle(battleData, int(key[-1]), deck)

    # do the same, but now for the helper
    # TODO: use actual support
    if not isMirrors:
        helper = dt.readJson('data/npc.json')
        helperCard = helper['userCardList'][0]
        helperChara = helper['userCharaList'][0]
        helperPieces = helper['userPieceList']

        helperMemoriae = battleTranslate(battleData, helperCard, helperPieces)

        battleInfo = {
            'helper': True,
            'friend': True, # TODO: actually change this
            'pos': deck['questPositionHelper'],
            'leader': False,
            'memoriaList': helperMemoriae
        }
        battleData['playerList'].append(cardToPlayer(helperCard, helperChara, battleInfo))

        # add support points
        supportPoints = dt.getUserObject('userItemList', 'YELL')
        supportPoints['quantity'] += 60
        dt.setUserObject('userItemList', 'YELL', supportPoints)

    # spend AP/BP
    apStatus = spendAP(battle)

    # change quest status
    battle['questBattleStatus'] = 'LOTTERY'
    dt.saveJson('data/user/userQuestBattleResult.json', battle)

    # TODO: use follower
    userFollowList = []

    # compile web data
    webData = {
        "gameUser": dt.readJson('data/user/gameUser.json'),
        "userStatusList": [apStatus],
        "userQuestBattleResultList": [battle],
        "resultCode": "success",
        "userFollowList": userFollowList,
    }
    if not isMirrors:
        webData["userItemList"] = [supportPoints]

    # add opponent stuff
    if not isMirrors:
        if battle['questBattleId'] in dt.masterWaves:
            waves = getQuestData(battle['questBattleId'], battleData)
        else:
            waves = [dt.readJson('data/hardCodedWave.json')]
    else:
        opponent = dt.readJson('data/arenaEnemies/'+arenaBattle['opponentUserId']+'.json')
        waves = [{
			"field": 21181,
			"boss": False,
			"sheetType": 9,
			"enemyList": opponent['enemyList']
        }]
        # this is a mess lol, only the arts from the memoria are in artList
        battleData['memoria'] += opponent['memoriaList']
        battleData['artList'] += opponent['artList']

        # the rest have to be extracted from the cards
        for enemyCard in opponent['opponentUserArenaBattleInfo']['userCardList']:
            battleTranslate(battleData, enemyCard, [])

    response = {
        'battleType': 'QUEST' if not isMirrors else 'ARENA', # TODO: change for tutorials, challenge quests
        'scenario': mirrorScenario if isMirrors else battle['scenario'],
        'waveList': waves,
        'playerList': battleData['playerList'],
        'doppelList': dedupeDictList(battleData['doppelList'], 'doppelId'),
        'artList': dedupeDictList(battleData['artList'], 'artId'),
        'memoriaList': dedupeDictList(battleData['memoria'], 'memoriaId'),
        'connectList': dedupeDictList(battleData['connectList'], 'connectId'),
        'magiaList': dedupeDictList(battleData['magiaList'], 'magiaId'),
        'continuable': True,
        'isHalfSkill': False,
        'webData': webData
    }
    return flask.jsonify(response)
