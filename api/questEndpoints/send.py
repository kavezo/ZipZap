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
        dt.setGameUserValue('level', newLevel)
        dt.setGameUserValue('totalExpForCurrentLevel', gameUser['totalExpForNextLevel'])

        expAdd = 0
        for i in range(0, newLevel + 1):
            expAdd += expForNextLevel[i] if i < len(expForNextLevel) else 30704        
        
        gameUser = dt.setGameUserValue('totalExpForNextLevel', gameUser['totalExpForNextLevel'] + expAdd)

        maxAP = dt.getUserObject('userStatusList', 'MAX_ACP')
        currAP = dt.getUserObject('userStatusList', 'ACP')
        maxAP['point'] += 1
        currAP['point'] += maxAP['point']

        currBP = dt.getUserObject('userStatusList', 'BTP')
        currBP['point'] = 5

        newStatus.append(maxAP)
        newStatus.append(currAP)

        dt.setUserObject('userStatusList', 'MAX_ACP', maxAP)
        dt.setUserObject('userStatusList', 'ACP', currAP)
        dt.setUserObject('userStatusList', 'BTP', currBP)
    return gameUser, newStatus

def getEpisodeUpCards(deckType):
    # in order to do this we have to actually use the userDeck, there's no other record of which
    # meguca has which memes on it
    episodeUpCards = []

    userDeck = dt.getUserObject('userDeckList', deckType)
    for card in range(1, 5):
        for piece in range(1, 5):
            pieceKey = f'userPieceId0{card}{piece}'
            if pieceKey in userDeck:
                userPiece = dt.getUserObject('userPieceList', userDeck[pieceKey])
                if '700216301' in json.dumps(userPiece): # this is so hacky I hate this but I'm too lazy to do more
                    episodeUpCards.append(userDeck[f'userCardId{card}'])
    
    return episodeUpCards

def giveMegucaExp(battle):
    # add exp to cards
    charaNos = {}
    cardIds = []
    resultUserCardList = []
    for i in range(9):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in battle:
            cardIds.append(battle[numberedId])

    for cardId in cardIds:
        currUserCard = dt.getUserObject('userCardList', cardId)
        charaNos[cardId] = currUserCard['card']['charaNo']
        
        rank = currUserCard['card']['rank']
        exp = battle['questBattle']['cardExp']
        currUserCard = userCard.levelUp(currUserCard, rank, exp)  
        
        resultUserCardList.append(currUserCard)
        dt.setUserObject('userCardList', cardId, currUserCard)

    # add episode points to charas
    episodeUpCards = getEpisodeUpCards(battle['deckType'])

    resultUserCharaList = []
    resultUserSectionList = []
    baseBondsPt = battle['questBattle']['baseBondsPt']
    for cardId, charaNo in charaNos.items():
        userChara = dt.getUserObject('userCharaList', charaNo)

        episodeLevelBefore = storyUtil.getEpisodeLevel(userChara)
        eps = baseBondsPt
        
        if cardId == battle['episodeUserCardId']:
            eps *= 1.5
        if cardId in episodeUpCards:
            eps *= 1.15

        # checking if this is the meguca's MSS
        strBattleId = str(battle['questBattle']['questBattleId'])
        if strBattleId.startswith('3') and strBattleId[1:5] == str(charaNo):
            eps *= 2
        userChara['bondsTotalPt'] += round(eps)

        resultUserCharaList.append(userChara)
        dt.setUserObject('userCharaList', charaNo, userChara)

        # check to see if we need to unlock a section
        episodeLevelAfter = storyUtil.getEpisodeLevel(userChara)
        if episodeLevelAfter > episodeLevelBefore and episodeLevelAfter != 4:
            unlockSectionId = int(f'3{charaNo}{episodeLevelAfter}')
            if episodeLevelAfter == 5: # a quirk...doppel sections are always 3{charaNo}4 and only unlock with level 5
                unlockSectionId = int(f'3{charaNo}4')
            
            unlockSection = dt.getUserObject('userSectionList', unlockSectionId)
            if unlockSection is not None:
                unlockSection['canPlay'] = True
            dt.setUserObject('userSectionList', unlockSectionId, unlockSection)
            resultUserSectionList.append(unlockSection)

    return resultUserCardList, resultUserCharaList, resultUserSectionList

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

def giveDrops(battle):
    resultDict = {}
    # default drop seems to always be CC...
    if 'defaultDropItem' in battle['questBattle']:
        cc = int(battle['questBattle']['defaultDropItem']['rewardCode1'].split('_')[-1])
        if len(getEpisodeUpCards(battle['deckType'])) > 0: cc *= 1.05 # CC up memes
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
        if missionCode.startswith('ONLY_MEMBER_COUNT'):
            if len(body['playerList']) <= count: clearMission(missionNum, battle, userQuestBattle)
        if missionCode in ['CLEAR', 'WAVE_1']: # automatic mission clear
            clearMission(missionNum, battle, userQuestBattle)
    
    rewards = {}
    if all([battle['clearedMission1'], battle['clearedMission2'], battle['clearedMission3']]):
        missionRewardCode = questBattle['missionRewardCode']
        rewards = obtainItem(missionRewardCode)
        userQuestBattle['rewardDone'] = True

    dt.setUserObject('userQuestBattleList', userQuestBattle['questBattleId'], userQuestBattle)
    return battle, userQuestBattle, rewards

def getBattleCards(battle):
    cardIds = [battle[key] for key in battle.keys() if key.startswith('userCardId')]
    cards = []
    charaIds = []
    for cardId in cardIds:
        userCard = dt.getUserObject('userCardList', cardId)
        if userCard is not None:
            cards.append(userCard)
            charaIds.append(userCard['card']['charaNo'])

    charas = []
    for charaId in charaIds:
        userChara = dt.getUserObject('userCharaList', charaId)
        if userChara is not None:
            charas.append(userChara)

    return cards, charas

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
    resultUserSectionList = None
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
        resultUserCardList, resultUserCharaList, resultUserSectionList = giveMegucaExp(battle)
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

    # a bunch of stuff that may or may not be necessary depending on which story and who's participating
    for partResponse in [storyResponse, dropResponse, rewardResponse]:
        if partResponse is not None:
            response = dt.updateJson(response, partResponse)

    userCards, userCharas = getBattleCards(battle)
    if resultUserCardList is not None:
        response['userCardList'] = resultUserCardList
    else:
        response['userCardList'] = userCards
    if resultUserCharaList is not None:
        response['userCharaList'] = resultUserCharaList
    else:
        response['userCharaList'] = userCharas
    if resultUserSectionList is not None and len(resultUserSectionList) != 0:
        response['userSectionList'] = resultUserSectionList

    if newStatus != []:
        response['userStatusList'] = newStatus

    return flask.jsonify(response)