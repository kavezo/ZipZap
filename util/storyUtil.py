from datetime import datetime
import logging

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr

logger = logging.getLogger('app.storyUtil')
questBattles = dt.readJson('data/questBattleList.json')

# {sectionId: [questBattleId]}
sectionBattles = {s: [b['questBattleId'] for b in questBattles if b['sectionId']==s]
                    for s in dt.masterSections.keys()}
# {sectionId: [challenge questBattleId]}
sectionChallengeBattles = {s: [b for b in bs if len(str(b))==8] for s, bs in sectionBattles.items()}
# {last questBattleId of a section: [next sectionIds]}
nextSection = {}
for sectionId, battles in sectionBattles.items():
    nonChallenge = [battle for battle in battles if len(str(battle))==7]
    if len(nonChallenge) == 0: 
        logger.error('section ' + str(sectionId) + ' has no non-challenge battles')
        continue

    lastBattle = sorted(nonChallenge)[-1]

    # branch quests
    if 'connectPointIds' in dt.masterSections[sectionId]:
        nextSection[lastBattle] = [int(connectPoint) 
            for connectPoint in dt.masterSections[sectionId]['connectPointIds'].split(',')]
    else:
        nextSection[lastBattle] = [sectionId+1] if sectionId+1 in dt.masterSections.keys() else None

nextChapter = {} # {last questBattleId of a chapter: next chapter ID}
chapterSections = {} # {chapterId: [sectionIds]}
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
        args['userDoppelList'] = args.get('userDoppelList', []) + [userDoppel]
    elif presentType == 'GEM': # only Iroha's gems are rewards, so no need to check missing chara
        userChara = dt.getUserObject('userCharaList', clearReward['genericId'])
        userChara['lbItemNum'] += quantity
        dt.setUserObject('userCharaList', clearReward['genericId'], userChara)
        args['userCharaList'] = args.get('userCharaList', []) + [userChara]
    elif presentType == 'ITEM':
        userItem = dt.getUserObject('userItemList', clearReward['itemId'])
        userItem['quantity'] += quantity
        dt.setUserObject('userItemList', clearReward['itemId'], userItem)
        args['userItemList'] = args.get('userItemList', []) + [userItem]
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

def getEpisodeLevel(userChara):
    episodePoints = [0, 1000, 4000, 14000, 64000]
    bondsTotalPt = userChara['bondsTotalPt']

    level = -1
    for i in range(len(episodePoints)):
        if bondsTotalPt >= episodePoints[i]:
            level = i+1
    return level

def startNewSection(newSectionId, response, canStart=True):
    # TODO: add challenge quests
    newSection, exists = newtil.createUserSection(newSectionId)
    if not exists:
        response['userSectionList'] = response.get('userSectionList', []) + [newSection]
        dt.setUserObject('userSectionList', newSectionId, newSection)
        # add enemies to userEnemyList, I think this is necessary for unlocking stuff
        openEnemyList = newSection['section']['openEnemyList']
        for enemy in openEnemyList:
            newEnemy, exists = newtil.createUserEnemy(enemy['enemyId'])
            if not exists: dt.setUserObject('userEnemyList', enemy['enemyId'], newEnemy)
    else:
        existingSection = dt.getUserObject('userSectionList', newSectionId)

        # check episode level
        if existingSection['section']['questType'] == 'CHARA':
            userChara = dt.getUserObject('userCharaList', existingSection['section']['charaId'])
            episodeLevel = getEpisodeLevel(userChara)
            canStart = canStart and episodeLevel >= int(str(existingSection['sectionId'])[-1])

        existingSection['canPlay'] = canStart
        dt.setUserObject('userSectionList', newSectionId, existingSection)
        response['userSectionList'] = response.get('userSectionList', []) + [existingSection]

    # create battles in section
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

    # create sections (and also battles) in new chapter
    canStart = True # only for the first one
    for sectionId in sorted(chapterSections[newChapterId], key=lambda x: x['sectionId']):
        startNewSection(sectionId, response, canStart)
        canStart = False

def addChallengeQuests(section, response):
    challengeBattleIds = sectionChallengeBattles[section]
    if len(challengeBattleIds) == 0: return

    challengeBattles = []
    for challengeBattleId in challengeBattleIds:
        challengeBattle, exists = newtil.createUserQuestBattle(challengeBattleId)
        if not exists:
            challengeBattles.append(challengeBattle)
            dt.setUserObject('userQuestBattleList', challengeBattleId, challengeBattle)
    
    response['userQuestBattleList'] = response.get('userQuestBattleList', []) + challengeBattles

def progressStory(battle):
    logger.info('progressing story')
    battleId = battle['questBattleId']
    response = {}
    # check if it's the last battle in a chapter
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

    # check if it's the last battle in a secton
    if battleId in nextSection:
        clearedSectionId = battle['questBattle']['sectionId']
        clearedSection = dt.getUserObject('userSectionList', clearedSectionId)
        clearedSection['cleared'] = True
        clearedSection['clearedAt'] = nowstr()

        response = obtainReward(clearedSection['section']['clearReward'], response)
        # TODO: make challenge quests work as well
    
        if nextSection[battleId] is not None:
            logger.info('battleId in nextSection')
            for nextSectionId in nextSection[battleId]:
                startNewSection(nextSectionId, response)  
            
        response['userSectionList'] = response.get('userSectionList', []) + [clearedSection]
        dt.setUserObject('userSectionList', clearedSectionId, clearedSection)

    # when it's not the last battle, get the next battle
    if battleId+1 in dt.masterBattles: # not sure if this heuristic is always the case
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

def progressMirrors(response):
    currPoints = response['userArenaBattle']['freeRankArenaPoint']
    # if it's the last available layer
    if currPoints >= dt.arenaClassList[1]['requiredPoint']:
        response['userArenaBattle']['freeRankArenaPoint'] = dt.arenaClassList[1]['requiredPoint']
        dt.saveJson('data/user/userArenaBattle.json', response['userArenaBattle'])
        return response

    # find which layer you're on with the given points
    arenaClassIdx = -1
    for i, arenaClass in enumerate(dt.arenaClassList[1:]):
        if currPoints >= arenaClass['requiredPoint']:
            arenaClassIdx = i
            break
    if arenaClassIdx == -1:
        arenaClassIdx = len(dt.arenaClassList)-1
    
    # if it's not the same layer as what's in the user's data, go to the next layer
    if dt.arenaClassList[arenaClassIdx]['arenaBattleFreeRankClass'] != response['userArenaBattle']['currentFreeRankClassType']:
        response['userArenaBattle']['currentFreeRankClassType'] = dt.arenaClassList[arenaClassIdx]['arenaBattleFreeRankClass']
        response['userArenaBattle']['currentFreeRankClass'] = response['userArenaBattle']['nextFreeRankClass']

        # set the 'nextClass' key if the new layer isn't the last, delete if it is
        if 'nextClass' in dt.arenaClassList[arenaClassIdx]:
            response['userArenaBattle']['nextFreeRankClass'] = dt.arenaClassList[arenaClassIdx-1]
        elif 'nextFreeRankClass' in response['userArenaBattle']:
            del response['userArenaBattle']['nextFreeRankClass']

        response = obtainReward(dt.arenaClassList[arenaClassIdx]['bonusRewardList'][0], response)

    dt.saveJson('data/user/userArenaBattle.json', response['userArenaBattle'])
    return response