import json
import re
from datetime import datetime,timedelta
import os
import flask
import random
import copy

from util import dataUtil, newUserObjectUtil

def arenaTop(response):
    response['userArenaBattle']=dataUtil.readJson('data/user/userArenaBattle.json')
    response['rankingClosing'] = True

def calculateArenaRating():
    arenaDeck = dataUtil.getUserObject('userDeckList', 21)
    cards = [dataUtil.getUserObject('userCardList', v) for k, v in arenaDeck.items() if k.startswith('userCardId')]
    pieces = [dataUtil.getUserObject('userPieceList', v) for k, v in arenaDeck.items() if k.startswith('userPieceId')]
    
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
    enemyInfo = [dataUtil.readJson('data/arenaEnemies/'+enemy)['opponentUserArenaBattleInfo'] for enemy in enemies]

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
		"matchedAt": newUserObjectUtil.nowstr(),
		"expiredAt": (datetime.now()+timedelta(minutes=15)).strftime('%Y/%m/%d %H:%M:%S'),
		"enable": True,
		"isNew": False
	}

def arenaResult(response):
    dummyResponse=dataUtil.readJson('data/arenaResultDummy.json')
    response.update(dummyResponse)

def charaCollection(response):
    response['userSectionList'] = dataUtil.readJson('data/user/userSectionList.json')
    allCards = dataUtil.readJson('data/cards.json') # this could proably use a better refactor

    userCharas = dataUtil.readJson('data/user/userCharaList.json')
    userCharaIds = [chara['charaId'] for chara in userCharas]
    userCards = dataUtil.readJson('data/user/userCardList.json')
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
    response['charaList'] = dataUtil.readJson('data/user/userCharaList.json')
    response['cardList'] = dataUtil.readJson('data/user/userCardList.json')

def charaTop(response):
    response['gameUser'] = dataUtil.readJson('data/user/gameUser.json')

def configTop(response):
    gameUser = dataUtil.readJson('data/user/gameUser.json')
    response['canChangeLoginName'] = True
    response['setPassword'] = 'passwordNotice' in gameUser and gameUser['passwordNotice']

def followTop(response):
    response['userFollowList'] = dataUtil.readJson('data/user/userFollowList.json')
    response['followers'] = dataUtil.getUserValue('followCount')
    response['blocked'] = 0

def gachaHistory(response):
    response['gachaHistoryList'] = dataUtil.readJson('data/user/gachaHistoryList.json')
    response['gachaHistoryCount'] = len(response['gachaHistoryList'])

def gachaTop(response):
    response['userGachaGroupList'] = dataUtil.readJson('data/user/userGachaGroupList.json')
    response['gachaScheduleList'] = dataUtil.readJson('data/gachaScheduleList.json')

def magiRepo(response):
    response['magiRepoList'] = dataUtil.readJson('data/magiRepoList.json')

def pieceArchive(response):
    userPieceList = dataUtil.readJson('data/user/userPieceList.json')
    response['userPieceArchiveList'] = [userPiece for userPiece in userPieceList if userPiece['archive']]

def pieceCollection(response):
    response['userPieceCollectionList'] = dataUtil.readJson('data/user/userPieceCollectionList.json')

def presentList(response):
    response['presentList'] = []

