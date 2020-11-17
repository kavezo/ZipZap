import flask
import json
from datetime import datetime
from uuid import uuid1
import numpy as np

from api import userCard
from util import dataUtil

def sendArena(request,response):
    """
        The response has 7 values:
        gameUser (should be in response),
        resultCode="success"
        userArenaBattle,
        userArenaBattleResultList,
        userDailyChallengeList,
        userItemList,
        userQuestBattleResultList (should be in response),

    """
    with open('data/user/userArenaBattle.json', encoding='utf-8') as f:
        userArenaBattle=json.load(f)

    #only mirror coins please
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        allItems = json.load(f)

    coins=next(filter(lambda item: item['itemId']=='ARENA_COIN',allItems))

    if (request['result']=='SUCCESSFUL'):
        arenaBattleStatus='WIN'
        coins['quantity']+=3
    else:
        arenaBattleStatus='LOSE'
        coins['quantity']+=1

    #updating coins
    with open('data/user/userItemList.json', 'w+', encoding='utf-8') as f:
        json.dump(allItems, f, ensure_ascii=False)

    userItemList=[coins]

    userDailyChallengeList=[] #TODO
    resultCode="success"
    userArenaBattleResultList=[{
        'arenaBattleStatus': arenaBattleStatus,
        'arenaBattleType': 'FREE_RANK', #change for ranked
        'numberOfConsecutiveWins': 1,
        'userQuestBattleResultId':request['userQuestBattleResultId'],
        'userId': dataUtil.userId,
        'opponentUserId':'',
        'point':0
    }]
    response.update({
        'userArenaBattle' : userArenaBattle,
        'userItemList': userItemList,
        'userArenaBattleResultList': userArenaBattleResultList,
        'resultCode': resultCode,
        'userDailyChallengeList': userDailyChallengeList,
    })

    return flask.jsonify(response)

def giveUserExp(battle):
    userExp = 0 # battle['questBattle']['exp']
    gameUser = dataUtil.setGameUserValue('exp', dataUtil.getGameUserValue('exp')+userExp)
    newStatus = []
    if gameUser['exp'] >= gameUser['totalExpForNextLevel']:
        dataUtil.setGameUserValue('exp', gameUser['exp'] - gameUser['totalExpForNextLevel'])
        dataUtil.setGameUserValue('level', gameUser['level'] + 1)
        dataUtil.setGameUserValue('totalExpForCurrentLevel', gameUser['totalExpForNextLevel'])
        # TODO: how does this actually work lol
        gameUser = dataUtil.setGameUserValue('totalExpForNextLevel', gameUser['totalExpForNextLevel'] + 10)

        maxAP = dataUtil.getUserObject('userStatusList', 'MAX_ACP')
        currAP = dataUtil.getUserObject('userStatusList', 'ACP')
        maxAP['point'] += 10
        currAP['point'] += maxAP['point']

        newStatus.append(maxAP)
        newStatus.append(currAP)

        dataUtil.setUserObject('userStatusList', 'MAX_ACP', maxAP)
        dataUtil.setUserObject('userStatusList', 'ACP', currAP)
    return gameUser, newStatus

def giveMegucaExp(body, battle):
    # add exp to cards
    charaNos = []
    leaderCardId = 0
    leaderCharaId = 0
    cardIds = []
    resultUserCardList = []
    for i in range(9):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in battle:
            cardIds.append(battle[numberedId])
            if battle[numberedId] == battle['episodeUserCardId']:
                leaderCardId = battle[numberedId]

    for cardId in cardIds:
        currUserCard = dataUtil.getUserObject('userCardList', cardId)
        charaNos.append(currUserCard['card']['charaNo'])
        if currUserCard['id'] == leaderCardId:
            leaderCharaId = currUserCard['card']['charaNo']

        exp = battle['questBattle']['cardExp']
        newLevel, extraExp = userCard.getFinalLevel(currUserCard, exp)
        maxLevel = userCard.maxLevels[currUserCard['card']['rank']]
        if newLevel >= maxLevel:
            currUserCard['level'] = maxLevel
            currUserCard['experience'] = 0
        else:
            currUserCard['level'] = newLevel
            currUserCard['experience'] = extraExp

        resultUserCardList.append(currUserCard)
        dataUtil.setUserObject('userCardList', cardId, currUserCard)

    # add episode points to charas
    for i in range(9):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in body:
            cardIds.append(body[numberedId])

    resultUserCharaList = []
    eps = battle['questBattle']['baseBondsPt']
    for charaNo in charaNos:
        userChara = dataUtil.getUserObject('userCharaList', charaNo)
        if charaNo == leaderCharaId:
            eps *= 1.5
        # checking if this is the meguca's MSS
        strBattleId = str(battle['questBattle']['questBattleId'])
        if strBattleId.startswith('3') and strBattleId[1:5] == str(charaNo):
            eps *= 2
        userChara['bondsTotalPt'] += eps

        resultUserCharaList.append(userChara)
        dataUtil.setUserObject('userCharaList', charaNo, userChara)
    return resultUserCardList, resultUserCharaList

