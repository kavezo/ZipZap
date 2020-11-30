import json
import flask

from util import dataUtil as dt
from util.homuUtil import nowstr
from api.questEndpoints.send import obtainItem

def receiveReward(challenge):
    response = {}
    for reward in challenge['challenge']['rewardCodes'].split(','):
        response = dt.updateJson(response, obtainItem(reward))
    challenge['receivedAt'] = nowstr()
    dt.setUserObject('userDailyChallengeList', challenge['challengeId'], challenge)
    return response

def receive():
    body = flask.request.json
    userChallenge = dt.getUserObject('userDailyChallengeList', body['challengeId'])

    response = receiveReward(userChallenge)
    response['resultCode'] = 'success'
    response['userDailyChallengeList'] = [userChallenge]
    return flask.jsonify(response)

def receiveAll():
    response = {"resultCode": "success"}
    userChallenges = dt.readJson('data/user/userDailyChallengeList.json')
    finalChallenges = []
    for challenge in userChallenges:
        if challenge['clearedCount'] >= challenge['challenge']['count']:
            response = dt.updateJson(response, receiveReward(challenge))
            finalChallenges.append(challenge)
    response['userDailyChallengeList'] = finalChallenges
    return flask.jsonify(response)

def handleDaily(endpoint):
    if endpoint.endswith('receive'):
        return receive()
    elif endpoint.endswith('receive/all'):
        return receiveAll()
    else:
        flask.abort(501, description='Not implemented')