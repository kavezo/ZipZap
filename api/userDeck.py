import flask
import json
from datetime import datetime
from api import userPiece, gacha
import logging

from util import dataUtil as dt
from util.homuUtil import nowstr

logger = logging.getLogger('app.userDeck')

def save():
    body = flask.request.json

    # sometimes, when you continue to edit a team, the deckType isn't sent at all,
    # so we have to store it
    # not sure if the request ever doesn't have a deckType on the first time you edit a team
    if 'deckType' in body:
        deckType = body['deckType']
        dt.saveJson('data/deckType.json',{'deckType': body['deckType']})
    else:
        deckType = dt.readJson('data/deckType.json')['deckType']

    userDeck = dt.getUserObject('userDeckList', deckType)
    if userDeck is None:
        userDeck = {'createdAt': nowstr(), 'userId': dt.userId, 'deckType': deckType}
    
    userDeck['name'] = body['name']
    
    if 'questPositionHelper' in body.keys():
        userDeck['questPositionHelper'] = body['questPositionHelper']
    if 'episodeUserCardId' in body.keys():
        userDeck['questEpisodeUserCardId'] = body['episodeUserCardId']
    if 'formationSheetId' in body.keys():
        userDeck['formationSheetId'] = body['formationSheetId']
        
    userFormation = dt.getUserObject('userFormationSheetList', body['formationSheetId'])
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
        numSlots = dt.getUserObject('userCardList', userDeck['userCardId'+str(i+1)])['revision'] + 1
        numMemoriaAssigned = 0
        for j, pieceId in enumerate(pieceIdList):
            userDeck['userPieceId0'+str(i+1)+str(j+1)] = pieceId
            numMemoriaAssigned += 1
            if numMemoriaAssigned >= numSlots:
                break

    dt.setUserObject('userDeckList', deckType, userDeck)
    
    return flask.jsonify({
        'resultCode': 'success',
        'userDeckList': [userDeck]
    })
    

def handleUserDeck(endpoint):
    if endpoint.startswith('save'):
        return save()
    else:
        logger.error('Missing implementation: userDeck/'+endpoint)
        flask.abort(501, description="Not implemented")