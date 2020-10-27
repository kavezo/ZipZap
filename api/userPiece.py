from mitmproxy import http
import json
import math
import numpy as np

# stolen from MemoriaUtil.js
exArr = [0, 100, 210, 330, 460, 600, 760, 950, 1180, 1460, 1800, 2210, 2690, 3240, 3860, 4550, 5310, 6140, 7040, 8010, 9050, 10160, 11340, 12590, 13910, 15300, 16760, 18290, 19890, 21560, 23300, 25110, 26990, 28940, 30960, 33050, 35210, 37440, 39740, 42110, 44550, 47060, 49640, 52290, 55010, 57800, 60660, 63590, 66590, 69660]
parExArr = [0, 100, 110, 120, 130, 140, 160, 190, 230, 280, 340, 410, 480, 550, 620, 690, 760, 830, 900, 970, 1040,
              1110, 1180, 1250, 1320, 1390, 1460, 1530, 1600, 1670, 1740, 1810, 1880, 1950, 2020, 2090, 2160, 2230, 2300, 2370, 2440, 2510, 2580, 2650, 2720, 2790, 2860, 2930, 3E3, 3070
              ]
def getComposeExp(memoriaToSpend):
    rankExp = [100, 200, 500, 1E3]
    totalExp = 0

    for mem in memoriaToSpend:
        rank = int(mem['piece']['rank'][-1])-1
        totalExp += rankExp[rank] + (mem['experience'] + exArr[mem['level'] - 1]) / 10

    return totalExp

m = [1, 1, 1.05, 1.11, 1.16, 1.22, 1.27, 1.33, 1.38, 1.44, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5]
n = [1, 1, 1.03, 1.07, 1.1, 1.14, 1.17, 1.21, 1.25, 1.28, 1.32, 1.35, 1.39, 1.42, 1.46, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5]
p = [1, 1, 1.02, 1.05, 1.07, 1.1, 1.13, 1.15, 1.18, 1.21, 1.23, 1.26, 1.28, 1.31, 1.34, 1.36, 1.39, 1.42, 1.44, 1.47, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05,
     2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5]
q = [1, 1, 1.01, 1.03, 1.05, 1.06, 1.08, 1.1, 1.12, 1.13, 1.15, 1.17, 1.18, 1.2, 1.22, 1.24, 1.25, 1.27, 1.29, 1.31, 1.32, 1.34, 1.36, 1.37, 1.39, 1.41, 1.43, 1.44, 1.46, 1.48, 1.5, 1.55, 1.6, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2, 2.05, 2.1, 2.15, 2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5]
def getStats(userPiece, level):
    attack = userPiece['piece']['attack'] if 'attack' in userPiece['piece'] else 0
    defense = userPiece['piece']['defense'] if 'defense' in userPiece['piece'] else 0
    multipliers = [m, n, p, q][int(userPiece['piece']['rank'][-1]) - 1]
    stats = {'hp': math.floor((userPiece['piece']['hp'] if 'hp' in userPiece['piece'] else 0) * multipliers[level]),
             'attack': math.floor(attack * multipliers[level]),
             'defense': math.floor(defense * multipliers[level])}
    return stats

priceArr = [0, 100, 300, 1E3, 5E3, 2E3]
def priceCalc(a, e):
    a = a.split("_")[-1]
    if e>4: e = 4
    return priceArr[int(a)] * (e + 1)

l = {"RANK_1": 10, "RANK_2": 15, "RANK_3": 20, "RANK_4": 30, "RANK_5": 50}

def getMaxLevel(a, e):
    e = 4 if 4 < e else e
    a = l.get(a, 30) + 5 * e
    if 50 < a: a = 50
    return a

def levelUp(targetUserPiece, memoriaToSpend):
    # figure out success type
    # (totally BS rates but whatevs)
    success = np.random.choice([1, 1.5, 2], p=[0.9, 0.08, 0.02])

    # modify meme's level and stats
    origLevel = targetUserPiece['level']
    rank = targetUserPiece['piece']['rank']
    finalExp = exArr[origLevel-1] + targetUserPiece['experience'] \
               + getComposeExp(memoriaToSpend) * success
    newLevel = 1
    extraExp = 0
    for i in range(len(exArr)-1, 0, -1): # maybe implement a binary rather than a linear search?
        if exArr[i] <= finalExp:
            newLevel = i+1
            extraExp = finalExp - exArr[i]
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

