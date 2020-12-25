import json
import flask
import logging

from util import dataUtil as dt

logger = logging.getLogger('app.gameUser')

def changeLeader():
    body = flask.request.json
    gameUser = dt.setGameUserValue('leaderId', body['userCardId'])
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': dt.readJson('data/user/user.json')
    }
    return flask.jsonify(response)

def editComment():
    body = flask.request.json
    gameUser = dt.setGameUserValue('comment', body['comment'])
    response = {
        "resultCode": "success",
        'gameUser': gameUser,
        'user': dt.readJson('data/user/user.json')
    }
    return flask.jsonify(response)

def setBackground():
    body = flask.request.json
    bgItem = dt.getUserObject('userItemList', body['itemId'])

    gameUser = dt.setGameUserValue('bgItemId', body['itemId'])
    if bgItem is not None:
        gameUser = dt.setGameUserValue('bgItem', bgItem['item'])
    
    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    return flask.jsonify(response)

def skipAdventure():
    body = flask.request.json
    gameUser = dt.setGameUserValue('skipAdventure', body['skipAdventure'])
    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    return flask.jsonify(response)
    
def handleGameUser(endpoint):
    if endpoint.endswith('changeLeader'):
        return changeLeader()
    elif endpoint.endswith('editComment'):
        return editComment()
    elif endpoint.endswith('setBackground'):
        return setBackground()
    elif endpoint.endswith('skipAdventure'):
        return skipAdventure()
    elif endpoint.endswith('cacheClear'):
        return '{}' # TODO: set the cacheCleared variable. actually idk why you even want this but
    elif endpoint.endswith('read/announcement'):
        return '{}' # TODO: figure out what this actually does
    else:
        logger.error('Missing implementation: gameUser' + endpoint)
        flask.abort(501, description="Not implemented")