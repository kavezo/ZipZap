from util import dataUtil, newUserObjectUtil
import json

def addMissingMss():
    allSectionIds = dataUtil.masterSections.keys()
    userSectionIds = dataUtil.userIndices['userSectionList'].keys()
    userCharaIds = dataUtil.userIndices['userCharaList'].keys() # don't need to dedupe because this already is a set
    missingMSSections = [sectionId for sectionId in allSectionIds if not sectionId in userSectionIds and str(sectionId).startswith('3')]
    addSections = [sectionId for sectionId in missingMSSections if int(str(sectionId)[1:5]) in userCharaIds]
    userSectionList = dataUtil.readJson('data/user/userSectionList.json')
    for sectionId in addSections:
        userSection = {
            "userId": dataUtil.userId,
            "sectionId": sectionId,
            "section": dataUtil.masterSections[sectionId],
            "canPlay": True, #str(sectionId).endswith('1'),
            "cleared": False,
            "createdAt": newUserObjectUtil.nowstr()
        }
        userSectionList.append(userSection)
    dataUtil.saveJson('data/user/userSectionList.json', userSectionList)

    allBattleIds = dataUtil.masterBattles.keys()
    userBattleIds = dataUtil.userIndices['userQuestBattleList'].keys()
    missingMSSBattles = [battleId for battleId in allBattleIds if not battleId in userBattleIds and str(battleId).startswith('3')]
    addBattles = [battleId for battleId in missingMSSBattles if int(str(battleId)[1:5]) in userCharaIds]
    userQuestBattleList = dataUtil.readJson('data/user/userQuestBattleList.json')
    for battleId in addBattles:
        userBattle = {
            "userId": dataUtil.userId,
            "questBattleId": battleId,
            "questBattle": dataUtil.masterBattles[battleId],
            "cleared": True,
            "missionStatus1": "CLEARED",
            "missionStatus2": "CLEARED",
            "missionStatus3": "CLEARED",
            "rewardDone": True,
            "createdAt": newUserObjectUtil.nowstr()
        }
        userQuestBattleList.append(userBattle)
    dataUtil.saveJson('data/user/userQuestBattleList.json', userQuestBattleList)

def dedupeCharas():
    # the problem is, every time you pull a new copy, you get a new chara
    # but until the end of the session, the game is stuck on the first chara
    # so we take the max episode point, and lbItemNum of the last chara
    # this leaves off some episode points that were earned, but might refund some gems
    finalCharas = {}
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)
    for userChara in userCharaList:
        charaId = userChara['charaId']
        if charaId in finalCharas:
            finalCharas[charaId]['bondsTotalPt'] = max(finalCharas[charaId]['bondsTotalPt'], userChara['bondsTotalPt'])
            finalCharas[charaId]['lbItemNum'] = userChara['lbItemNum']
        else:
            finalCharas[charaId] = userChara

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(list(finalCharas.values()), f, ensure_ascii=False)

if __name__=='__main__':
    print(
"""
My, are you here for an adjustment?

Which would you like today?
1) Add MSS for characters you've pulled
2) Get rid of extra MSS
3) N-nothing, just wanted to...visit...
"""
    )
    while True:
        choice = input('(type 1, 2, or 3, then enter): ')
        if choice == '1':
            addMissingMss()
            print('Here you go.')
        if choice == '2':
            dedupeCharas()
            print('Done. Oh, I might have accidentally touched some other bits of your fate, like giving you extra destiny gems -- but that shouldn\'t bother you too much.')
        if choice == '3':
            print()
            print('Ooh, I\'m flattered. I\'ll always be here when you need me for adjustment, \'kay?')
            input('(enter to close)')
            exit(0)
        print()

        print('Is that all for today?')
        while(True):
            choice = input('(Y/N): ')
            if choice.lower() == 'y':
                print()
                print('Thanks, come again!')
                input('(enter to close)')
                exit(0)
            if choice.lower() == 'n':
                break
            print('Sorry, what was that?')