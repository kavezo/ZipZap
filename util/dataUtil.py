import json

ITEM_VALFUNC = lambda i, x: x
INDEX_VALFUNC = lambda i, x: i

def idxFunc(idx):
    return lambda x: x[idx]

# some nice abstractions
def readJson(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def saveJson(path, data):
    with open(path, 'w+', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

# Only used with list files
def createIndex(jsonpath, idFunc=idxFunc('id'), valFunc=INDEX_VALFUNC):
    return createIndexFromList(readJson(jsonpath), idFunc, valFunc)

def createIndexFromList(xs, idFunc=idxFunc('id'), valFunc=INDEX_VALFUNC):
    return {idFunc(x): valFunc(i, x) for i, x in enumerate(xs)}

masterCards = createIndex('data/cards.json', idxFunc('charaId'), ITEM_VALFUNC)
masterPieces = createIndex('data/pieces.json', idxFunc('pieceId'), ITEM_VALFUNC)
masterSections = createIndex('data/sectionList.json', idxFunc('sectionId'), ITEM_VALFUNC)
masterChapters = createIndex('data/chapterList.json', idxFunc('chapterId'), ITEM_VALFUNC)
masterItems = createIndex('data/itemList.json', idxFunc('itemCode'), ITEM_VALFUNC)
masterGifts = createIndex('data/giftList.json', valFunc=ITEM_VALFUNC)
masterFormations = createIndex('data/formationSheetList.json', valFunc=ITEM_VALFUNC)

userIndices = {
    'userCardList': createIndex('data/user/userCardList.json'),
    'userChapterList': createIndex('data/user/userChapterList.json', idxFunc('chapterId')),
    'userCharaList': createIndex('data/user/userCharaList.json', idxFunc('charaId')),
    'userDeckList': createIndex('data/user/userDeckList.json', idxFunc('deckType')),
    'userDoppelList': createIndex('data/user/userDoppelList.json', idxFunc('doppelId')),
    'userFollowList': createIndex('data/user/userFollowList.json', idxFunc('followUserId')),
    'userFormationSheetList': createIndex('data/user/userFormationSheetList.json', idxFunc('formationSheetId')),
    'userGachaGroupList': createIndex('data/user/userGachaGroupList.json', idxFunc('gachaGroupId')),
    'gachaHistoryList': createIndex('data/user/gachaHistoryList.json'),
    'userGiftList': createIndex('data/user/userGiftList.json', idxFunc('giftId')),
    'userItemList': createIndex('data/user/userItemList.json', idxFunc('itemId')),
    'userLimitedChallengeList': createIndex('data/user/userLimitedChallengeList.json', idxFunc('challengeId')),
    'userLive2dList': createIndex('data/user/userLimitedChallengeList.json', 
                lambda x: int(str(x['charaId'])+x['live2dId']), 
                valFunc=ITEM_VALFUNC),
    'userPieceList': createIndex('data/user/userPieceList.json'),
    'userPieceCollectionList': createIndex('data/user/userPieceCollectionList.json', idxFunc('pieceId')),
    'userPieceSetList': createIndex('data/user/userPieceSetList.json', idxFunc('setNum')),
    'userQuestAdventureList': createIndex('data/user/userQuestAdventureList.json', idxFunc('adventureId')),
    'userQuestBattleList': createIndex('data/user/userQuestBattleList.json', idxFunc('questBattleId')),
    'userSectionList': createIndex('data/user/userSectionList.json', idxFunc('sectionId')),
    'userShopList': createIndex('data/user/userShopItemList.json', idxFunc('shopId')),
    # [{itemId: index}, {itemId: index}]
    'userShopItems': [createIndexFromList(shop['shopList']) for shop in createIndex('data/user/userShopItemList.json', idxFunc('shopId'), ITEM_VALFUNC)],
    'userStatusList': createIndex('data/user/userStatusList.json', idxFunc('statusId')),
    'userTotalChallengeList': createIndex('data/user/userTotalChallengeList.json', idxFunc('challengeId'))
}

# Doesn't work for userShopItemList, but we're having separate cases for that anyways
userPaths = {key: 'data/user/'+key+'.json' for key in userIndices.keys()}

def deleteUserObject(listName, objectId):
    path = userPaths[listName]
    data = readJson(path)

    if not objectId in userIndices[listName]:
        return data
    
    idx = userIndices[listName][objectId]
    del userIndices[listName][objectId]
    del data[idx]

    saveJson(path, data)
    return data

def getUserObject(listName, objectId):
    if not objectId in userIndices[listName]:
        return None

    idx = userIndices[listName][objectId]
    data = readJson(userPaths[listName])
    return data[idx]

def getUserShopItem(shopId, itemId):
    if not shopId in userIndices['userShopList']:
        return None
    shopIdx = userIndices['userShopList'][shopId]

    if not itemId in userIndices['userShopItems'][shopIdx]:
        return None
    itemIdx = userIndices['userShopItems'][shopIdx][itemId]

    data = readJson('data/user/userShopItemList.json')
    return data[shopIdx][itemIdx]

# Doesn't work for userLive2dList...we have to just avoid setting it using this
def setUserObject(listName, objectId, objectData):
    path = userPaths[listName]
    data = readJson(path)

    if objectId in userIndices[listName]:
        idx = userIndices[listName][objectId]
        data[idx] = objectData
    else:
        userIndices[listName][objectId] = len(data)
        data.append(objectData)

    saveJson(path, data)
    return data

def setUserShopItem(shopId, itemId, itemData, shopData = None):
    path = 'data/user/userShopItemList.json'
    data = readJson(path)

    shopIdToIdx = userIndices['userShopList']
    if not shopId in shopIdToIdx or shopData is not None:
        if shopData is None:
            raise ValueError('Tried to set an item value in a nonexistent shop')
        userIndices['userShopList'][shopId] = len(shopIdToIdx)
        data.append(shopData)

    shopIdx = userIndices['userShopList'][shopId]
    itemIdToIdx = userIndices['userShopItems'][shopIdx]

    if itemId in itemIdToIdx:
        itemIdx = itemIdToIdx[itemId]
        data[shopIdx][itemIdx] = itemData
    else:
        userIndices['userShopItems'][shopIdx][itemId] = len(itemIdToIdx)
        data[shopIdx].append(itemData)

    saveJson(path, data)
    return data

def getGameUserValue(key):
    gameUser = readJson('data/user/gameUser.json')
    if not key in gameUser:
        return None
    return gameUser[key]

def setGameUserValue(key, value):
    gameUser = readJson('data/user/gameUser.json')
    gameUser[key] = value
    saveJson('data/user/gameUser.json', gameUser)
    return gameUser

def getUserValue(key):
    user = readJson('data/user/user.json')
    if not key in user:
        return None
    return user[key]

def setUserValue(key, value):
    user = readJson('data/user/user.json')
    user[key] = value
    saveJson('data/user/user.json', user)
    return user

userId = getUserValue('id')