def shopTop(response):
    response['shopList'] = dataUtil.readJson('data/shopList.json')
    response['userShopItemList'] = dataUtil.readJson('data/user/userShopItemList.json')

    shopItemIds = set([item['shopItemId'] for item in response['userShopItemList']])
    backgrounds = {'HOME_EV_1003_21028': 381, 'HOME_MAP_11011': 1720, 'HOME_MAP_11012': 1721, 
                    'HOME_MAP_11013': 1722, 'HOME_EV_1033_13101': 2388}
    addBackgrounds = [itemId for itemId in backgrounds.keys() 
                        if dataUtil.getUserObject('userItemList', itemId) is not None
                        and backgrounds[itemId] not in shopItemIds]
    for itemId in addBackgrounds:
        response['userShopItemList'].append({
            "createdAt": newUserObjectUtil.nowstr(),
            "num": 1,
            "shopItemId": backgrounds[itemId],
            "userId": dataUtil.userId
        })

    formations = {'911': 999431, '912': 999432, '913': 999433, '921': 999434, '922': 999435, '923': 999436, 
                '131': 5, '141': 424, '151': 425, '161': 426, '171': 427, '181': 428, '711': 999428, '611': 999430}
    addFormations = [itemId for itemId in formations.keys() 
                        if dataUtil.getUserObject('userItemList', itemId) is not None
                        and formations[itemId] not in shopItemIds]
    for itemId in addFormations:
        response['userShopItemList'].append({
            "createdAt": newUserObjectUtil.nowstr(),
            "num": 1,
            "shopItemId": formations[itemId],
            "userId": dataUtil.userId
        })

def storyCollection(response):
    response['eventStoryList'] = dataUtil.readJson('data/eventStoryList.json')
    response['arenaBattleFreeRankClassList'] = dataUtil.readJson('data/arenaBattleFreeRankClassList.json')
    response['userArenaBattle'] = dataUtil.readJson('data/user/userArenaBattle.json')
    response['campaignStoryList'] = dataUtil.readJson('data/campaignStoryList.json')

def supportSelect(response):
    response['npcHelpList'] = [dataUtil.readJson('data/npc.json')]

def doppelCollection(response):
    response['doppelList'] = dataUtil.masterDoppels

def enemyCollection(response):
    response['enemyList'] = dataUtil.readJson('data/enemyList.json')
    response['userEnemyList'] = dataUtil.readJson('data/user/userEnemyList.json')

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
    print('logging in')
    nowstr = newUserObjectUtil.nowstr()
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

    dataUtil.setGameUserValue('announcementViewAt', nowstr)
    return user

def addArgs(response, args, isLogin):
    user = dataUtil.readJson('data/user/user.json')

    lastLogin = datetime.strptime(user['lastLoginDate'], '%Y/%m/%d %H:%M:%S')
    # checking if midnight passed; logins have to happen then too
    if isLogin or (lastLogin.date()-datetime.today().date()).days > 0:
        user = login(user)
        dataUtil.saveJson('data/user/user.json', user)

    for arg in args:
        if arg in ['user', 'gameUser', 'userStatusList',
        'userLive2dList', 'userCardList', 'userCharaList', 'userDeckList', 'userFormationSheetList',
        'userPieceList', 'userPieceSetList', 'userItemList', 'userSectionList', 'userGiftList',
        'userQuestAdventureList', 'userQuestBattleList', 'userChapterList', 'userDoppelList',
        'userDailyChallengeList', 'userLimitedChallengeList', 'userTotalChallengeList',]:
            print('loading ' + arg + ' from json')
            fpath = 'data/user/'+arg+'.json'
            if os.path.exists(fpath):
                response[arg] = dataUtil.readJson(fpath)
                if arg == 'userPieceList':
                    response[arg] = [userPiece for userPiece in response[arg] if not userPiece['archive']]
            else:
                print(f'{fpath} not found')
        elif arg in ['itemList', 'giftList', 'pieceList']:
            print('loading ' + arg + ' from json')
            fpath = 'data/'+arg+'.json'
            if os.path.exists(fpath):
                response[arg] = dataUtil.readJson(fpath)
            else:
                print(f'{fpath} not found')
        elif arg.endswith('BattleResultList'):
            print('loading ' + arg[:-4] + ' from json')
            fpath = 'data/user/'+arg[:-4]+'.json'
            if os.path.exists(fpath):
                response[arg] = dataUtil.readJson(fpath)
        elif arg.lower().endswith('list'):
            response[arg] = []

def handlePage(endpoint):
    response = dataUtil.readJson('data/events.json')

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
        print('resuming')

    addArgs(response, args, 'TopPage' in endpoint) # login if it's TopPage
    #print(response) 
    return flask.jsonify(response)
