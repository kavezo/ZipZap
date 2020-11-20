import json
import flask

from util import dataUtil

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
    response['userName'] = dataUtil.getUserValue('loginName')
    response['lastAccessDate'] = dataUtil.getUserValue('lastLoginDate')

    if endpoint.split('/')[-1] != user['id']:
        flask.abort(501, description='User does not exist')

    response['gameUser'] = dataUtil.readJson('data/user/gameUser.json')
    response['userRank'] = dataUtil.getGameUserValue('level')
    response['comment'] = dataUtil.getGameUserValue('comment')
    response['inviteCode'] = dataUtil.getGameUserValue('inviteCode')

    response['userCardList'] = dataUtil.readJson('data/user/userCardList.json')
    leaderId = dataUtil.getGameUserValue('leaderId')
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
    
    response['userDeck'] = dataUtil.getUserObject('userDeckList', 20)

    for key in ['userCharaList', 'userPieceList', 'userDoppelList', 'userArenaBattle']:
        response[key] = dataUtil.readJson('data/user/'+ key + '.json')

    return flask.jsonify(response)

def handleFriend(endpoint):
    print(endpoint)
    if endpoint.startswith('user'):
        return user(endpoint)
    else:
        print(flask.request.path)
        flask.abort(501, description='Not implemented')
