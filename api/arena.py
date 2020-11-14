import json
import flask
from datetime import datetime
from uuid import uuid1

def arenaStart(response):
    body = flask.request.json
    # with open('data/arenaStartDummy.json') as f:
    #     dummyResponse=json.load(f)
    # response["resultCode"]="success"
    #response["userArenaBattleMatch"]=dummyResponse["userArenaBattleMatch"]
    nowstr = (datetime.now()).strftime('%Y/%m/%d %H:%M:%S')

    with open('data/user/gameUser.json', encoding='utf-8') as f:
        userInfo = json.load(f)

    with open('data/user/userDeckList.json', encoding='utf-8') as f:
        userDeckList = json.load(f)
    chosenTeam = None
    for userDeck in userDeckList:
        if userDeck['deckType'] == 21:
                chosenTeam = userDeck
    if chosenTeam is None:
        flask.abort(400, '{"errorTxt": "You don\'t have a mirrors team...","resultCode": "error","title": "Error"}')

    with open('data/user/userFormationSheetList.json', encoding='utf-8') as f:
        formations = json.load(f)
    chosenFormation = None
    for formation in formations:
        if formation['formationSheetId'] == chosenTeam['formationSheetId']:
            chosenFormation = formation
    if chosenFormation is None:
        flask.abort(500, '{"errorTxt": "You don\'t have that formation.","resultCode": "error","title": "Error"}')

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
            "createdAt": nowstr,
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
            "level": userInfo['level'],
            "magiaNum": 0,
            "nativeClearTime": 0,
            "questBattleStatus": "CREATED",
            "riche": 0,
            "serverClearTime": 0,
            "skillNum": 0,
            "turns": 0,
            "userId": userInfo['userId']
        }

    for i in range(5):
        numberedId = 'userCardId'+str(i+1)
        if numberedId in chosenTeam:
            userQuestBattleResult['userCardId'+str(chosenTeam['questPositionId'+str(i+1)])] = chosenTeam[numberedId]
    
    userArenaBattleResult = {
        "userQuestBattleResultId": battleId,
        "userId": userInfo['userId'],
        "opponentUserId": body['opponentUserId'],
        "arenaBattleType": "FREE_RANK",
        "arenaBattleStatus": "CREATED",
        "arenaBattleOpponentType": "SAME",
        "numberOfConsecutiveWins": 0,
        "point": 0,
        "createdAt": nowstr
    }

    response.update({
        "resultCode": "success",
        "userQuestBattleResultList": [userQuestBattleResult],
        'userArenaBattleResult': [userArenaBattleResult]
    })

    with open('data/user/userQuestBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(userQuestBattleResult, f, ensure_ascii=False)
    
    with open('data/user/userArenaBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(userArenaBattleResult, f, ensure_ascii=False)

    # response["userArenaBattleResultList"]=dummyResponse["userArenaBattleResultList"]
    # response["userArenaBattleResultList"][0]["createdAt"]=nowstr
    # response["userQuestBattleResultList"]=dummyResponse["userQuestBattleResultList"]
    # response["userQuestBattleResultList"][0]["createdAt"]=nowstr
    # print(response)
    # with open('data/user/userQuestBattleResult.json', 'w+', encoding='utf-8') as f:
    #     json.dump(response["userQuestBattleResultList"][0], f, ensure_ascii=False)
    
    # #This actually matches with UserArenaBattle in /native/send/result
    # with open('data/user/userArenaBattleResult.json', 'w+', encoding='utf-8') as f:
    #     json.dump(response["userArenaBattleResultList"][0], f, ensure_ascii=False)

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

