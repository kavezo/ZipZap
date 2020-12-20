# welcome to microservice naming 101
# tsurunoUtil is tsurunoUtil because everyone get challenge by mightiest meguca

import flask

from util import dataUtil as dt
from util.homuUtil import nowstr

def resetDaily():
    path = 'data/user/userDailyChallengeList.json'
    userDailyChallenges = dt.readJson(path)
    for challenge in userDailyChallenges:
        challenge['clearedCount'] = 0
    dt.saveJson(path, userDailyChallenges)

def clearDaily(challengeIds):
    dailyChallenges = []
    for challengeId in challengeIds:
        dailyChallenge = dt.getUserObject('userDailyChallengeList', challengeId)
        if dailyChallenge['clearedCount'] < dailyChallenge['challenge']['count']:
            dailyChallenge['clearedCount'] += 1
            if dailyChallenge['clearedCount'] >= dailyChallenge['challenge']['count']:
                dailyChallenge['clearedAt'] = nowstr()
            dt.setUserObject('userDailyChallengeList', challengeId, dailyChallenge)
            dailyChallenges.append(dailyChallenge)
    return dailyChallenges

def questClear(response):
    if 'userArenaBattle' in response:
        return clearDaily([20200702, 20200705, 20200707]), [], []
    if response['userQuestBattleResultList'][0]['questBattleStatus'] == 'SUCCESSFUL':
        print('clearing daily')
        return clearDaily([20200701, 20200704, 20200706, 20200708, 20200709, 20200710, 20200711]), [], []

challengeHandlers = {
    '/quest/native/result/send': questClear,
    '/userPiece/compose': lambda _: (clearDaily([20200703]), [], [])
}

def handleChallenge(response):
    path = flask.request.path
    if not path in challengeHandlers:
        return response

    responseDict = response.json
    challengeLists = challengeHandlers[path](responseDict)
    if challengeLists is None: return response
    dailies, totals, limiteds = challengeLists

    if not len(dailies) == 0:
        responseDict['userDailyChallengeList'] = dailies
    if not len(totals) == 0:
        responseDict['userTotalChallengeList'] = totals
    if not len(limiteds) == 0:
        responseDict['userLimitedChallengeList'] = limiteds
    return flask.jsonify(responseDict)