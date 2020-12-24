import flask
import math
import numpy as np
import logging

from util import dataUtil as dt

logger = logging.getLogger('data/userPiece')

expByLevel = [0, 100, 210, 330, 460, 600, 760, 950, 1180, 1460, 1800, 2210, 2690, 3240, 3860, 4550, 5310, 6140, 7040, 8010, 9050, 10160, 11340, 12590, 13910, 15300, 16760, 18290, 19890, 21560, 23300, 25110, 26990, 28940, 30960, 33050, 35210, 37440, 39740, 42110, 44550, 47060, 49640, 52290, 55010, 57800, 60660, 63590, 66590, 69660]
dExpdLevel = [0] + [b-a for a,b in zip(expByLevel[:-1], expByLevel[1:])]

def getComposeExp(memoriaToSpend):
    rankExp = [100, 200, 500, 1E3]
    totalExp = 0

    for mem in memoriaToSpend:
        rank = int(mem['piece']['rank'][-1])-1
        totalExp += rankExp[rank] + (mem['experience'] + expByLevel[mem['level'] - 1]) / 10

    return totalExp

multByRank = {
    'RANK_1': [1, 1, 1.05, 1.11, 1.16, 1.22, 1.27, 1.33, 1.38, 1.44, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 
                2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5],
    'RANK_2': [1, 1, 1.03, 1.07, 1.1, 1.14, 1.17, 1.21, 1.25, 1.28, 1.32, 1.35, 1.39, 1.42, 1.46, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 
                1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5],
    'RANK_3': [1, 1, 1.02, 1.05, 1.07, 1.1, 1.13, 1.15, 1.18, 1.21, 1.23, 1.26, 1.28, 1.31, 1.34, 1.36, 1.39, 1.42, 1.44, 1.47, 
                1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5],
    'RANK_4': [1, 1, 1.01, 1.03, 1.05, 1.06, 1.08, 1.1, 1.12, 1.13, 1.15, 1.17, 1.18, 1.2, 1.22, 1.24, 1.25, 1.27, 1.29, 1.31, 
                1.32, 1.34, 1.36, 1.37, 1.39, 1.41, 1.43, 1.44, 1.46, 1.48, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 
                2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5]
}
def getStats(userPiece, level):
    attack = userPiece['piece']['attack'] if 'attack' in userPiece['piece'] else 0
    defense = userPiece['piece']['defense'] if 'defense' in userPiece['piece'] else 0
    hp = userPiece['piece']['hp'] if 'hp' in userPiece['piece'] else 0

    multipliers = multByRank[userPiece['piece']['rank']]
    stats = {'hp': math.floor(hp * multipliers[level]),
             'attack': math.floor(attack * multipliers[level]),
             'defense': math.floor(defense * multipliers[level])}
    return stats

priceArr = [100, 300, 1E3, 5E3, 2E3]
def priceCalc(rank, lbNum):
    return priceArr[int(rank.split("_")[-1])-1] * (min(lbNum, 4)+1)

maxLvlByRank = {"RANK_1": 10, "RANK_2": 15, "RANK_3": 20, "RANK_4": 30, "RANK_5": 50}

def getMaxLevel(rank, lbNum):
    return maxLvlByRank.get(rank, 30) + 5 * min(lbNum, 4)

def levelUp(targetUserPiece, memoriaToSpend):
    # figure out success type
    # (totally BS rates but whatevs)
    success = np.random.choice([1, 1.5, 2], p=[0.9, 0.08, 0.02])

    # modify meme's level and stats
    origLevel = targetUserPiece['level']
    rank = targetUserPiece['piece']['rank']
    finalExp = expByLevel[origLevel-1] + targetUserPiece['experience'] \
               + getComposeExp(memoriaToSpend) * success
    newLevel = 1
    extraExp = 0
    for i in range(len(expByLevel)-1, 0, -1): # maybe implement a binary rather than a linear search?
        if expByLevel[i] <= finalExp:
            newLevel = i+1
            extraExp = finalExp - expByLevel[i]
            break

    if newLevel >= getMaxLevel(rank, targetUserPiece['lbCount']):
        newLevel = getMaxLevel(rank, targetUserPiece['lbCount'])
        extraExp = 0

    stats = getStats(targetUserPiece, newLevel)
    stats['level'] = newLevel
    stats['experience'] = extraExp

    for key in stats.keys():
        targetUserPiece[key] = stats[key]

    return targetUserPiece, success

