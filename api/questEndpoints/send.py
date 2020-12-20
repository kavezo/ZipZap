import flask
import json
import re
import logging

from api import userCard
from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util import storyUtil
from util import homuUtil as homu

logger = logging.getLogger('app.quest.send')

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
    userArenaBattleResult = dt.readJson('data/user/userArenaBattleResult.json')

    coins = dt.getUserObject('userItemList', 'ARENA_COIN')

    if (request['result']=='SUCCESSFUL'):
        coins['quantity']+=3

        numTurnsCapped = min(max(request['totalTurn'], 2), 7) # cap to 2 and 7
        turnBonus = 1.0 + 0.1*(7-numTurnsCapped)
        opponentBonus = {'SAME': 1.0, 'HIGHER': 1.2, 'LOWER': 0.8}[userArenaBattleResult['arenaBattleOpponentType']]
        consecBonus = [0,1,2,3,5,7,10][userArenaBattleResult['numberOfConsecutiveWins']-1]
        getPoints = 10 * turnBonus * opponentBonus + consecBonus
        userArenaBattle['freeRankArenaPoint'] += getPoints

        userArenaBattleResult['arenaBattleStatus'] = 'WIN'
        userArenaBattleResult['numberOfConsecutiveWins'] = userArenaBattleResult['numberOfConsecutiveWins'] % 7 + 1
        userArenaBattleResult['point'] = getPoints

        dt.setGameUserValue('numberOfFreeRankTotalWins', dt.getGameUserValue('numberOfFreeRankTotalWins')+1)
    else:
        userArenaBattleResult['arenaBattleStatus']='LOSE'
        coins['quantity']+=1
        userArenaBattleResult['numberOfConsecutiveWins'] = 0

        userArenaBattle['freeRankArenaPoint'] += 3
        userArenaBattleResult['point'] = userArenaBattle['freeRankArenaPoint']

    dt.setGameUserValue('freeRankArenaPoint', userArenaBattle['freeRankArenaPoint'])
    gameUser = dt.setGameUserValue('numberOfFreeRankConsecutiveWins', userArenaBattleResult['numberOfConsecutiveWins'])

    dt.saveJson('data/user/userArenaBattle.json', userArenaBattle)
    dt.saveJson('data/user/userArenaBattleResult.json', userArenaBattleResult)

    # updating coins
    dt.setUserObject('userItemList', 'ARENA_COIN', coins)
    userItemList=[coins]

    resultCode="success"
    response.update({
        'gameUser': gameUser,
        'userArenaBattle' : userArenaBattle,
        'userItemList': userItemList,
        'userArenaBattleResultList': [userArenaBattleResult],
        'resultCode': resultCode
    })
    response = storyUtil.progressMirrors(response)
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
        maxAP['point'] += 1
        currAP['point'] += maxAP['point']

        newStatus.append(maxAP)
        newStatus.append(currAP)

        dt.setUserObject('userStatusList', 'MAX_ACP', maxAP)
        dt.setUserObject('userStatusList', 'ACP', currAP)
    return gameUser, newStatus

def giveMegucaExp(battle):
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

def obtainItem(itemCode, amount=1):
    resultDict = {}
    if itemCode.startswith('GIFT'):
        giftId = int(itemCode.split('_')[1])
        dropNum = amount*int(itemCode.split('_')[-1]) # seems to be always 1, but whatever
        userGift = dt.getUserObject('userGiftList', giftId)
        userGift['quantity'] += dropNum
        resultDict['userGiftList'] = resultDict.get('userGiftList', []) + [userGift]
        dt.setUserObject('userGiftList', giftId, userGift)
    elif itemCode.startswith('ITEM'):
        itemId = '_'.join(itemCode.split('_')[1:-1])
        dropNum = amount*int(itemCode.split('_')[-1]) # seems to be always 1, but whatever
        userItem = dt.getUserObject('userItemList', itemId)
        userItem['quantity'] += dropNum
        resultDict['userItemList'] = resultDict.get('userItemList', []) + [userItem]
        dt.setUserObject('userItemList', itemId, userItem)
    elif itemCode.startswith('RICHE'):
        cc = amount*int(itemCode.split('_')[-1])
        resultDict['gameUser'] = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+cc)
    return resultDict

# TODO: memoria that increase CC amount
def giveDrops(battle):
    resultDict = {}
    # default drop seems to always be CC...
    if 'defaultDropItem' in battle['questBattle']:
        cc = int(battle['questBattle']['defaultDropItem']['rewardCode1'].split('_')[-1])
        resultDict['gameUser'] = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+cc)
        battle['riche'] = cc

    dropRewardCodes = []
    dropCodes = dt.readJson('data/user/promisedDrops.json')
    if dropCodes['questBattleId'] != battle['questBattleId']: # weird error that should never happen...
        logger.error('questBattleId mismatch when sending drops')
        return resultDict
    for dropCode, amount in dropCodes.items():
        if dropCode == 'questBattleId': continue
        resultDict = dt.updateJson(resultDict, obtainItem(dropCode, amount))        
        dropRewardCodes += [dropCode]*amount

    battle['dropRewardCodes'] = ','.join(dropRewardCodes)
    return resultDict

