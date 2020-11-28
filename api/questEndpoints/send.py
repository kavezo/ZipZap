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

# courtesy of magireco discord data mining
expForNextLevel = [0, 40, 40, 40, 90, 90, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 
    61, 62, 63, 64, 65, 80, 97, 115, 134, 154, 175, 197, 220, 244, 269, 295, 322, 350, 379, 409, 444, 484, 529, 579, 
    634, 694, 759, 829, 904, 984, 1069, 1159, 1254, 1354, 1504, 1704, 1954, 2254, 2604, 3004, 3454, 3954, 4504, 5104, 
    5754, 6454, 7204, 8004, 8854, 9754, 10704, 11704, 12704, 13704, 14704, 15704, 16704, 17704, 18704, 19704, 20704, 
    21704, 22704, 23704, 24704, 25704, 26704, 27704, 28704, 29704]
def giveUserExp(battle):
    userExp = battle['questBattle']['exp']
    battle['exp'] = battle['questBattle']['exp']
    gameUser = dt.setGameUserValue('exp', dt.getGameUserValue('exp')+userExp)
    newStatus = []
    if gameUser['exp'] >= gameUser['totalExpForNextLevel']:
        newLevel = gameUser['level'] + 1
        dt.setGameUserValue('exp', gameUser['exp'] - gameUser['totalExpForNextLevel'])
        dt.setGameUserValue('level', newLevel)
        dt.setGameUserValue('totalExpForCurrentLevel', gameUser['totalExpForNextLevel'])
        gameUser = dt.setGameUserValue('totalExpForNextLevel', expForNextLevel[newLevel] if newLevel < len(expForNextLevel) else 30704)

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
        userChara['bondsTotalPt'] += round(eps)

        resultUserCharaList.append(userChara)
        dt.setUserObject('userCharaList', charaNo, userChara)
    return resultUserCardList, resultUserCharaList

# TODO: memoria that increase CC amount
def giveDrops(battle, cleared):
    resultDict = {}
    # default drop seems to always be CC...
    if 'defaultDropItem' in battle['questBattle']:
        cc = int(battle['questBattle']['defaultDropItem']['rewardCode1'].split('_')[-1])
        resultDict['gameUser'] = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+cc)
        battle['riche'] = cc

    dropRewardCodes = []
    dropCodes = dt.readJson('data/user/promisedDrops.json')
    if dropCodes['questBattleId'] != battle['questBattleId']: # weird error that should never happen...
        print('questBattleId mismatch when sending drops')
        return resultDict

    # first clear
    dropCodes = list(dropCodes.items()) # unordered dict -> ordered list bc we want the first clear reward to be the first one
    if not cleared:
        dropCodes = [(battle['questBattle']['firstClearRewardCodes'], 1)] + dropCodes

    for dropCode, amount in dropCodes:
        if dropCode == 'questBattleId': continue
        
        if dropCode.startswith('GIFT'):
            giftId = int(dropCode.split('_')[1])
            dropNum = amount*int(dropCode.split('_')[-1]) # seems to be always 1, but whatever
            userGift = dt.getUserObject('userGiftList', giftId)
            userGift['quantity'] += dropNum
            resultDict['userGiftList'] = resultDict.get('userGiftList', []) + [userGift]
            dt.setUserObject('userGiftList', giftId, userGift)
        elif dropCode.startswith('ITEM'):
            itemId = '_'.join(dropCode.split('_')[1:-1])
            dropNum = amount*int(dropCode.split('_')[-1]) # seems to be always 1, but whatever
            userItem = dt.getUserObject('userItemList', itemId)
            userItem['quantity'] += dropNum
            resultDict['userItemList'] = resultDict.get('userItemList', []) + [userItem]
            dt.setUserObject('userItemList', itemId, userItem)
        elif dropCode.startswith('RICHE'):
            cc = amount*int(dropCode.split('_')[-1])
            resultDict['gameUser'] = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+cc)
        dropRewardCodes += [dropCode]*amount

    battle['dropRewardCodes'] = ','.join(dropRewardCodes)
    return resultDict

def send():
    body = flask.request.json
    battle = dt.readJson('data/user/userQuestBattleResult.json')

    if(battle['battleType']=="ARENA"):
        return sendArena(body,{'userQuestBattleResultList':[battle],'gameUser': dt.readJson('data/user/gameUser.json')})

    if not battle['id'] == body['userQuestBattleResultId']:
        flask.abort(400, description='{"errorTxt": "You didn\'t really start this quest, or something...","resultCode": "error","title": "Error"}')

    # really gross, but cbf'd rn to refactor
    storyResponse = None
    dropResponse = None
    resultUserCardList = None
    resultUserCharaList = None
    gameUser = dt.readJson('data/user/gameUser.json')
    newStatus = []

    # change userQuestBattleResult status
    if body['result'] == 'FAILED':
        battle['questBattleStatus'] = 'FAILED'
        resultUserQuestBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
        if resultUserQuestBattle is None: # not sure why this would happen, but?? make it just in case
            resultUserQuestBattle = newtil.createUserQuestBattle(battle['questBattleId'])
            dt.setUserObject('userQuestBattleList', battle['questBattleId'], resultUserQuestBattle)
    else:
        battle['questBattleStatus'] = 'SUCCESSFUL'
        resultUserQuestBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
        # add exp to user and level up, maybe
        gameUser, newStatus = giveUserExp(battle)
        # level up/episode up megucas
        resultUserCardList, resultUserCharaList = giveMegucaExp(body, battle)
        cleared = 'cleared' in resultUserQuestBattle and resultUserQuestBattle['cleared']
        # add drops -- required before clearing
        dropResponse = giveDrops(battle, cleared)
        # clear
        if not cleared:
            resultUserQuestBattle = storyUtil.clearBattle(battle)
        else:
            resultUserQuestBattle['lastClearedAt'] = homu.nowstr()
            resultUserQuestBattle['clearCount'] = resultUserQuestBattle.get('clearCount', 0) + 1
        # add to stories
        storyResponse = storyUtil.progressStory(battle)
    
    # TODO: clear missions

    # make response
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'userCardList': resultUserCardList,
        'userCharaList': resultUserCharaList,
        'userQuestBattleResultList': [battle],
        'userQuestBattleList': [resultUserQuestBattle]
    }

    if storyResponse is not None:
        response = dt.updateJson(response, storyResponse)
    if dropResponse is not None:
        response = dt.updateJson(response, dropResponse)

    if resultUserCardList is not None:
        response['userCardList'] = resultUserCardList
    if resultUserCharaList is not None:
        response['userCharaList'] = resultUserCharaList

    if newStatus != []:
        response['userStatusList'] = newStatus

    print(response)
    return flask.jsonify(response)