def compose():
    body = flask.request.json
    targetUserPieceId = body['baseUserPieceId']
    targetUserPiece = dt.getUserObject('userPieceList', targetUserPieceId)
    memoriaToSpend = []
    
    for materialPieceId in body['materialUserPieceIdList']:
        memoriaToSpend.append(dt.getUserObject('userPieceList', materialPieceId))

    if targetUserPiece == {}:
        flask.abort(400, description='Tried to level up a memoria you don\'t have...')

    # limit break
    isLimitBreak = False
    for memoria in memoriaToSpend:
        if memoria['pieceId'] == targetUserPiece['pieceId'] or \
        ('pieceKind' in memoria['piece'] and memoria['piece']['pieceKind']=='LIMIT_BREAK'):
            isLimitBreak = True
    if isLimitBreak:
        targetUserPiece['lbCount'] += len(memoriaToSpend)

    originalUserPiece = {k: v for k, v in targetUserPiece.items()}
    targetUserPiece, success = levelUp(targetUserPiece, memoriaToSpend)

    dt.setUserObject('userPieceList', targetUserPieceId, targetUserPiece)

    # modify CC
    totalCC = 0
    for memoria in memoriaToSpend:
        totalCC += priceCalc(memoria['piece']['rank'], memoria['lbCount'])
        dt.deleteUserObject('userPieceList', memoria['id'])

    currCC = dt.getGameUserValue('riche')
    if currCC < totalCC:
        raise ValueError("Tried to use more cc than you have...")
    gameUser = dt.setGameUserValue('riche', currCC-totalCC)

    # It looks like the archive ignores this information and shows everything max leveld and mlb'd...
    # with open('data/user/userPieceCollectionList.json', encoding='utf-8') as f:
    #     pieceCollection = json.load(f)
    # for i, piece in enumerate(pieceCollection):
    #     if piece['pieceId'] == targetUserPiece['pieceId']:
    #         if targetUserPiece['level'] > piece['maxLevel']:
    #             pieceCollection[i]['maxLevel'] = targetUserPiece['level']
    #         if targetUserPiece['lbCount'] > piece['maxLbCount']:
    #             pieceCollection[i]['maxLbCount'] = targetUserPiece['lbCount']
    # with open('data/user/userPieceCollectionList.json', 'w+', encoding='utf-8') as f:
    #     json.dump(pieceCollection, f, ensure_ascii=False)

    response = {
        'resultCode': 'success',
        'gameUser': gameUser,
        'userPieceList': [targetUserPiece],
        "memoria": {
            "materialList": [memoria['pieceId'] for memoria in memoriaToSpend],
            "memoriaId": targetUserPiece['pieceId'],
            "status": {
                "current": {
                    "atk": originalUserPiece['piece']['attack'],
                    "def": originalUserPiece['piece']['defense'],
                    "gainedExp": originalUserPiece['experience'],
                    "hp": originalUserPiece['piece']['hp'],
                    "lbCount": originalUserPiece['lbCount'],
                    "level": originalUserPiece['level'],
                    "limitExp": dExpdLevel[originalUserPiece['level']-1],
                    "limitLevel": getMaxLevel(originalUserPiece['piece']['rank'], originalUserPiece['lbCount']),
                    "rarity": int(originalUserPiece['piece']['rank'][-1])
                },
                "result": {
                    "atk": targetUserPiece['piece']['attack'],
                    "def": targetUserPiece['piece']['defense'],
                    "gainedExp": targetUserPiece['experience'],
                    "hp": targetUserPiece['piece']['hp'],
                    "lbCount": targetUserPiece['lbCount'],
                    "level": targetUserPiece['level'],
                    "limitExp": dExpdLevel[targetUserPiece['level']-1],
                    "limitLevel": getMaxLevel(targetUserPiece['piece']['rank'], targetUserPiece['lbCount']),
                    "rarity": int(targetUserPiece['piece']['rank'][-1])
                }
            },
            "successType": success
        }
    }
    return flask.jsonify(response)

def setProtect(isProtected):
    body = flask.request.json
    userPiece = dt.getUserObject('userPieceList', body['userPieceId'])
    userPiece['protect'] = isProtected
    dt.setUserObject('userPieceList', body['userPieceId'], userPiece)
    response = {
        'resultCode': 'success',
        'userPieceList': [userPiece]
    }
    return flask.jsonify(response)

def setArchive(isArchive):
    body = flask.request.json
    
    resultUserPieceList = []
    for pieceId in body['archiveUserPieceIdList']:
        targetUserPiece = dt.getUserObject('userPieceList', pieceId)
        if targetUserPiece is None:
            flask.abort(400, description='Tried to ' + ('' if isArchive else 'un') +
                                                                        'archive a memoria you don\'t have...')

        targetUserPiece['archive'] = isArchive
        dt.setUserObject('userPieceList', pieceId, targetUserPiece)
        resultUserPieceList.append(targetUserPiece)

    response = {
        'resultCode': 'success',
        'userPieceList': resultUserPieceList
    }
    return flask.jsonify(response)

def sale():
    body = flask.request.json
    totalCC = 0
    for userPieceId in body['saleUserPieceIdList']:
        soldMemoria = dt.getUserObject('userPieceList', userPieceId)
        totalCC += priceCalc(soldMemoria['piece']['rank'], soldMemoria['lbCount'])
        dt.deleteUserObject('userPieceList', soldMemoria['id'])
    
    gameUser = dt.setGameUserValue('riche', dt.getGameUserValue('riche')+totalCC)
    response = {
        'resultCode': 'success',
        'gameUser': gameUser
    }
    return flask.jsonify(response)

def handleUserPiece(endpoint):
    if endpoint.endswith('compose'):
        return compose()
    elif endpoint.endswith('unarchive'):
        return setArchive(False)
    elif endpoint.endswith('archive'):
        return setArchive(True)
    elif endpoint.endswith('unprotect'):
        return setProtect(False)
    elif endpoint.endswith('protect'):
        return setProtect(True)
    elif endpoint.endswith('sale'):
        return sale()
    else:
        logging.error('Missing implementation: userPiece/'+endpoint)
        flask.abort(501, description="Not implemented")