def send():
    body = flask.request.json
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')

    battle = dataUtil.readJson('data/user/userQuestBattleResult.json')

    if(battle['battleType']=="ARENA"):
        return sendArena(body,{'userQuestBattleResultList':[battle],'gameUser': dataUtil.readJson('data/user/gameUser.json')})

    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # add exp to user and level up, maybe
    gameUser, newStatus = giveUserExp(battle)

    # level up/episode up megucas
    resultUserCardList, resultUserCharaList = giveMegucaExp(body, battle)

    # TODO: add to stories
    resultUserQuestAdventureList = []

    # change userQuestBattleResult status
    battle['questBattleStatus'] = 'SUCCESSFUL'
    
    # add to userQuestBattleList
    resultUserQuestBattle = dataUtil.getUserObject('userQuestBattleList', battle['questBattleId'])
    # TODO: get real mission clear values
    if resultUserQuestBattle is None:
        resultUserQuestBattle = {
            "userId": dataUtil.userId,
            "questBattleId": battle['questBattleId'],
            "questBattle": battle,
            "cleared": True,
            "missionStatus1": "NON_CLEAR",
            "missionStatus2": "NON_CLEAR",
            "missionStatus3": "NON_CLEAR",
            "rewardDone": False,
            "clearCount": 0,
            "maxDamage": 0,
            "createdAt": nowstr
        }
    resultUserQuestBattleList = [resultUserQuestBattle]
    dataUtil.setUserObject('userQuestBattleList', battle['questBattleId'], resultUserQuestBattle)

    # TODO: calculate drops and add to items
    resultUserItemList = []

    # make response
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'userQuestAdventureList': resultUserQuestAdventureList,
        'userCardList': resultUserCardList,
        'userCharaList': resultUserCharaList,
        'userItemList': resultUserItemList,
        'userQuestBattleResultList': [battle],
        'userQuestBattleList': resultUserQuestBattleList
    }
    if newStatus != []:
        response['userStatusList'] = newStatus
    return flask.jsonify(response)

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
    if 'doppelCardMagia' in userCard['card']:
        cardDoppel = userCard['card']['doppelCardMagia']
    else:
        return None
    return {
            "artList": [cardDoppel[key] for key in cardDoppel if key.startswith('artId')],
            "description": cardDoppel['shortDescription'],
            "doppelId": cardDoppel['id'],
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

def piecesToMemoriae(memoriaIds):
    memoria = []
    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        userPieceList = json.load(f)
    for userPiece in userPieceList:
        if userPiece['id'] in memoriaIds:
            memoria.append({
                "memoriaId": str(userPiece['piece']['pieceId'])+'00', # TODO: replace 00 with something else?
                "name": userPiece['piece']['name'],
                "icon": userPiece['piece']['pieceSkill']['groupId'],
                "level": userPiece['level'],
                "cost": 0,
                "description": userPiece['piece']['description'],
                "voice": 0,
                "artList": extractArts(None, [userPiece['piece']]),
                "type": userPiece['piece']['pieceType'],
                "displayType": "MEMORIA"
            })
    return memoria

def cardToPlayer(userCard, userChara, battleInfo):
    charaMessages = [message for message in userChara['chara']['charaMessageList']if 40<=message['messageId']<50]
    charaMessage = np.random.choice(charaMessages)
    return {
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
        "maxMp": 1000, # TODO: allow doppels
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
        "memoriaList": battleInfo['memoriaList']
    }

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

def separateEnemyInfo(enemy):
    response = {key: [] for key in ['artList', 'magiaList', 'doppelList', 'memoria']}

    if 'magia' in enemy:
        response['artList'] += enemy['magia']['artList']
        enemy['magia']['artList'] = [art['artId'] for art in enemy['magia']['artList']]
        response['magiaList'].append(enemy['magia'])
        del enemy['magia']

    if 'doppel' in enemy:
        response['artList'] += enemy['doppel']['artList']
        enemy['doppel']['artList'] = [art['artId'] for art in enemy['doppel']['artList']]
        response['doppelList'].append(enemy['doppel'])
        del enemy['doppel']

    for i in range(len(enemy['memoriaList'])):
        response['artList'].append(enemy['memoriaList'][i]['artList'])
        enemy['memoriaList'][i]['artList'] = [art['artId'] for art in enemy['memoriaList'][i]['artList']]
    response['memoria'] += enemy['memoriaList']
    enemy['memoriaList'] = [mem['memoriaId'] for mem in enemy['memoriaList']]

    return enemy, response

def getQuestData(battleId, args):
    waveList = dataUtil.masterWaves[battleId]
    allQuestEnemies = dataUtil.readJson('data/uniqueQuestEnemies.json')
    for i, wave in enumerate(waveList):
        if not wave['boss']:
            enemyPool = []
            for enemyInfo in wave['enemyList']:
                charId, idx = enemyInfo.split('-')
                enemy, response = separateEnemyInfo(allQuestEnemies[charId][idx])
                enemyPool.append(enemy)
                for key in response.keys():
                    args[key] = list(set(args.get(key, []) + response[key]))

            # randomize
            numEnemies = min(3, np.random.binomial(9, 0.5))
            enemyPositions = np.random.choice(list(range(1, 10)), (numEnemies,), replace=False)
            finalEnemies = []

            for pos in enemyPositions:
                finalEnemy = np.random.choice(enemyPool)
                finalEnemy['pos'] = pos
                finalEnemies.append(finalEnemy)

            waveList[i]['enemyList'] = finalEnemies
        else:
            for j, enemyInfo in enumerate(wave['enemyList']):
                charId, idx = enemyInfo['id'].split('-')
                enemy, response = separateEnemyInfo(allQuestEnemies[charId][idx])
                for key in response.keys():
                    args[key] = list(set(args.get(key, []) + response[key]))
                enemy['pos'] = enemyInfo['pos']
                waveList[i]['enemyList'][j] = enemy
    return waveList

def get():
    body = flask.request.json
    battle = dataUtil.readJson('data/user/userQuestBattleResult.json')
    isMirrors = battle['battleType']=="ARENA"

    if isMirrors:
        arenaBattle = dataUtil.readJson('data/user/userArenaBattleResult.json')
        if not arenaBattle['userQuestBattleResultId'] == battle['id']:
            flask.abort(500, description='{"errorTxt": "Something weird happened with order of battles","resultCode": "error","title": "Error"}')

    if not battle['id'] == body['userQuestBattleResultId']:
        print('battle ID mismatch')
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # grab team info
    deck = dataUtil.getUserObject('userDeckList', battle['deckType'])
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
            currCardIdx = 0
            for i in range(4):
                if 'questPositionId'+str(i+1) in deck:
                    if deck['questPositionId'+str(i+1)]==int(key[-1]):
                        currCardIdx = i+1
            
            userCardId = deck['userCardId'+str(currCardIdx)]
            userCard = dataUtil.getUserObject('userCardList', userCardId)
            if userCard is None:
                print('can\'t find card with id ' + userCardId)
                flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have...","resultCode": "error","title": "Error"}')
            
            pieceIds = [deck[key] for key in deck.keys() if key.startswith('userPieceId0'+str(currCardIdx))]
            pieces = [dataUtil.getUserObject('userPieceList', pieceId) for pieceId in pieceIds]
            currMemoriae = battleTranslate(battleData, userCard, pieces)

            userCharaId = userCard['card']['charaNo']
            userChara = dataUtil.getUserObject('userCharaList', userCharaId)
            if userChara is None:
                print('can\'t find chara with id ' + str(userCharaId))
                flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have...","resultCode": "error","title": "Error"}')

            battleInfo = {
                'helper': False,
                'friend': False,
                'pos': int(key[-1]),
                'leader': deck['questEpisodeUserCardId'] == userCharaId,
                'memoriaList': currMemoriae
            }
            battleData['playerList'].append(cardToPlayer(userCard, userChara, battleInfo))

    # do the same, but now for the helper
    # TODO: use actual support
    if not isMirrors:
        helper = dataUtil.readJson('data/npc.json')
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
    # TODO: change this based on the helper
    if not isMirrors:
        supportPoints = dataUtil.getUserObject('userItemList', 'YELL')
        supportPoints['quantity'] += 60
        dataUtil.setUserObject('userItemList', 'YELL', supportPoints)

    # spend AP/BP
    apType = 'ACP' if not isMirrors else 'BTP'
    apStatus = dataUtil.getUserObject('userStatusList', apType)
    apStatus['point'] -= 0
    if apStatus['point'] < 0:
        flask.abort(400, '{"errorTxt": "Not enough BP.","resultCode": "error","title": "Error"}')
    dataUtil.setUserObject('userStatusList', apType, apStatus)

    # change quest status
    battle['questBattleStatus'] = 'LOTTERY'
    dataUtil.saveJson('data/user/userQuestBattleResult.json', battle)

    # TODO: use follower
    userFollowList = []

    # compile web data
    webData = {
        "gameUser": dataUtil.readJson('data/user/gameUser.json'),
        "userStatusList": [apStatus],
        "userQuestBattleResultList": [battle],
        "resultCode": "success",
        "userFollowList": userFollowList,
    }
    if not isMirrors:
        webData["userItemList"] = [supportPoints]

    # add opponent stuff
    # TODO: instead of checking if it's mirrors, we need to go through all enemies at all times and check for HUMANs
    if not isMirrors:
        if str(battle['questBattleId']) in dataUtil.masterWaves:
            waves = getQuestData(str(battle['questBattleId']), battleData)
        else:
            waves = [dataUtil.readJson('data/hardCodedWave.json')]
    else:
        opponent = dataUtil.readJson('data/arenaEnemies/'+arenaBattle['opponentUserId']+'.json')
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
        
    # dedupe
    artIds = set({})
    finalArtList = []
    for art in battleData['artList']:
        if not art['artId'] in artIds:
            finalArtList.append(art)
            artIds.add(art['artId'])

    if isMirrors:
        scenario = {
            "bgm": "bgm01_battle01",
            "bgmBoss": "bgm01_battle01",
            "difficulty": 0,
            "cost": 0,
            "missionList": [],
            "sheetType": 9,
            "auto": False
        }
    else:
        scenario = battle['questBattle']

    response = {
        'battleType': 'QUEST' if not isMirrors else 'ARENA', # TODO: change for tutorials, challenge quests
        'scenario': scenario,
        'waveList': waves,
        'playerList': battleData['playerList'],
        'doppelList': battleData['doppelList'],
        'artList': finalArtList,
        'memoriaList': battleData['memoria'],
        'connectList': battleData['connectList'],
        'magiaList': battleData['magiaList'],
        'continuable': True,
        'isHalfSkill': False,
        'webData': webData
    }
    return flask.jsonify(response)

def start():    
    body = flask.request.json
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')

    with open('data/user/gameUser.json', encoding='utf-8') as f:
        userInfo = json.load(f)

    with open('data/user/userQuestBattleList.json', encoding='utf-8') as f:
        userQuestBattleList = json.load(f)

    userQuestInfo = {}
    for userQuestBattle in userQuestBattleList:
        if userQuestBattle['questBattleId'] == body['questBattleId']:
            userQuestInfo = userQuestBattle

    if userQuestInfo == {}:
        with open('data/questBattleList.json', encoding='utf-8') as f:
            allBattles = json.load(f)
        for battle in allBattles: 
            if battle['questBattleId'] == body['questBattleId']:
                userQuestInfo = {
                    "userId": dataUtil.userId,
                    "questBattleId": battle['questBattleId'],
                    "questBattle": battle,
                    "cleared": True,
                    "missionStatus1": "NON_CLEAR",
                    "missionStatus2": "NON_CLEAR",
                    "missionStatus3": "NON_CLEAR",
                    "rewardDone": False,
                    "clearCount": 0,
                    "maxDamage": 0,
                    "createdAt": nowstr
                }
        userQuestBattleList.append(userQuestInfo)
        with open('data/user/userQuestBattleList.json', 'w+', encoding='utf-8') as f:
            json.dump(userQuestBattleList, f, ensure_ascii=False)

    with open('data/user/userDeckList.json', encoding='utf-8') as f:
        userDeckList = json.load(f)
    chosenTeam = None
    for userDeck in userDeckList:
        if userDeck['deckType'] == body['deckType']:
                chosenTeam = userDeck
    if chosenTeam is None:
        flask.abort(400, '{"errorTxt": "The team doesn\'t exist...","resultCode": "error","title": "Error"}')

    with open('data/user/userFormationSheetList.json', encoding='utf-8') as f:
        formations = json.load(f)
    chosenFormation = None
    for formation in formations:
        if formation['formationSheetId'] == chosenTeam['formationSheetId']:
            chosenFormation = formation
    if chosenFormation is None:
        flask.abort(500, '{"errorTxt": "You don\'t have that formation.","resultCode": "error","title": "Error"}')

    userQuestBattleResult = {
            "battleType": "QUEST",
            "bondsPt1": 0,
            "bondsPt2": 0,
            "bondsPt3": 0,
            "bondsPt4": 0,
            "bondsPt5": 0,
            "bondsPt6": 0,
            "bondsPt7": 0,
            "bondsPt8": 0,
            "bondsPt9": 0,
            "clearedMission1": userQuestInfo['missionStatus1']=='CLEARED',
            "clearedMission2": userQuestInfo['missionStatus2']=='CLEARED',
            "clearedMission3": userQuestInfo['missionStatus3']=='CLEARED',
            "connectNum": 0,
            "continuedNum": 0,
            "createdAt": nowstr,
            "deadNum": 0,
            "deckType": body['deckType'],
            "diskAcceleNum": 0,
            "diskBlastNum": 0,
            "diskChargeNum": 0,
            "doppelNum": 0,
            "enemyNum": 0,
            "episodeUserCardId": chosenTeam['questEpisodeUserCardId'],
            "exp": 0,
            "follow": True,
            "follower": True,
            "formationSheetId": chosenTeam['formationSheetId'],
            "formationSheet": chosenFormation,
            "helpAttributeId": body['helpAttributeId'],
            "helpBondsPt": 0,
            "helpPosition": chosenTeam['questPositionHelper'],
            "id": str(uuid1()),
            "level": userInfo['level'],
            "magiaNum": 0,
            "nativeClearTime": 0,
            "questBattle": userQuestInfo['questBattle'],
            "questBattleId": body['questBattleId'],
            "questBattleStatus": "CREATED",
            "riche": 0,
            "serverClearTime": 0,
            "skillNum": 0,
            "turns": 0,
            "userId": dataUtil.userId
        }

    if 'helpUserCardId' in body:
        userQuestBattleResult["helpUserCardId"] = body['helperUserCardId'],
        userQuestBattleResult["helpUserId"] = body['helperUserId'],

    for i in range(4):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in body:
            userQuestBattleResult['userCardId'+str(body['questPositionId'+str(i+1)])] = body[numberedId]

    resultdict = {
        "resultCode": "success",
        "userQuestBattleResultList": [userQuestBattleResult]
    }

    with open('data/user/userQuestBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(userQuestBattleResult, f, ensure_ascii=False)

    return flask.jsonify(resultdict)

def handleQuest(endpoint):
    if endpoint.startswith('start'):
        return start()
    elif endpoint.startswith('native/get'):
        return get()
    elif endpoint.startswith('native/result/send'):
        return send()
    else:
        print('quest/'+endpoint)
        flask.abort(501, description="Not implemented")