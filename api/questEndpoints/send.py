import flask
import json

from api import userCard
from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util import storyUtil
from util import homuUtil as homu

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
    userArenaBattle=dt.readJson('data/user/userArenaBattle.json')

    #only mirror coins please
    coins = dt.getUserObject('userItemList', 'ARENA_COIN')

    if (request['result']=='SUCCESSFUL'):
        arenaBattleStatus='WIN'
        coins['quantity']+=3
    else:
        arenaBattleStatus='LOSE'
        coins['quantity']+=1

    #updating coins
    dt.setUserObject('userItemList', 'ARENA_COIN', coins)
    userItemList=[coins]

    userDailyChallengeList=[] #TODO
    resultCode="success"
    userArenaBattleResultList=[{
        'arenaBattleStatus': arenaBattleStatus,
        'arenaBattleType': 'FREE_RANK', #change for ranked
        'numberOfConsecutiveWins': 1,
        'userQuestBattleResultId':request['userQuestBattleResultId'],
        'userId': dt.userId,
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
    print(json.dumps(response))
    return flask.jsonify(response)

def giveUserExp(battle):
    userExp = 0 #battle['questBattle']['exp'] # not uncommenting this until we know how to level up
    gameUser = dt.setGameUserValue('exp', dt.getGameUserValue('exp')+userExp)
    newStatus = []
    if gameUser['exp'] >= gameUser['totalExpForNextLevel']:
        dt.setGameUserValue('exp', gameUser['exp'] - gameUser['totalExpForNextLevel'])
        dt.setGameUserValue('level', gameUser['level'] + 1)
        dt.setGameUserValue('totalExpForCurrentLevel', gameUser['totalExpForNextLevel'])
        # TODO: how does this actually work lol
        gameUser = dt.setGameUserValue('totalExpForNextLevel', gameUser['totalExpForNextLevel'] + 10)

        maxAP = dt.getUserObject('userStatusList', 'MAX_ACP')
        currAP = dt.getUserObject('userStatusList', 'ACP')
        maxAP['point'] += 10
        currAP['point'] += maxAP['point']

        newStatus.append(maxAP)
        newStatus.append(currAP)

        dt.setUserObject('userStatusList', 'MAX_ACP', maxAP)
        dt.setUserObject('userStatusList', 'ACP', currAP)
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
        currUserCard = dt.getUserObject('userCardList', cardId)
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
        dt.setUserObject('userCardList', cardId, currUserCard)

    # add episode points to charas
    for i in range(9):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in body:
            cardIds.append(body[numberedId])

    resultUserCharaList = []
    eps = battle['questBattle']['baseBondsPt']
    for charaNo in charaNos:
        userChara = dt.getUserObject('userCharaList', charaNo)
        if charaNo == leaderCharaId:
            eps *= 1.5
        # checking if this is the meguca's MSS
        strBattleId = str(battle['questBattle']['questBattleId'])
        if strBattleId.startswith('3') and strBattleId[1:5] == str(charaNo):
            eps *= 2
        userChara['bondsTotalPt'] += eps

        resultUserCharaList.append(userChara)
        dt.setUserObject('userCharaList', charaNo, userChara)
    return resultUserCardList, resultUserCharaList

def send():
    body = flask.request.json
    battle = dt.readJson('data/user/userQuestBattleResult.json')

    if(battle['battleType']=="ARENA"):
        return sendArena(body,{'userQuestBattleResultList':[battle],'gameUser': dt.readJson('data/user/gameUser.json')})

    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # change userQuestBattleResult status
    storyResponse = None
    if body['result'] == 'FAILED':
        battle['questBattleStatus'] = 'FAILED'
        resultUserQuestBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
        if resultUserQuestBattle is None: # not sure why this would happen, but?? make it just in case
            resultUserQuestBattle = newtil.createUserQuestBattle(battle['questBattleId'])
            dt.setUserObject('userQuestBattleList', battle['questBattleId'], resultUserQuestBattle)
    else:
        battle['questBattleStatus'] = 'SUCCESSFUL'
        # add exp to user and level up, maybe
        gameUser, newStatus = giveUserExp(battle)
        # level up/episode up megucas
        resultUserCardList, resultUserCharaList = giveMegucaExp(body, battle)
        # clear
        if 'cleared' not in battle or not battle['cleared']:
            resultUserQuestBattle = storyUtil.clearBattle(battle)
        else:
            battle['lastClearedAt'] = homu.nowstr()
            battle['clearCount'] = battle.get('clearCount', 0) + 1
        # add to stories
        storyResponse = storyUtil.progressStory(battle)
    
    # TODO: clear missions

    # TODO: calculate drops and add to items
    resultUserItemList = []

    # make response
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'userCardList': resultUserCardList,
        'userCharaList': resultUserCharaList,
        'userItemList': resultUserItemList,
        'userQuestBattleResultList': [battle],
        'userQuestBattleList': [resultUserQuestBattle]
    }
    if storyResponse is not None:
        dt.updateJson(response, storyResponse)
    if newStatus != []:
        response['userStatusList'] = newStatus

    print(response)
    return flask.jsonify(response)