import json
from mitmproxy import http

def user(flow):

    response = {
        "followCount": 0,
        "followerCount": 0,
        "follow": False,
        "follower": False,
        "blocked": False
    }
    with open('data/user/user.json', encoding='utf-8') as f:
        user = json.load(f)
    response['userName'] = user['loginName']
    response['lastAccessDate'] = user['lastLoginDate']

    if flow.request.path.split('/')[-1] != user['id']:
        flow.response = http.HTTPResponse.make(501, "not implemented :/", {})
        return

    with open('data/user/gameUser.json', encoding='utf-8') as f:
        gameUser = json.load(f)
    response['gameUser'] = gameUser
    response['userRank'] = gameUser['level']
    response['comment'] = gameUser['comment']
    response['inviteCode'] = gameUser['inviteCode']

    with open('data/user/userCardList.json', encoding='utf-8') as f:
        userCardList = json.load(f)
    response['userCardList'] = userCardList

    for userCard in userCardList:
        if userCard['id'] == gameUser['leaderId']:
            response['leaderUserCard'] = userCard
            response['cardId'] = userCard['cardId']
            response['charaName'] = userCard['card']['cardName']
            response['cardRank'] = userCard['card']['rank']
            response['attributeId'] = userCard['card']['attributeId']
            response['level'] = userCard['level']
            response['displayCardId'] = userCard['displayCardId']
            response['revision'] = userCard['revision']
            break
    
    userDeck = {}
    with open('data/user/userDeckList.json', encoding='utf-8') as f:
        userDeckList = json.load(f)
    for deck in userDeckList:
        if deck['deckType'] == 20:
            userDeck = deck
    response['userDeck'] = userDeck

    for key in ['userCharaList', 'userPieceList', 'userDoppelList', 'userArenaBattle']:
        with open('data/user/' + key + '.json', encoding='utf-8') as f:
            value = json.load(f)
        response[key] = value

    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

def handleFriend(flow):
    endpoint = flow.request.path.replace('/magica/api/friend', '')
    if endpoint.startswith('/user'):
        user(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})
