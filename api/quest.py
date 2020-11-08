import flask
import json
from datetime import datetime
from uuid import uuid1
import numpy as np
from api import userCard

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
        'numberOfConsecutiveWins':1,
        'userQuestBattleResultId':request['userQuestBattleResultId'],
        'userId':'',
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


def send():
    body = flask.request.json
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')

    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
        userId = user['id']
    with open('data/user/userQuestBattleResult.json', encoding='utf-8') as f:
        battle = json.load(f)

    if(battle['battleType']=="ARENA"):
        return sendArena(body,{'userQuestBattleResultList':[battle],'gameUser':user})
        
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)
    with open('data/user/userCardList.json', encoding='utf-8') as f:
        userCardList = json.load(f)


    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # add exp to user and level up, maybe
    userExp = battle['questBattle']['exp']
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    gameUser['exp'] += userExp
    newStatus = []
    if gameUser['exp'] >= gameUser['totalExpForNextLevel']:
        gameUser['level'] += 1
        gameUser['totalExpForCurrentLevel'] = gameUser['totalExpForNextLevel']
        gameUser['totalExpForNextLevel'] += 10 # TODO: how does this actually work lol
        with open('data/user/userStatusList.json', encoding='utf-8') as f:
            userStatusList = json.load(f)
        
        maxAPIdx = 0
        currAPIdx = 0
        for i, status in enumerate(userStatusList):
            if status['statusId'] == 'MAX_ACP':
                maxAPIdx = i
            if status['statusId'] == 'ACP':
                currAPIdx = i
        userStatusList[maxAPIdx]['point'] += 10
        userStatusList[currAPIdx]['point'] += userStatusList[maxAPIdx]['point']
        newStatus.append(userStatusList[maxAPIdx])
        newStatus.append(userStatusList[currAPIdx])

        with open('data/user/userStatusList.json', 'w+', encoding='utf-8') as f:
            json.dump(userStatusList, f, ensure_ascii=False)

    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        json.dump(gameUser, f, ensure_ascii=False)

    # TODO: add to stories
    resultUserQuestAdventureList = []

    # change userQuestBattleResult status
    battle['questBattleStatus'] = 'SUCCESSFUL'

    # add to userQuestBattleList
    with open('data/user/userQuestBattleList.json', encoding='utf-8') as f:
        userQuestBattleList = json.load(f)

    resultUserQuestBattle = {}
    # TODO: get real mission clear values
    for userQuestBattle in userQuestBattleList:
        if userQuestBattle['questBattleId'] == battle['questBattleId']:
            resultUserQuestBattle = userQuestBattle
    if resultUserQuestBattle == {}:
        resultUserQuestBattle = {
            "userId": userId,
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
        userQuestBattleList.append(resultUserQuestBattle)
    resultUserQuestBattleList = [resultUserQuestBattle]
    with open('data/user/userQuestBattleList.json', 'w+', encoding='utf-8') as f:
        json.dump(userQuestBattleList, f, ensure_ascii=False)

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

    for i, currUserCard in enumerate(userCardList):
        if currUserCard['id'] in cardIds:
            charaNos.append(currUserCard['card']['charaNo'])
            if currUserCard['id'] == leaderCardId:
                leaderCharaId = currUserCard['card']['charaNo']

            exp = battle['questBattle']['cardExp']
            newLevel, extraExp = userCard.getFinalLevel(currUserCard, exp)
            maxLevel = userCard.maxLevels[currUserCard['card']['rank']]
            if newLevel >= maxLevel:
                userCardList[i]['level'] = maxLevel
                userCardList[i]['experience'] = 0
            else:
                userCardList[i]['level'] = newLevel
                userCardList[i]['experience'] = extraExp

            resultUserCardList.append(userCardList[i])

    with open('data/user/userCardList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCardList, f, ensure_ascii=False)

    # add episode points to charas
    for i in range(9):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in body:
            cardIds.append(body[numberedId])

    resultUserCharaList = []
    for i, userChara in enumerate(userCharaList):
        if userChara['charaId'] in charaNos:
            eps = battle['questBattle']['baseBondsPt']
            if userChara['charaId'] == leaderCharaId:
                eps *= 1.5
            userCharaList[i]['bondsTotalPt'] = min(userCharaList[i]['bondsTotalPt']+eps, 64000)
            resultUserCharaList.append(userCharaList[i])

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCharaList, f, ensure_ascii=False)

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
    for piece in userPieceList:
        skills = [piece['piece'][key] for key in piece['piece'].keys() if key.startswith('pieceSkill')]
        for skill in skills:
            arts += [skill[key] for key in skill.keys() if key.startswith('art')
                     and not key.startswith('artId')]
    return arts

def cardMagiaToMagia(userCard):
    cardMagia = userCard['card']['cardMagia']
    return {
        "magiaId": cardMagia['id'],
        "name": cardMagia['name'],
        "icon": cardMagia['groupId'],
        "level": userCard['magiaLevel'],
        "description": cardMagia['shortDescription'],
        "artList": [cardMagia[key] for key in cardMagia if key.startswith('artId')]
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
        "magiaId": str(userCard['card']['cardMagia']['id'])+str(userCard['magiaLevel']),
        "blast": 0,
        "charge": 0,
        "mpup": 0,
        "rateGainMpAtk": userCard['card']['rateGainMpAtk'],
        "rateGainMpDef": userCard['card']['rateGainMpDef'],
        "leader": battleInfo['leader'],
        "ai": 3 if userChara['charaId']==1001 else 1, # TODO: figure out how this actually works
        "memoriaList": battleInfo['memoriaList']
    }

def getArena(response):
    
    with open('data/arenaNativeGetDummy.json') as f:
        response.update(json.load(f))
    print(response)
    return flask.jsonify(response)
 
def get():
    body = flask.request.json

    isMirrors = False # TODO: make this actually represent if it's a mirrors battle

    with open('data/user/userQuestBattleResult.json', encoding='utf-8') as f:
        battle = json.load(f)
    if(battle['battleType']=="ARENA"):
       return getArena({})


    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    with open('data/user/userDeckList.json', encoding='utf-8') as f:
        userDeckList = json.load(f)
    with open('data/user/userCardList.json', encoding='utf-8') as f:
        userCardList = json.load(f)
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)
    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        userPieceList = json.load(f)

    # grab team info
    deck = {}
    for userDeck in userDeckList:
        if userDeck['deckType'] == battle['deckType']:
            deck = userDeck

    playerList = []
    artList = []
    magiaList = []
    connectList = []
    doppelList = []
    memoria = []
    for key in battle.keys():
        if key.startswith('userCardId'):
            currCardIdx = 0
            for i in range(4):
                if 'questPositionId'+str(i+1) in deck:
                    if deck['questPositionId'+str(i+1)]==int(key[-1]):
                        currCardIdx = i+1
            
            userCardId = deck['userCardId'+str(currCardIdx)]
            userCard = {}
            for card in userCardList:
                if card['id'] == userCardId and card['enabled']:
                    userCard = card
            if userCard == {}:
                flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have...","resultCode": "error","title": "Error"}')
            magiaList.append(cardMagiaToMagia(userCard))
            connectList.append(cardSkillToConnect(userCard))

            userCharaId = userCard['card']['charaNo']
            userChara = {}
            for chara in userCharaList:
                if chara['charaId'] == userCharaId:
                    userChara = chara
            if userChara == {}:
                flask.abort(400, description='{"errorTxt": "Tried to start quest with a meguca you don\'t have...","resultCode": "error","title": "Error"}')

            pieceIds = [deck[key] for key in deck.keys() if key.startswith('userPieceId0'+str(currCardIdx))]
            pieces = [userPiece for userPiece in userPieceList if userPiece['id'] in pieceIds]
            artList += extractArts(userCard, pieces)
            currMemoria = piecesToMemoriae(pieces)
            memoria += currMemoria

            battleInfo = {
                'helper': False,
                'friend': False,
                'pos': int(key[-1]),
                'leader': deck['questEpisodeUserCardId'] == userCharaId,
                'memoriaList': currMemoria
            }
            playerList.append(cardToPlayer(userCard, userChara, battleInfo))

    # do the same, but now for the helper
    # TODO: use actual support
    with open('data/npc.json', encoding='utf-8') as f:
        helper = json.load(f)
    helperCard = helper['userCardList'][0]
    helperChara = helper['userCharaList'][0]
    helperPieces = helper['userPieceList']

    magiaList.append(cardMagiaToMagia(helperCard))
    connectList.append(cardSkillToConnect(helperCard))
    artList += extractArts(helperCard, helperPieces)
    helperMemoria = piecesToMemoriae(helperPieces)
    memoria += helperMemoria

    battleInfo = {
        'helper': True,
        'friend': True, # TODO: actually change this
        'pos': deck['questPositionHelper'],
        'leader': False,
        'memoriaList': helperMemoria
    }
    playerList.append(cardToPlayer(helperCard, helperChara, battleInfo))

    # add support points
    with open('data/user/userItemList.json', encoding='utf-8') as f:
        userItems = json.load(f)
    supportPoints = {}
    for i, item in enumerate(userItems):
        if item['itemId'] == 'YELL':
            userItems[i]['quantity'] += 60 # TODO: change this based on the helper
            supportPoints = userItems[i]
    with open('data/user/userItemList.json', 'w+', encoding='utf-8') as f:
        json.dump(userItems, f)

    # spend AP
    with open('data/user/userStatusList.json', encoding='utf-8') as f:
        userStatuses = json.load(f)
    apStatus = {}
    for i, status in enumerate(userStatuses):
        if status['statusId'] == 'ACP':
            userStatuses[i]['point'] -= 1 # TODO: figure out how to find this...
            apStatus = userStatuses[i]
    with open('data/user/userStatusList.json', 'w+', encoding='utf-8') as f:
        json.dump(userStatuses, f)

    # change quest status
    battle['questBattleStatus'] = 'LOTTERY'
    with open('data/user/userQuestBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(battle, f)

    # TODO: use follower
    userFollowList = []

    # compile web data
    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    webData = {
        "gameUser": gameUser,
        "userStatusList": [apStatus],
        "userQuestBattleResultList": [battle],
        "resultCode": "success",
        "userFollowList": [userFollowList],
        "userItemList": [supportPoints]
    }

    with open('data/hardCodedWave.json', encoding='utf-8') as f:
        wave = json.load(f)

    response = {
        'scenario': battle['questBattle'],
        'waveList': [wave],
        'battleType': 'QUEST', # TODO: change for tutorials, mirrors
        'playerList': playerList,
        'doppelList': doppelList,
        'artList': artList,
        'memoriaList': memoria,
        'connectList': connectList,
        'magiaList': magiaList,
        'continuable': True,
        'isHalfSkill': isMirrors,
        'webData': webData
    }
    return flask.jsonify(response)

def start():    
    body = flask.request.json
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')

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
                    "userId": userInfo['userId'],
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
            "userId": userInfo['userId']
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