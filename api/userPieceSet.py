import flask
from datetime import datetime

from util import dataUtil as dt
from util.homuUtil import nowstr

def save():
    body = flask.request.json

    targetUserPieceSet = dt.getUserObject('userPieceSetList', body['setNum'])
    if targetUserPieceSet is None:
        targetUserPieceSet = {
            "createdAt": nowstr(),
            'userId': dt.userId,
            'setNum': body['setNum']
        }

    targetUserPieceSet['name'] = body['name']
    for i, id in enumerate(body['userPieceIdList']):
        targetUserPieceSet['userPieceId'+str(i+1)] = id

    dt.setUserObject('userPieceSetList', body['setNum'], targetUserPieceSet)

    response = {
        'resultCode': 'success',
        'userPieceSetList': [targetUserPieceSet]
    }
    return flask.jsonify(response)

def handleUserPieceSet(endpoint):
    if endpoint.startswith('save'):
        return save()
    else:
        print('userPieceSet/'+endpoint)
        flask.abort(501, description="Not implemented")