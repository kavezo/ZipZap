import json
import re
from datetime import datetime,timedelta
import os
import flask
import random
import copy
import logging

from util import dataUtil as dt
from util import homuUtil as homu

logger = logging.getLogger('app.page')

def arenaTop(response):
    response['userArenaBattle']=dt.readJson('data/user/userArenaBattle.json')
    response['rankingClosing'] = True

def calculateArenaRating():
    arenaDeck = dt.getUserObject('userDeckList', 21)
    cards = [dt.getUserObject('userCardList', v) for k, v in arenaDeck.items() if k.startswith('userCardId')]
    pieces = [dt.getUserObject('userPieceList', v) for k, v in arenaDeck.items() if k.startswith('userPieceId')]
    
    rating = 0
    for userCard in cards:
        rating += userCard['hp']
        rating += userCard['defense']
        rating += userCard['attack']
    for userPiece in pieces:
        rating += userPiece['hp']
        rating += userPiece['defense']
        rating += userPiece['attack']
    return rating

def arenaFreeRank(response):
    # Assumes there are at least three enemies possible, no error checking
    enemies = random.sample(os.listdir('data/arenaEnemies'), k=3)
    enemyInfo = [dt.readJson('data/arenaEnemies/'+enemy)['opponentUserArenaBattleInfo'] for enemy in enemies]

    response['userArenaBattleMatch'] = {
		"userId": "0571792e-f615-11ea-bdf5-024ec58565ab",
		"arenaBattleType": "FREE_RANK",
		"userRatingPoint": calculateArenaRating(),
		"opponentUserId1": enemyInfo[0]['userId'],
		"opponentUserArenaBattleInfo1": enemyInfo[0],
		"opponentUserId2": enemyInfo[1]['userId'],
		"opponentUserArenaBattleInfo2": enemyInfo[1],
		"opponentUserId3": enemyInfo[2]['userId'],
		"opponentUserArenaBattleInfo3": enemyInfo[2],
		"opponentUserIdList": [],
		"matchedAt": homu.nowstr(),
		"expiredAt": (datetime.now()+timedelta(minutes=15)).strftime('%Y/%m/%d %H:%M:%S'),
		"enable": True,
		"isNew": False
	}

def arenaResult(response):
    body = flask.request.json
    opponentId = body['strUserId']
    opponentInfo = dt.readJson('data/arenaEnemies/' + opponentId + '.json')
    response.update({'userProfile': opponentInfo['opponentUserArenaBattleInfo']})

def charaCollection(response):
    response['userSectionList'] = dt.readJson('data/user/userSectionList.json')
    allCards = dt.readJson('data/cards.json') # this could proably use a better refactor

    userCharas = dt.readJson('data/user/userCharaList.json')
    userCharaIds = [chara['charaId'] for chara in userCharas]
    userCards = dt.readJson('data/user/userCardList.json')
    cardIds = {card['cardId']: card['id'] for card in userCards}
        
    for i in range(len(allCards)):
        if allCards[i]['charaId'] in userCharaIds:
            del allCards[i]['chara']
        for j in range(len(allCards[i]['cardList'])):
            currId = allCards[i]['cardList'][j]['cardId']
            if currId in cardIds.keys():
                allCards[i]['cardList'][j] = {'userCardId': cardIds[currId], 'cardId': currId}
                
    response['charaList'] = allCards

def charaListCompose(response):
    response['charaList'] = dt.readJson('data/user/userCharaList.json')
    response['cardList'] = dt.readJson('data/user/userCardList.json')

def charaTop(response):
    response['gameUser'] = dt.readJson('data/user/gameUser.json')

def configTop(response):
    gameUser = dt.readJson('data/user/gameUser.json')
    response['canChangeLoginName'] = True
    response['setPassword'] = 'passwordNotice' in gameUser and gameUser['passwordNotice']

def followTop(response):
    response['userFollowList'] = dt.readJson('data/user/userFollowList.json')
    response['followers'] = dt.getUserValue('followCount')
    response['blocked'] = 0

def gachaHistory(response):
    response['gachaHistoryList'] = dt.readJson('data/user/gachaHistoryList.json')
    response['gachaHistoryCount'] = len(response['gachaHistoryList'])

def gachaTop(response):
    response['userGachaGroupList'] = dt.readJson('data/user/userGachaGroupList.json')
    response['gachaScheduleList'] = dt.readJson('data/gachaScheduleList.json')

def magiRepo(response):
    response['magiRepoList'] = dt.readJson('data/magiRepoList.json')

def pieceArchive(response):
    userPieceList = dt.readJson('data/user/userPieceList.json')
    response['userPieceArchiveList'] = [userPiece for userPiece in userPieceList if userPiece['archive']]

def pieceCollection(response):
    response['userPieceCollectionList'] = dt.readJson('data/user/userPieceCollectionList.json')

def presentList(response):
    response['presentList'] = []

