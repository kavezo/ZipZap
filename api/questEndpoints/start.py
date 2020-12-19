import flask
from uuid import uuid1

from util import dataUtil as dt
from util import newUserObjectUtil as newtil
from util.homuUtil import nowstr

def createScenario(userQuestBattle):
    questBattle = userQuestBattle['questBattle']
    section = dt.masterSections[questBattle['sectionId']]

    scenario = {
        "bgm": questBattle['bgm'],
        "bgmBoss": questBattle['bossBgm'],
        "title": section['title'],
        "cost": questBattle['ap'] if 'ap' in questBattle else section['ap'],
        "missionList": [],
        #"sheetType": 6, # what is this?
        "questType": section['questType'],
        "auto": True
    }
    for i in range(1,4):
        scenario['missionList'].append({
            'description': questBattle['missionMaster'+str(i)]['description'],
            'clear': userQuestBattle['missionStatus'+str(i)] == 'CLEARED'
        })

    if str(section['sectionId']).startswith('1') or str(section['sectionId']).startswith('2'):
        chapterNo = dt.masterChapters[section['genericId']]['chapterNoForView']
        scenario['titleExtend'] = 'Ch.' + chapterNo + ' Ep.' + str(section['genericIndex'])

    if 'difficulty' in section:
        scenario["difficulty"] = section['difficulty']
        
    return scenario

def createResult(userQuestInfo, chosenTeam, chosenFormation):
    return {
        "battleType": "QUEST",
        "bondsPt1": 0,
        "bondsPt2": 0,
        "bondsPt3": 0,
        "bondsPt4": 0,
        "bondsPt5": 0,
        "bondsPt6": 0,
        "bondsPt7": 0,
        "bondsPt8": 0,
        "bondsPt9": 0,
        "clearedMission1": userQuestInfo['missionStatus1']=='CLEARED',
        "clearedMission2": userQuestInfo['missionStatus2']=='CLEARED',
        "clearedMission3": userQuestInfo['missionStatus3']=='CLEARED',
        "connectNum": 0,
        "continuedNum": 0,
        "createdAt": nowstr(),
        "deadNum": 0,
        "deckType": chosenTeam['deckType'],
        "diskAcceleNum": 0,
        "diskBlastNum": 0,
        "diskChargeNum": 0,
        "doppelNum": 0,
        "enemyNum": 0,
        "episodeUserCardId": chosenTeam['questEpisodeUserCardId'],
        "exp": 0,
        "follow": True,
        "follower": True,
        "formationSheetId": chosenTeam['formationSheetId'],
        "formationSheet": chosenFormation,
        "helpBondsPt": 0,
        "helpPosition": chosenTeam['questPositionHelper'],
        "id": str(uuid1()),
        "level": dt.getGameUserValue('level'),
        "magiaNum": 0,
        "nativeClearTime": 0,
        "questBattle": userQuestInfo['questBattle'],
        "questBattleId": userQuestInfo['questBattleId'],
        "questBattleStatus": "CREATED",
        "riche": 0,
        "scenario": createScenario(userQuestInfo),
        "serverClearTime": 0,
        "skillNum": 0,
        "turns": 0,
        "userId": dt.userId
    }

def start():    
    body = flask.request.json

    # get userQuestBattle
    userQuestInfo = dt.getUserObject('userQuestBattleList', body['questBattleId'])

    if userQuestInfo is None:
        userQuestInfo = newtil.createUserQuestBattle(body['questBattleId'])
        dt.setUserObject('userQuestBattleList', body['questBattleId'], userQuestInfo)

    # get team information
    chosenTeam = dt.getUserObject('userDeckList', body['deckType'])
    if chosenTeam is None:
        flask.abort(400, '{"errorTxt": "The team doesn\'t exist...","resultCode": "error","title": "Error"}')

    chosenFormation = dt.getUserObject('userFormationSheetList', chosenTeam['formationSheetId'])
    if chosenFormation is None:
        flask.abort(500, '{"errorTxt": "You don\'t have that formation.","resultCode": "error","title": "Error"}')

    userQuestBattleResult = createResult(userQuestInfo, chosenTeam, chosenFormation)

    # add cards to team
    if 'helpUserCardId' in body:
        userQuestBattleResult["helpUserCardId"] = body['helperUserCardId']
        userQuestBattleResult["helpUserId"] = body['helperUserId']
        userQuestBattleResult["helpAttributeId"] = body['helpAttributeId']

    for i in range(4):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in body:
            userQuestBattleResult['userCardId'+str(body['questPositionId'+str(i+1)])] = body[numberedId]

    resultdict = {
        "resultCode": "success",
        "userQuestBattleResultList": [userQuestBattleResult]
    }

    dt.saveJson('data/user/userQuestBattleResult.json', userQuestBattleResult)
    return flask.jsonify(resultdict)