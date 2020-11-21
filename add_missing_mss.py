from util import dataUtil, newUserObjectUtil

allSectionIds = dataUtil.masterSections.keys()
userSectionIds = dataUtil.userIndices['userSectionList'].keys()
userCharaIds = dataUtil.userIndices['userCharaList'].keys()
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
        "cleared": False,
        "missionStatus1": "NON_CLEAR",
        "missionStatus2": "NON_CLEAR",
        "missionStatus3": "NON_CLEAR",
        "rewardDone": False,
        "createdAt": newUserObjectUtil.nowstr()
    }
    userQuestBattleList.append(userBattle)
dataUtil.saveJson('data/user/userQuestBattleList.json', userQuestBattleList)