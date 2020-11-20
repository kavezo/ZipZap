import json
import flask
from datetime import datetime
from uuid import uuid1

from util import dataUtil, newUserObjectUtil

def arenaStart(response):
    body = flask.request.json
    
    chosenTeam = dataUtil.getUserObject('userDeckList', 21)
    if chosenTeam is None:
        flask.abort(400, '{"errorTxt": "You don\'t have a mirrors team...","resultCode": "error","title": "Error"}')

    chosenFormation = dataUtil.getUserObject('userFormationSheetList', chosenTeam['formationSheetId'])
    if chosenFormation is None:
        flask.abort(400, '{"errorTxt": "You don\'t have that formation.","resultCode": "error","title": "Error"}')

    battleId = str(uuid1())
    userQuestBattleResult = {
            "battleType": "ARENA",
            "bondsPt1": 0,
            "bondsPt2": 0,
            "bondsPt3": 0,
            "bondsPt4": 0,
            "bondsPt5": 0,
            "bondsPt6": 0,
            "bondsPt7": 0,
            "bondsPt8": 0,
            "bondsPt9": 0,
            "clearedMission1": False,
            "clearedMission2": False,
            "clearedMission3": False,
            "connectNum": 0,
            "continuedNum": 0,
            "createdAt": newUserObjectUtil.nowstr(),
            "deadNum": 0,
            "deckType": 21,
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
            "id": battleId,
            "level": dataUtil.getUserValue('level'),
            "magiaNum": 0,
            "nativeClearTime": 0,
            "questBattleStatus": "CREATED",
            "riche": 0,
            "serverClearTime": 0,
            "skillNum": 0,
            "turns": 0,
            "userId": dataUtil.userId
        }

    for i in range(5):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in chosenTeam:
            userQuestBattleResult['userCardId'+str(chosenTeam['questPositionId'+str(i+1)])] = chosenTeam[numberedId]
    
    userArenaBattleResult = {
        "userQuestBattleResultId": battleId,
        "userId": dataUtil.userId,
        "opponentUserId": body['opponentUserId'],
        "arenaBattleType": "FREE_RANK",
        "arenaBattleStatus": "CREATED",
        "arenaBattleOpponentType": "SAME",
        "numberOfConsecutiveWins": 0,
        "point": 0,
        "createdAt": newUserObjectUtil.nowstr()
    }

    response.update({
        "resultCode": "success",
        "userQuestBattleResultList": [userQuestBattleResult],
        'userArenaBattleResult': [userArenaBattleResult]
    })

    dataUtil.saveJson('data/user/userQuestBattleResult.json', userQuestBattleResult)
    dataUtil.saveJson('data/user/userArenaBattleResult.json', userArenaBattleResult)

def arenaReload(response):
#same as page/ArenaFreeRank?
    pass

def handleArena(endpoint):
    specialCases={
        'start':arenaStart,
        'reload':arenaReload
    }
    response={} 
    if endpoint in specialCases.keys():
        specialCases[endpoint](response)
        return flask.jsonify(response)

