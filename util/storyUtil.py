from datetime import datetime

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr

questBattles = dt.readJson('data/questBattleList.json')

# TODO: need to fix for branch quests like chapter 9
nextSection = {sorted([b['questBattleId'] for b in questBattles if b['sectionId']==s])[-1]: s+1
                    for s in dt.masterSections.keys() if s+1 in dt.masterSections.keys()}
sectionBattles = {s: [b['questBattleId'] for b in questBattles if b['sectionId']==s]
                    for s in dt.masterSections.keys()}

nextChapter = {}
chapterSections = {}
for chapterId in dt.masterChapters.keys():
    chapterBattles = []
    for battle in questBattles:
        strBattleId = str(battle['questBattleId'])
        battleChapter = int(strBattleId[2:4])
        if (strBattleId.startswith('1') or strBattleId.startswith('2')) \
            and battleChapter == chapterId:
            chapterBattles.append(battle)
    chapterBattles = sorted(chapterBattles, key=lambda x: x['questBattleId'])
    chapterSections[chapterId] = list({battle['sectionId'] for battle in chapterBattles})
    if chapterId + 1 in dt.masterChapters.keys():
        nextChapter[chapterBattles[-1]['questBattleId']] = chapterId + 1

def obtainReward(clearReward, args):
    presentType = clearReward['presentType']
    quantity = clearReward['quantity']
    if presentType == 'DOPPEL':
        userDoppel, exists = newtil.createUserDoppel(clearReward['genericId'])
        if not exists: dt.setUserObject('userDoppelList', clearReward['genericId'], userDoppel)
    elif presentType == 'GEM': # only Iroha's gems are rewards, so no need to check missing chara
        userChara = dt.getUserObject('userCharaList', clearReward['genericId'])
        userChara['lbItemNum'] += quantity
        dt.setUserObject('userCharaList', clearReward['genericId'], userChara)
    elif presentType == 'ITEM':
        userItem = dt.getUserObject('userItemList', clearReward['itemId'])
        userItem['quantity'] += quantity
        dt.setUserObject('userItemList', clearReward['itemId'], userItem)
    elif presentType == 'LIVE2D':
        newLive2d, exists = newtil.createUserLive2d(clearReward['genericId'], 
                                                clearReward['genericCode'], clearReward['displayName'])
        if not exists:
            userLive2dList = dt.readJson('data/user/userLive2dList')
            dt.saveJson('data/user/userLive2dList', userLive2dList + [newLive2d])
        args['userLive2dList'] = args.get('userLive2dList', []) + [newLive2d]
    elif presentType == 'PIECE':
        args['userPieceList'] = args.get('userPieceList', [])
        for _ in range(quantity):
            newPiece = newtil.createUserMemoria(clearReward)
            args['userPieceList'].append(newPiece)
            dt.setUserObject('userPieceList', newPiece['id'], newPiece)
    return args

def startNewSection(newSectionId, response):
    newSection, exists = newtil.createUserSection(newSectionId)
    if not exists:
        response['userSectionList'] = response.get('userSectionList', []) + [newSection]
        dt.setUserObject('userSectionList', newSectionId, newSection)

    for newBattleId in sectionBattles[newSectionId]:
        newBattle, exists = newtil.createUserQuestBattle(newBattleId)
        if not exists:
            response['userQuestBattleList'] = response.get('userQuestBattleList', []) + [newBattle]
            dt.setUserObject('userQuestBattleList', newBattleId, newBattle)

def startNewChapter(newChapterId, response):
    newChapter, exists = newtil.createUserChapter(newChapterId)
    if not exists:
        response['userChapterList'] = response.get('userChapterList', []) + [newChapter]
        dt.setUserObject('userChapterList', newChapterId, newChapter)

    for sectionId in chapterSections[newChapterId]:
        startNewSection(sectionId, response)

# TODO: integrate this and see if it works
def progressStory(battle):
    battleId = battle['questBattleId']
    response = {}
    if battleId in nextChapter:
        startNewChapter(nextChapter[battleId], response)

        clearedChapterId = int(str(battle['questBattleId'])[2:4])
        clearedChapter = dt.getUserObject('userChapterList', clearedChapterId)
        clearedChapter['cleared'] = True
        clearedChapter['clearedAt'] = nowstr()
        response['userChapterList'].append(clearedChapter)
        dt.setUserObject('userChapterList', clearedChapterId, clearedChapter)

    if battleId in nextSection:
        startNewSection(nextSection[battleId], response)

        clearedSectionId = battle['questBattle']['sectionId']
        clearedSection = dt.getUserObject('userSectionList', clearedSectionId)
        clearedSection['cleared'] = True
        clearedSection['clearedAt'] = nowstr()
        obtainReward(clearedSection['clearReward'], response)
        response['userSectionList'].append(clearedSection)
        dt.setUserObject('userSectionList', clearedSectionId, clearedSection)

    if battleId+1 in dt.masterBattles:
        newBattle, exists = newtil.createUserQuestBattle(battleId+1)
        if not exists:
            response['userQuestBattleList'] = response.get('userQuestBattleList', []) + [newBattle]
            dt.setUserObject('userQuestBattleList', battleId+1, newBattle)

    return response

def clearBattle(battle):
    userBattle = dt.getUserObject('userQuestBattleList', battle['questBattleId'])
    if userBattle is None: return None

    now = nowstr()
    userBattle['cleared'] = True
    if 'firstClearedAt' not in userBattle:
        userBattle['firstClearedAt'] = now
    userBattle['lastClearedAt'] = now
    userBattle['clearCount'] = userBattle.get('clearCount', 0) + 1

    dt.setUserObject('userQuestBattleList', battle['questBattleId'], userBattle)
    return userBattle

