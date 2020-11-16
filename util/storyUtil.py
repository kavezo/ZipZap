from util import dataUtil, newUserObjectUtil
from datetime import datetime

questBattles = dataUtil.readJson('data/questBattleList.json')

nextSection = {sorted([b['questBattleId'] for b in questBattles if b['sectionId']==s])[-1]: s+1
                    for s in dataUtil.masterSections.keys() if s+1 in dataUtil.masterSections.keys()}
nextChapter = {}
for chapterId in dataUtil.masterChapters.keys():
    if chapterId + 1 in dataUtil.masterChapters.keys():
        chapterBattles = []
        for battle in questBattles:
            strBattleId = str(battle['questBattleId'])
            battleChapter = int(strBattleId[2:4])
            if (strBattleId.startswith('1') or strBattleId.startswith('2')) \
                and battleChapter == chapterId:
                chapterBattles.append(battle)
        chapterBattles = sorted(chapterBattles)
        nextChapter[chapterBattles[-1]['questBattleId']] = chapterId + 1

def obtainReward(clearReward, args):
    presentType = clearReward['presentType']
    quantity = clearReward['quantity']
    if presentType == 'DOPPEL':
        userDoppel, exists = newUserObjectUtil.createUserDoppel(clearReward['genericId'])
        if not exists: dataUtil.setUserObject('userDoppelList', clearReward['genericId'], userDoppel)
    elif presentType == 'GEM': # only Iroha's gems are rewards, so no need to check missing chara
        userChara = dataUtil.getUserObject('userCharaList', clearReward['genericId'])
        userChara['lbItemNum'] += quantity
        dataUtil.setUserObject('userCharaList', clearReward['genericId'], userChara)
    elif presentType == 'ITEM':
        userItem = dataUtil.getUserObject('userItemList', clearReward['itemId'])
        userItem['quantity'] += quantity
        dataUtil.setUserObject('userItemList', clearReward['itemId'], userItem)
    elif presentType == 'LIVE2D':
        newLive2d, exists = newUserObjectUtil.createUserLive2d(clearReward['genericId'], 
                                                clearReward['genericCode'], clearReward['displayName'])
        if not exists:
            userLive2dList = dataUtil.readJson('data/user/userLive2dList')
            dataUtil.saveJson('data/user/userLive2dList', userLive2dList + [newLive2d])
        args['userLive2dList'] = args.get('userLive2dList', []) + [newLive2d]
    elif presentType == 'PIECE':
        args['userPieceList'] = args.get('userPieceList', [])
        for _ in range(quantity):
            newPiece, _ = newUserObjectUtil.createUserMemoria(clearReward)
            args['userPieceList'].append(newPiece)
            dataUtil.setUserObject('userPieceList', newPiece['id'], newPiece)
    return args

# TODO: integrate this and see if it works
def progressStory(battle):
    battleId = battle['questBattleId']
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')
    response = {}
    if battleId in nextChapter:
        response['userChapterList'] = [
            {
                "chapter": dataUtil.masterChapters[nextChapter[battleId]],
                "chapterId": nextChapter[battleId],
                "cleared": False,
                "createdAt": nowstr,
                "userId": dataUtil.userId
            }
        ]
        currChapterId = int(str(battle['questBattleId'])[2:4])
        clearedChapter = dataUtil.getUserObject('userChapterList', currChapterId)
        clearedChapter['cleared'] = True
        clearedChapter['clearedAt'] = nowstr
        response['userChapterList'].append(clearedChapter)
        dataUtil.setUserObject('userChapterList', currChapterId, clearedChapter)
    if battleId in nextSection:
        sectionId = nextSection[battleId]
        response['userSectionList'] = [
            {
                "userId": dataUtil.userId,
                "sectionId": sectionId,
                "section": dataUtil.masterSections[sectionId],
                "canPlay": True,
                "cleared": False,
                "createdAt": nowstr
            }
        ]
        clearedSection = dataUtil.getUserObject('userSectionList', battle['sectionId'])
        clearedSection['cleared'] = True
        clearedSection['clearedAt'] = nowstr
        response['userSectionList'].append(clearedSection)
        obtainReward(clearedSection['clearReward'], response)
        dataUtil.setUserObject('userSectionList', sectionId, clearedSection)
    return response