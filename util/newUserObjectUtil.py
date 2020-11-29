from util import dataUtil as dt
from util.homuUtil import nowstr

from uuid import uuid1
from datetime import datetime

def createUserLive2d(charaId, live2dId, description):
    return {
        "userId": dt.userId,
        "charaId": charaId,
        "live2dId": live2dId,
        "live2d": {
            "charaId": charaId,
            "live2dId": live2dId,
            "description": description,
            "defaultOpened": False,
            "voicePrefixNo": live2dId
        },
        "createdAt": nowstr()
    }, dt.getUserObject('userLive2dList', str(charaId)+str(live2dId)) is not None

def createUserMeguca(charaId, card=None):
    userCardId = str(uuid1())
    masterCard = dt.masterCards[charaId]
    chara = masterCard['chara']

    if card is None:
        card = masterCard['cardList'][0]['card']
    userCard = {
        "id": userCardId,
        "userId": dt.userId,
        "cardId": card['cardId'],
        "displayCardId": card['cardId'],
        "revision": 0,
        "attack": card['attack'],
        "defense": card['defense'],
        "hp": card['hp'],
        "level": 1,
        "experience": 0,
        "magiaLevel": 1,
        "enabled": True,
        "customized1": False,
        "customized2": False,
        "customized3": False,
        "customized4": False,
        "customized5": False,
        "customized6": False,
        "createdAt": nowstr(),
        "card": card
    }
    userChara = {
        "userId": dt.userId,
        "charaId": charaId,
        "chara": chara,
        "bondsTotalPt": 0,
        "userCardId": userCardId,
        "lbItemNum": 0,
        "visualizable": True,
        "commandVisualType": "CHARA",
        "commandVisualId": charaId,
        "live2dId": "00",
        "createdAt": nowstr()
    }
    userLive2d, _ = createUserLive2d(charaId, '00', 'Magical Girl')
    userLive2d['defaultOpened'] = True
    return userCard, userChara, userLive2d

def createUserMemoria(pieceId):
    piece = dt.masterPieces[pieceId]
    
    userPieceId = str(uuid1())
    userPiece = {
        "id": userPieceId,
        "userId": dt.userId,
        "pieceId": piece['pieceId'],
        "piece": piece,
        "level": 1,
        "experience": 0,
        "lbCount": 0,
        "attack": piece['attack'],
        "defense": piece['defense'],
        "hp": piece['hp'],
        "protect": False,
        "archive": False,
        "createdAt": nowstr()
    }
    dt.setUserObject('userPieceList', userPieceId, userPiece)
    return userPiece

def createUserGachaGroup(groupId):
    return {
        "userId": dt.userId,
        "gachaGroupId": groupId,
        "count": 0,
        "paid": 0,
        "totalCount": 0,
        "dailyCount": 0,
        "weeklyCount": 0,
        "monthlyCount": 0,
        "currentScheduleId": 20,
        "resetCount": 0,
        "createdAt": nowstr()
    }

def createUserItem(item):
    return {
        "userId": dt.userId,
        "itemId": item['itemCode'],
        "environmentId": "COMMON",
        "quantity": 0,
        "total": 0,
        "item": item,
        "createdAt": nowstr()
    }

def createUserDoppel(doppelId):
    doppel = dt.masterDoppels[doppelId]
    return {
        "userId": dt.userId,
        "doppelId": doppelId,
        "doppel": doppel,
        "createdAt": nowstr()
    }, dt.getUserObject('userDoppelList', doppelId) is not None

def createUserFormation(formationId):
    formation = dt.masterFormations[formationId]
    return {
        "userId": dt.userId,
        "formationSheetId": formationId,
        "createdAt": nowstr(),
        "formationSheet": formation
    }, dt.getUserObject('userFormationSheetList', formationId) is not None

def createUserPiece(pieceId):
    found = False
    for userPiece in dt.readJson('data/user/userPieceList.json'):
        if userPiece['pieceId'] == pieceId:
            found = True
    piece = dt.masterPieces[pieceId]
    return {
        "id": str(uuid1()),
        "userId": dt.userId,
        "pieceId": piece['pieceId'],
        "piece": piece,
        "level": 1,
        "experience": 0,
        "lbCount": 0,
        "attack": piece['attack'],
        "defense": piece['defense'],
        "hp": piece['hp'],
        "protect": False,
        "archive": False,
        "createdAt": nowstr()
    }, found

def createUserSection(sectionId):
    return {
        "userId": dt.userId,
        "sectionId": sectionId,
        "section": dt.masterSections[sectionId],
        "canPlay": True,
        "cleared": False,
        "createdAt": nowstr()
    }, dt.getUserObject('userSectionList', sectionId) is not None

def createUserChapter(chapterId):
    return {
        "chapter": dt.masterChapters[chapterId],
        "chapterId": chapterId,
        "cleared": False,
        "createdAt": nowstr(),
        "userId": dt.userId
    }, dt.getUserObject('userChapterList', chapterId) is not None

def createUserQuestBattle(battleId):
    return {
        "userId": dt.userId,
        "questBattleId": battleId,
        "questBattle": dt.masterBattles[battleId],
        "cleared": False,
        "missionStatus1": "NON_CLEAR",
        "missionStatus2": "NON_CLEAR",
        "missionStatus3": "NON_CLEAR",
        "rewardDone": False,
        "createdAt": nowstr()
    }, dt.getUserObject('userQuestBattleList', battleId) is not None

def createUserEnemy(enemyId):
    return {
        'userId': dt.userId,
        'createdAt': nowstr(),
        'enemyId': enemyId,
        'enemy': dt.masterEnemies[enemyId]
    }, dt.getUserObject('userEnemyList', enemyId) is not None