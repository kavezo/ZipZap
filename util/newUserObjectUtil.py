from util import dataUtil
from uuid import uuid1
from datetime import datetime

def createUserMeguca(charaId, card=None):
    userCardId = str(uuid1())
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    masterCard = dataUtil.masterCards[charaId]
    chara = masterCard['chara']

    if card is None:
        card = masterCard['cardList'][0]['card']
    userCard = {
        "id": userCardId,
        "userId": dataUtil.userId,
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
        "createdAt": nowstr,
        "card": card
    }
    userChara = {
        "userId": dataUtil.userId,
        "charaId": charaId,
        "chara": chara,
        "bondsTotalPt": 0,
        "userCardId": userCardId,
        "lbItemNum": 0,
        "visualizable": True,
        "commandVisualType": "CHARA",
        "commandVisualId": charaId,
        "live2dId": "00",
        "createdAt": nowstr
    }
    userLive2d = {
        "userId": dataUtil.userId,
        "charaId": charaId,
        "live2dId": "00",
        "live2d": {
            "charaId": charaId,
            "live2dId": "00",
            "description": "Magical Girl",
            "defaultOpened": True,
            "voicePrefixNo": "00"
        },
        "createdAt": nowstr
    }
    return userCard, userChara, userLive2d

def createUserMemoria(pieceId):
    piece = dataUtil.masterPieces[pieceId]
    foundExisting = pieceId in dataUtil.userIndices['userPieceList']

    userPieceId = str(uuid1())
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    userPiece = {
        "id": userPieceId,
        "userId": dataUtil.userId,
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
        "createdAt": nowstr
    }
    dataUtil.setUserObject('userPieceList', userPieceId, userPiece)
    return userPiece, foundExisting

def createUserGachaGroup(groupId):
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    return {
        "userId": dataUtil.userId,
        "gachaGroupId": groupId,
        "count": 0,
        "paid": 0,
        "totalCount": 0,
        "dailyCount": 0,
        "weeklyCount": 0,
        "monthlyCount": 0,
        "currentScheduleId": 20,
        "resetCount": 0,
        "createdAt": nowstr
    }