def clearMissions(body, battle):
    questBattle = battle['questBattle']
    missionCodes = [questBattle['mission1'], questBattle['mission2'], questBattle['mission3']]

    userQuestBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
    if all([battle['clearedMission1'], battle['clearedMission2'], battle['clearedMission3']]):
        return battle, userQuestBattle, {}

    def clearMission(missionNum, battle, userQuestBattle):
        userQuestBattle['missionStatus'+missionNum] = 'CLEARED'
        battle['clearedMission'+missionNum] = True

    for i, missionCode in enumerate(missionCodes):
        missionNum = str(i+1)
        count = int(missionCode.split('_')[-1]) if re.fullmatch(r'\d+', missionCode.split('_')[-1]) else None
        if missionCode == 'NOT_DEAD':
            if body['deadNum'] == 0: clearMission(missionNum, battle, userQuestBattle)
        if missionCode == 'NOT_CONTINUE':
            if body['continueNum'] == 0: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('ACTION'):
            if body['totalTurn'] <= count: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('HP'):
            if body['rateHp'] >= count: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('COUNT_CONNECT'):
            if body['connectNum'] >= count: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('ONLY_DAMAGE_ATTRIBUTE'):
            attributeDamage = {
                'DARK': body['totalDamageByDark'],
                'FIRE': body['totalDamageByFire'],
                'LIGHT': body['totalDamageByLight'],
                'TIMBER': body['totalDamageByTimber'],
                'VOID': body['totalDamageByVoid'],
                'WATER': body['totalDamageByWater']
            }
            attribute = missionCode.split('_')[-1]
            del attributeDamage[attribute]
            if sum(attributeDamage.values()) == 0: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('COMBO'):
            comboType = missionCode.split('_')[1].lower().capitalize()
            if body['combo'+comboType+'Num'] >= count: clearMission(missionNum, battle, userQuestBattle)
        if missionCode.startswith('MEMBER_CHARA'):
            userCardIds = [v for k, v in battle.items() if k.startswith('userCardId')]
            charaNos = [dt.getUserObject('userCardList', userCardId)['card']['charaNo'] for userCardId in userCardIds]
            if count in charaNos: clearMission(missionNum, battle, userQuestBattle)
        if missionCode in ['CLEAR', 'WAVE_1', 'ONLY_MEMBER_COUNT_5']: # automatic mission clear
            clearMission(missionNum, battle, userQuestBattle)
    
    rewards = {}
    if all([battle['clearedMission1'], battle['clearedMission2'], battle['clearedMission3']]):
        missionRewardCode = questBattle['missionRewardCode']
        rewards = obtainItem(missionRewardCode)
        userQuestBattle['rewardDone'] = True

    dt.setUserObject('userQuestBattleList', userQuestBattle['questBattleId'], userQuestBattle)
    return battle, userQuestBattle, rewards

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
    rewardResponse = None
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
        resultUserCardList, resultUserCharaList = giveMegucaExp(battle)
        cleared = 'cleared' in resultUserQuestBattle and resultUserQuestBattle['cleared']
        # add drops -- required before clearing
        dropResponse = giveDrops(battle)
        # clear
        if not cleared:
            resultUserQuestBattle = storyUtil.clearBattle(battle)
            storyResponse = storyUtil.progressStory(battle)
        else:
            resultUserQuestBattle['lastClearedAt'] = homu.nowstr()
            resultUserQuestBattle['clearCount'] = resultUserQuestBattle.get('clearCount', 0) + 1        
        # missions
        battle, resultUserQuestBattle, rewardResponse = clearMissions(body, battle)

    # make response
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'userCardList': resultUserCardList,
        'userCharaList': resultUserCharaList,
        'userQuestBattleResultList': [battle],
        'userQuestBattleList': [resultUserQuestBattle]
    }

    for partResponse in [storyResponse, dropResponse, rewardResponse]:
        if partResponse is not None:
            response = dt.updateJson(response, partResponse)

    if resultUserCardList is not None:
        response['userCardList'] = resultUserCardList
    else:
        response['userCardList'] = dt.readJson('data/user/userCardList.json')
    if resultUserCharaList is not None:
        response['userCharaList'] = resultUserCharaList
    else:
        response['userCharaList'] = dt.readJson('data/user/userCharaList.json')

    if newStatus != []:
        response['userStatusList'] = newStatus

    return flask.jsonify(response)