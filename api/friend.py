import json
import flask
import logging

from util import dataUtil as dt

logger = logging.getLogger('app.friend')

def user(endpoint):
    response = {
        "followCount": 0,
        "followerCount": 0,
        "follow": False,
        "follower": False,
        "blocked": False
    }
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    response['userName'] = dt.getUserValue('loginName')
    response['lastAccessDate'] = dt.getUserValue('lastLoginDate')

    if endpoint.split('/')[-1] != user['id']:
        flask.abort(501, description='User does not exist')

    response['gameUser'] = dt.readJson('data/user/gameUser.json')
    response['userRank'] = dt.getGameUserValue('level')
    response['comment'] = dt.getGameUserValue('comment')
    response['inviteCode'] = dt.getGameUserValue('inviteCode')

    response['userCardList'] = dt.readJson('data/user/userCardList.json')
    leaderId = dt.getGameUserValue('leaderId')
    for userCard in response['userCardList']:
        if userCard['id'] == leaderId:
            response['leaderUserCard'] = userCard
            response['cardId'] = userCard['cardId']
            response['charaName'] = userCard['card']['cardName']
            response['cardRank'] = userCard['card']['rank']
            response['attributeId'] = userCard['card']['attributeId']
            response['level'] = userCard['level']
            response['displayCardId'] = userCard['displayCardId']
            response['revision'] = userCard['revision']
            break
    
    response['userDeck'] = dt.getUserObject('userDeckList', 20)

    for key in ['userCharaList', 'userPieceList', 'userDoppelList', 'userArenaBattle']:
        response[key] = dt.readJson('data/user/'+ key + '.json')

    return flask.jsonify(response)

def handleFriend(endpoint):
    if endpoint.startswith('user'):
        return user(endpoint)
    else:
        logger.error('Missing implementation: ' + flask.request.path)
        flask.abort(501, description='Not implemented')
