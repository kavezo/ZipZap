import json
from datetime import datetime
import os
import shutil

def createDefaultUser():
    if not os.path.exists('data/user'):
        print('Copying over default user...') # logging isn't set up yet, and also it's not too important to have in logs
        shutil.copytree('data/default_user', 'data/user')

def addAllDailies():
    with open('data/dailyChallengeList.json', encoding='utf-8') as f:
        challenges = json.load(f)
    with open('data/user/userDailyChallengeList.json', encoding='utf-8') as f:
        userChallenges = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    
    userChallengeIds = {userChallenge['challengeId'] for userChallenge in userChallenges}
    missingChallenges = [challenge for challenge in challenges if not challenge['id'] in userChallengeIds]
    userChallenges += [{
        'userId': userId,
        'challengeId': challenge['id'],
        'challenge': challenge,
        'clearedCount': 0,
        'receivedAt': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        'update': False
    } for challenge in missingChallenges]

    with open('data/user/userDailyChallengeList.json', 'w+', encoding='utf-8') as f:
        json.dump(userChallenges, f, ensure_ascii=False)

def addToShopItemList(dt): # passing in dataUtil as a hacky workaround for how this module has to import before logging
    userShopItemList = dt.readJson('data/user/userShopItemList.json')
    nowstr = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    shopItemIds = set([item['shopItemId'] for item in userShopItemList])
    
    backgrounds = {'HOME_EV_1003_21028': 381, 'HOME_MAP_11011': 1720, 'HOME_MAP_11012': 1721, 
                    'HOME_MAP_11013': 1722, 'HOME_EV_1033_13101': 2388}
    addBackgrounds = [itemId for itemId in backgrounds.keys() 
                        if dt.getUserObject('userItemList', itemId) is not None
                        and backgrounds[itemId] not in shopItemIds]
    for itemId in addBackgrounds:
        dt.setUserObject('userShopItemList', backgrounds[itemId], {
            "createdAt": nowstr,
            "num": 1,
            "shopItemId": backgrounds[itemId],
            "userId": dt.userId
        })

    formations = {911: 999431, 912: 999432, 913: 999433, 921: 999434, 922: 999435, 923: 999436, 
                131: 5, 141: 424, 151: 425, 161: 426, 171: 427, 181: 428, 711: 999428, 611: 999430}
    addFormations = [itemId for itemId in formations.keys() 
                        if dt.getUserObject('userFormationSheetList', itemId) is not None
                        and formations[itemId] not in shopItemIds]
    for itemId in addFormations:
        dt.setUserObject('userShopItemList', formations[itemId], {
            "createdAt": nowstr,
            "num": 1,
            "shopItemId": formations[itemId],
            "userId": dt.userId
        })

def fixQuestAdventures():
    with open('data/user/userQuestAdventureList.json', encoding='utf-8') as f:
        adventures = json.load(f)
    with open('data/user/userQuestBattleList.json', encoding='utf-8') as f:
        userBattles = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']

    adventuresIdx = {adventure['adventureId']: adventure for adventure in adventures}
    def makeAdventure(adventureId): 
        return {
            "userId": userId,
            "adventureId": adventureId,
            "skipped": False,
            "createdAt": "2020/01/01 00:00:00"
        }
    
    for userBattle in userBattles:
        battle = userBattle['questBattle']
        # add cleared adventure if it doesn't exist
        if 'cleared' in userBattle and userBattle['cleared']:
            if 'startStory' in battle and battle['startStory'] not in adventuresIdx:
                adventuresIdx[battle['startStory']] = makeAdventure(battle['startStory'])
            if 'questStory' in battle and battle['questStory'] not in adventuresIdx:
                adventuresIdx[battle['questStory']] = makeAdventure(battle['questStory'])
            if 'endStory' in battle and battle['endStory'] not in adventuresIdx:
                adventuresIdx[battle['endStory']] = makeAdventure(battle['endStory'])

        # get rid of extra adventures
        else:
            if 'startStory' in battle and battle['startStory'] in adventuresIdx:
                del adventuresIdx[battle['startStory']]
            if 'questStory' in battle and battle['questStory'] in adventuresIdx:
                del adventuresIdx[battle['questStory']]
            if 'endStory' in battle and battle['endStory'] in adventuresIdx:
                del adventuresIdx[battle['endStory']]

    with open('data/user/userQuestAdventureList.json', 'w+', encoding='utf-8') as f:
        json.dump(list(adventuresIdx.values()), f, ensure_ascii=False)

def resetShop(dt):
    # some gross resused code from homuUtil, but tbh they're not that compatible anywayas
    skipTypes = ['PIECE', 'MAXPIECE', 'FORMATION_SHEET', 'CARD']
    shopList = dt.readJson('data/shopList.json')
    DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
    today = datetime.today

    for shopIdx in range(4): # magia chips, mirrors coins, support pts, daily coins
        shopItems = shopList[shopIdx]['shopItemList']
        for item in shopItems:
            if 'endAt' in item and not item['shopItemType'] in skipTypes:
                itemEnd = datetime.strptime(item['endAt'], DATE_FORMAT)
                dt.deleteUserObject('userShopItemList', item['id'])