def shopTop(response):
    response['shopList'] = dt.readJson('data/shopList.json')
    response['userShopItemList'] = dt.readJson('data/user/userShopItemList.json')

    shopItemIds = set([item['shopItemId'] for item in response['userShopItemList']])
    backgrounds = {'HOME_EV_1003_21028': 381, 'HOME_MAP_11011': 1720, 'HOME_MAP_11012': 1721, 
                    'HOME_MAP_11013': 1722, 'HOME_EV_1033_13101': 2388}
    addBackgrounds = [itemId for itemId in backgrounds.keys() 
                        if dt.getUserObject('userItemList', itemId) is not None
                        and backgrounds[itemId] not in shopItemIds]
    for itemId in addBackgrounds:
        response['userShopItemList'].append({
            "createdAt": homu.nowstr(),
            "num": 1,
            "shopItemId": backgrounds[itemId],
            "userId": dt.userId
        })

    formations = {'911': 999431, '912': 999432, '913': 999433, '921': 999434, '922': 999435, '923': 999436, 
                '131': 5, '141': 424, '151': 425, '161': 426, '171': 427, '181': 428, '711': 999428, '611': 999430}
    addFormations = [itemId for itemId in formations.keys() 
                        if dt.getUserObject('userItemList', itemId) is not None
                        and formations[itemId] not in shopItemIds]
    for itemId in addFormations:
        response['userShopItemList'].append({
            "createdAt": homu.nowstr(),
            "num": 1,
            "shopItemId": formations[itemId],
            "userId": dt.userId
        })

def storyCollection(response):
    response['eventStoryList'] = dt.readJson('data/eventStoryList.json')
    response['arenaBattleFreeRankClassList'] = dt.readJson('data/arenaBattleFreeRankClassList.json')
    response['userArenaBattle'] = dt.readJson('data/user/userArenaBattle.json')
    response['campaignStoryList'] = dt.readJson('data/campaignStoryList.json')

def supportSelect(response):
    response['npcHelpList'] = [dt.readJson('data/npc.json')]

def doppelCollection(response):
    response['doppelList'] = dt.masterDoppels

def enemyCollection(response):
    response['enemyList'] = dt.readJson('data/enemyList.json')
    response['userEnemyList'] = dt.readJson('data/user/userEnemyList.json')

specialCases = {
    "ArenaFreeRank": arenaFreeRank,
    "ArenaResult": arenaResult,
    "ArenaTop": arenaTop,
    "CharaCollection": charaCollection,
    "CharaTop": charaTop,
    "ConfigTop": configTop,
    "FollowTop": followTop,
    "GachaHistory": gachaHistory,
    "GachaTop": gachaTop,
    "GachaResult": gachaTop,
    "MagiRepo": magiRepo,
    "PieceArchive": pieceArchive,
    "PieceCollection": pieceCollection,
    "PresentList": presentList,
    "ShopTop": shopTop,
    "StoryCollection": storyCollection,
    "SupportSelect": supportSelect,
    "DoppelCollection": doppelCollection,
    "EnemyCollection": enemyCollection
}

# TODO: clear history on first login of the day
def login(user):
    logger.info('logging in')
    nowstr = homu.nowstr()
    lastLogin = datetime.strptime(user['lastLoginDate'], '%Y/%m/%d %H:%M:%S')
    if (lastLogin.date()-datetime.today().date()).days == 1:
        user['loginDaysInRow'] += 1
        user['todayFirstAccessDate'] = nowstr
        user['dataPatchedAt'] = nowstr
    
    user['loginCount'] += 1
    user['penultimateLoginDate'] = user['lastLoginDate']
    user['lastLoginDate'] = nowstr
    user['lastAccessDate'] = nowstr
    user['indexingTargetDate'] = nowstr

    dt.setGameUserValue('announcementViewAt', nowstr)
    return user

def addArgs(response, args, isLogin):
    user = dt.readJson('data/user/user.json')

    lastLogin = datetime.strptime(user['lastLoginDate'], '%Y/%m/%d %H:%M:%S')
    # checking if midnight passed; logins have to happen then too
    if isLogin or (lastLogin.date()-datetime.today().date()).days > 0:
        user = login(user)
        dt.saveJson('data/user/user.json', user)

    for arg in args:
        if arg in ['user', 'gameUser',
        'userLive2dList', 'userCardList', 'userCharaList', 'userDeckList', 'userFormationSheetList',
        'userPieceList', 'userPieceSetList', 'userItemList', 'userSectionList', 'userGiftList',
        'userQuestAdventureList', 'userQuestBattleList', 'userChapterList', 'userDoppelList',
        'userDailyChallengeList', 'userLimitedChallengeList', 'userTotalChallengeList',]:
            logger.info('loading ' + arg + ' from json')
            fpath = 'data/user/'+arg+'.json'
            if os.path.exists(fpath):
                response[arg] = dt.readJson(fpath)
                if arg == 'userPieceList':
                    response[arg] = [userPiece for userPiece in response[arg] if not userPiece['archive']]
            else:
                logger.warning(f'{fpath} not found')
        elif arg == 'userStatusList':
            response[arg] = homu.getAllStatuses()
        elif arg in ['itemList', 'giftList', 'pieceList']:
            logger.info('loading ' + arg + ' from json')
            fpath = 'data/'+arg+'.json'
            if os.path.exists(fpath):
                response[arg] = dt.readJson(fpath)
            else:
                logger.warning(f'{fpath} not found')
        elif arg.endswith('BattleResultList'):
            logger.info('loading ' + arg[:-4] + ' from json')
            fpath = 'data/user/'+arg[:-4]+'.json'
            if os.path.exists(fpath):
                response[arg] = dt.readJson(fpath)
        elif arg.lower().endswith('list'):
            response[arg] = []

def handlePage(endpoint):
    response = dt.readJson('data/events.json')
    response['currentTime'] = homu.nowstr()

    args = flask.request.args.get('value')
    if args is not None:
        args = re.sub(r'&timeStamp=\d+', '', args) \
                .replace('value=', '') \
                .split(',')
    else:
        args = []
    if endpoint in specialCases.keys():
        specialCases[endpoint](response)
    
    if endpoint=='ResumeBackground':
        logger.info('resuming')

    addArgs(response, args, 'TopPage' in endpoint) # login if it's TopPage
    return flask.jsonify(response)
