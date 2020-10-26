from mitmproxy import http
import json
from datetime import datetime
from api import userPiece, gacha
from uuid import uuid1

def save(flow):
    body = json.loads(flow.request.text)
    with open('data/user/userDeckList.json', encoding='utf-8') as f:
        userDeckList = json.load(f)    
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    nowstr = str(datetime.now()).split('.')[0].replace('-', '/')

    # sometimes, when you continue to edit a team, the deckType isn't sent at all,
    # so we have to store it
    # not sure if it ever doesn't have a deckType on the first time you edit a team
    if 'deckType' in body:
        deckType = body['deckType']
        with open('data/deckType.json', 'w+', encoding='utf-8') as f:
            json.dump({'deckType': body['deckType']}, f, ensure_ascii=False)
    else:
        with open('data/deckType.json', encoding='utf-8') as f:
            deckType = json.load(f)['deckType']

    deckIdx = -1
    for i in range(len(userDeckList)):
        if userDeckList[i]['deckType'] == deckType:
            deckIdx = i
    if deckIdx == -1:
        deckIdx = len(userDeckList)
        userDeckList.append({'createdAt': nowstr, 'userId': userId, 'deckType': deckType})
    
    userDeckList[deckIdx]['name'] = body['name']
    userDeckList[deckIdx]['questEpisodeUserCardId'] = body['episodeUserCardId']
    userDeckList[deckIdx]['questPositionHelper'] = body['questPositionHelper']
    userDeckList[deckIdx]['formationSheetId'] = body['formationSheetId']

    with open('data/formationSheetList.json', encoding='utf-8') as f:
        formationSheetList = json.load(f)
    
    chosenFormationSheet = {}
    for formation in formationSheetList:
        if formation['id'] == body['formationSheetId']:
            chosenFormationSheet = formation
            break
    if chosenFormationSheet == {}:
        flow.response = http.HTTPResponse.make(400, '{"errorTxt": "Trying to use a nonexistent formation","resultCode": "error","title": "Error"}', {})
        return

    userDeckList[deckIdx]['formationSheet'] = chosenFormationSheet

    for i, positionId in enumerate(body['questPositionIds']):
        userDeckList[deckIdx]['questPositionId'+str(i+1)] = positionId
    
    for i, cardId in enumerate(body['userCardIds']):
        userDeckList[deckIdx]['userCardId'+str(i+1)] = cardId

    for i, pieceIdList in enumerate(body['userPieceIdLists']):
        for j, pieceId in enumerate(pieceIdList):
            userDeckList[deckIdx]['userPieceId0'+str(i+1)+str(j+1)] = pieceId

    with open('data/user/userDeckList.json', 'w+', encoding='utf-8') as f:
        json.dump(userDeckList, f, ensure_ascii=False)
    
    response = json.dumps({
        'resultCode': 'success',
        'userDeckList': [userDeckList[deckIdx]]
    }, ensure_ascii=False)
    flow.response = http.HTTPResponse.make(200, response, {})
    

def handleUserDeck(flow):
    endpoint = flow.request.path.replace('/magica/api/userDeck', '')
    if endpoint.startswith('/save'):
        save(flow)
    else:
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})