def compose(flow):
    body = json.loads(flow.request.text)
    targetUserPieceId = body['baseUserPieceId']

    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        userPieceList = json.load(f)

    targetUserPiece = {}
    targetUserPieceIdx = None
    memoriaToSpend = []
    removeUserPieceIdxs = []
    for i, userPiece in enumerate(userPieceList):
        if userPiece['id'] == targetUserPieceId:
            targetUserPiece = userPiece
            targetUserPieceIdx = i
        for materialPieceId in body['materialUserPieceIdList']:
            if userPiece['id'] == materialPieceId:
                memoriaToSpend.append(userPiece)
                removeUserPieceIdxs.append(i)

    if targetUserPiece == {}:
        flow.response = http.HTTPResponse.make(400, 'Tried to level up a memoria you don\'t have...', {})
        return

    originalUserPiece = {k: v for k, v in targetUserPiece.items()}
    targetUserPiece, success = levelUp(targetUserPiece, memoriaToSpend)

    # limit break
    isLimitBreak = False
    for memoria in memoriaToSpend:
        if memoria['pieceId'] == targetUserPiece['pieceId'] or \
        ('pieceKind' in userPiece['piece'] and userPiece['piece']['pieceKind']=='LIMIT_BREAK'):
            isLimitBreak = True
    if isLimitBreak:
        targetUserPiece['lbCount'] += len(memoriaToSpend)

    userPieceList[targetUserPieceIdx] = targetUserPiece

    # modify CC
    totalCC = 0
    for i in reversed(removeUserPieceIdxs):
        totalCC += priceCalc(userPieceList[i]['piece']['rank'], userPieceList[i]['lbCount'])
        del userPieceList[i]

    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    gameUser['riche'] -= totalCC
    if gameUser['riche'] < 0:
        raise ValueError("Tried to use more cc than you have...")

    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        json.dump(gameUser, f, ensure_ascii=False)

    # save meme info
    with open('data/user/userPieceList.json', 'w+', encoding='utf-8') as f:
        json.dump(userPieceList, f, ensure_ascii=False)

    with open('data/user/userPieceCollectionList.json', encoding='utf-8') as f:
        pieceCollection = json.load(f)
    for i, piece in enumerate(pieceCollection):
        if piece['pieceId'] == targetUserPiece['pieceId']:
            if targetUserPiece['level'] > piece['maxLevel']:
                pieceCollection[i]['maxLevel'] = targetUserPiece['level']
            if targetUserPiece['lbCount'] > piece['maxLbCount']:
                pieceCollection[i]['maxLbCount'] = targetUserPiece['lbCount']
    with open('data/user/userPieceCollectionList.json', 'w+', encoding='utf-8') as f:
        json.dump(pieceCollection, f, ensure_ascii=False)

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
                    "limitExp": parExArr[originalUserPiece['level']],
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
                    "limitExp": parExArr[targetUserPiece['level']],
                    "limitLevel": getMaxLevel(targetUserPiece['piece']['rank'], targetUserPiece['lbCount']),
                    "rarity": int(targetUserPiece['piece']['rank'][-1])
                }
            },
            "successType": success
        }
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})

def setArchive(flow, isArchive):
    body = json.loads(flow.request.text)

    with open('data/user/userPieceList.json', encoding='utf-8') as f:
        userPieceList = json.load(f)

    targetUserPiece = {}
    targetUserPieceIdx = 0
    for i, userPiece in enumerate(userPieceList):
        if userPiece['id'] == body['archiveUserPieceIdList'][0]:
            targetUserPiece = userPiece
            targetUserPieceIdx = i

    if targetUserPiece == {}:
        flow.response = http.HTTPResponse.make(400, 'Tried to ' + ('' if isArchive else 'un') +
                                                                    'archive a memoria you don\'t have...', {})
        return

    targetUserPiece['archive'] = isArchive
    userPieceList[targetUserPieceIdx] = targetUserPiece
    with open('data/user/userPieceList.json', 'w+', encoding='utf-8') as f:
        json.dump(userPieceList, f, ensure_ascii=False)

    response = {
        'resultCode': 'success',
        'userPieceList': [targetUserPiece]
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {})

def handleUserPiece(flow):
    endpoint = flow.request.path.replace('/magica/api/userPiece', '')
    if endpoint.endswith('/compose'):
        compose(flow)
    elif endpoint.endswith('/archive'):
        setArchive(flow, True)
    elif endpoint.endswith('/unarchive'):
        setArchive(flow, False)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})
