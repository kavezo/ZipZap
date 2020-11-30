from datetime import datetime
import logging

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr

logger = logging.getLogger('app.storyUtil')
questBattles = dt.readJson('data/questBattleList.json')

# TODO: need to fix for branch quests like chapter 9
sectionBattles = {s: [b['questBattleId'] for b in questBattles if b['sectionId']==s]
                    for s in dt.masterSections.keys()}
nextSection = {sorted(battles)[-1]: (sectionId+1) if sectionId+1 in dt.masterSections.keys() else None
                    for sectionId, battles in sectionBattles.items()}

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
    else:
        nextChapter[chapterBattles[-1]['questBattleId']] = None

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
            userLive2dList = dt.readJson('data/user/userLive2dList.json')
            dt.saveJson('data/user/userLive2dList.json', userLive2dList + [newLive2d])
        args['userLive2dList'] = args.get('userLive2dList', []) + [newLive2d]
    elif presentType == 'PIECE':
        args['userPieceList'] = args.get('userPieceList', [])
        for _ in range(quantity):
            newPiece = newtil.createUserMemoria(clearReward['genericId'])
            args['userPieceList'].append(newPiece)
            dt.setUserObject('userPieceList', newPiece['id'], newPiece)
    return args

def startNewSection(newSectionId, response, canStart=True):
    newSection, exists = newtil.createUserSection(newSectionId)
    if not exists:
        response['userSectionList'] = response.get('userSectionList', []) + [newSection]
        dt.setUserObject('userSectionList', newSectionId, newSection)
        # open enemies
        openEnemyList = newSection['section']['openEnemyList']
        for enemy in openEnemyList:
            newEnemy, exists = newtil.createUserEnemy(enemy['enemyId'])
            if not exists: dt.setUserObject('userEnemyList', enemy['enemyId'], newEnemy)
    else:
        existingSection = dt.getUserObject('userSectionList', newSectionId)
        existingSection['canPlay'] = canStart
        dt.setUserObject('userSectionList', newSectionId, existingSection)
        response['userSectionList'] = response.get('userSectionList', []) + [existingSection]

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

    canStart = True # only for the first one
    for sectionId in sorted(chapterSections[newChapterId], key=lambda x: x['sectionId']):
        startNewSection(sectionId, response, canStart)
        canStart = False

def progressStory(battle):
    logger.info('progressing story')
    battleId = battle['questBattleId']
    response = {}
    if battleId in nextChapter:
        clearedChapterId = int(str(battle['questBattleId'])[2:4])
        clearedChapter = dt.getUserObject('userChapterList', clearedChapterId)
        clearedChapter['cleared'] = True
        clearedChapter['clearedAt'] = nowstr()

        if nextChapter[battleId] is not None:
            logger.info('battleId in nextChapter')
            startNewChapter(nextChapter[battleId], response)
        
        response['userChapterList'] = response.get('userChapterList', []) + [clearedChapter]
        dt.setUserObject('userChapterList', clearedChapterId, clearedChapter)

    if battleId in nextSection:
        clearedSectionId = battle['questBattle']['sectionId']
        clearedSection = dt.getUserObject('userSectionList', clearedSectionId)
        clearedSection['cleared'] = True
        clearedSection['clearedAt'] = nowstr()

        response = obtainReward(clearedSection['section']['clearReward'], response)
    
        if nextSection[battleId] is not None:
            logger.info('battleId in nextSection')
            startNewSection(nextSection[battleId], response)           
            
        response['userSectionList'] = response.get('userSectionList', []) + [clearedSection]
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

