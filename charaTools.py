from util import dataUtil as dt
from util.homuUtil import nowstr
from util import newUserObjectUtil as newtil
import json

def addMissingMss():
    allSectionIds = dt.masterSections.keys()
    userSectionIds = dt.listUserObjectKeys('userSectionList')
    userCharaIds = dt.listUserObjectKeys('userCharaList') # don't need to dedupe because this already is a set
    missingMSSections = [sectionId for sectionId in allSectionIds if not sectionId in userSectionIds and str(sectionId).startswith('3')]
    addSections = [sectionId for sectionId in missingMSSections if int(str(sectionId)[1:5]) in userCharaIds]
    userSectionList = dt.readJson('data/user/userSectionList.json')
    for sectionId in addSections:
        userSection = {
            "userId": dt.userId,
            "sectionId": sectionId,
            "section": dt.masterSections[sectionId],
            "canPlay": True, #str(sectionId).endswith('1'),
            "cleared": False,
            "createdAt": nowstr()
        }
        userSectionList.append(userSection)
    dt.saveJson('data/user/userSectionList.json', userSectionList)

    allBattleIds = dt.masterBattles.keys()
    userBattleIds = dt.listUserObjectKeys('userQuestBattleList')
    missingMSSBattles = [battleId for battleId in allBattleIds if not battleId in userBattleIds and str(battleId).startswith('3')]
    addBattles = [battleId for battleId in missingMSSBattles if int(str(battleId)[1:5]) in userCharaIds]
    userQuestBattleList = dt.readJson('data/user/userQuestBattleList.json')
    for battleId in addBattles:
        userBattle = {
            "userId": dt.userId,
            "questBattleId": battleId,
            "questBattle": dt.masterBattles[battleId],
            "cleared": True,
            "missionStatus1": "CLEARED",
            "missionStatus2": "CLEARED",
            "missionStatus3": "CLEARED",
            "rewardDone": True,
            "createdAt": nowstr()
        }
        userQuestBattleList.append(userBattle)
    dt.saveJson('data/user/userQuestBattleList.json', userQuestBattleList)

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

def clearLabyrinths():
    clearedSection = {
        "cleared": True,
        "clearedAt": "2020/01/01 00:00:00"
    }

    clearedBattle = {
        "cleared": True,
        "missionStatus1": "CLEARED",
        "missionStatus2": "CLEARED",
        "missionStatus3": "CLEARED",
        "rewardDone": True,
        "firstClearedAt": "2020/01/01 00:00:00",
        "lastClearedAt": "2020/01/01 00:00:00",
        "clearCount": 1,
        "maxDamage": 1,
    }

    for labType in range(1, 3):
        for day in range(1, 7):
            sectionId = int(f'4000{day}{labType}')
            section = dt.getUserObject('userSectionList', sectionId)

            if section is None: 
                section, _ = newtil.createUserSection(sectionId)

            if not section['cleared']:
                section.update(clearedSection)
                dt.setUserObject('userSectionList', sectionId, section)

            for level in range(1, 5):
                battleId = int(f'4000{day}{labType}{level}')
                battle = dt.getUserObject('userQuestBattleList', battleId)

                if battle is None:
                    battle, _ = newtil.createUserQuestBattle(battleId)

                if not battle['cleared']: 
                    battle.update(clearedBattle)
                    dt.setUserObject('userQuestBattleList', battleId, battle)

if __name__=='__main__':
    print(
"""
My, are you here for an adjustment?

Which would you like today?
1) Add MSS for characters you've pulled
2) Get rid of extra MSS
3) Clear all labyrinth quests and missions (without getting rewards)
4) N-nothing, just wanted to...visit...
"""
    )
    while True:
        choice = input('(type a number between 1 and 4, then enter): ')
        if choice == '1':
            addMissingMss()
            print('Here you go.')
        if choice == '2':
            dedupeCharas()
            print('Done. Oh, I might have accidentally touched some other bits of your fate, like giving you extra destiny gems -- but that shouldn\'t bother you too much.')
        if choice == '3':
            print('On it...')
            clearLabyrinths()
            print('Ahh, forcing your dear coordinator to do the dirty work for you...don\'t you think I deserve more payment?')
        if choice == '4':
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