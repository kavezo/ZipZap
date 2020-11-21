import flask
import json
from datetime import datetime
from api import userPiece, gacha
from uuid import uuid1

from util import dataUtil, newUserObjectUtil

def save():
    body = flask.request.json

    # sometimes, when you continue to edit a team, the deckType isn't sent at all,
    # so we have to store it
    # not sure if it ever doesn't have a deckType on the first time you edit a team
    if 'deckType' in body:
        deckType = body['deckType']
        dataUtil.saveJson('data/deckType.json',{'deckType': body['deckType']})
    else:
        deckType = dataUtil.readJson('data/deckType.json')['deckType']

    userDeck = dataUtil.getUserObject('userDeckList', deckType)
    if userDeck is None:
        userDeck = {'createdAt': newUserObjectUtil.nowstr(), 'userId': dataUtil.userId, 'deckType': deckType}
    
    userDeck['name'] = body['name']
    userDeck['questEpisodeUserCardId'] = body['episodeUserCardId']
    userDeck['formationSheetId'] = body['formationSheetId']
    
    if 'questPositionHelper' in userDeck.keys():
        userDeck['questPositionHelper'] = body['questPositionHelper']
        
    userFormation = dataUtil.getUserObject('userFormationSheetList', body['formationSheetId'])
    if userFormation is None:
        flask.abort(400, description='{"errorTxt": "Trying to use a nonexistent formation","resultCode": "error","title": "Error"}')

    userDeck['formationSheet'] = userFormation['formationSheet']

    keys = set(userDeck.keys())
    for key in keys:
        if key.startswith('questPositionId') or key.startswith('userCardId') or key.startswith('userPieceId'):
            del userDeck[key]        

    for i, positionId in enumerate(body['questPositionIds']):
        userDeck['questPositionId'+str(i+1)] = positionId
    
    for i, cardId in enumerate(body['userCardIds']):
        userDeck['userCardId'+str(i+1)] = cardId

    for i, pieceIdList in enumerate(body['userPieceIdLists']):
        numSlots = dataUtil.getUserObject('userCardList', userDeck['userCardId'+str(i+1)])['revision'] + 1
        numMemoriaAssigned = 0
        for j, pieceId in enumerate(pieceIdList):
            userDeck['userPieceId0'+str(i+1)+str(j+1)] = pieceId
            numMemoriaAssigned += 1
            if numMemoriaAssigned >= numSlots:
                break

    dataUtil.setUserObject('userDeckList', deckType, userDeck)
    
    print(userDeck)
    return flask.jsonify({
        'resultCode': 'success',
        'userDeckList': [userDeck]
    })
    

def handleUserDeck(endpoint):
    if endpoint.startswith('save'):
        return save()
    else:
        print('userDeck/'+endpoint)
        flask.abort(501, description="Not implemented")