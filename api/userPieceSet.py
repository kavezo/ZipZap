import flask
from datetime import datetime

from util import dataUtil, newUserObjectUtil

def save():
    body = flask.request.json

    targetUserPieceSet = dataUtil.getUserObject('userPieceSetList', body['setNum'])
    if targetUserPieceSet is None:
        targetUserPieceSet = {
            "createdAt": newUserObjectUtil.nowstr(),
            'userId': dataUtil.userId,
            'setNum': body['setNum']
        }

    targetUserPieceSet['name'] = body['name']
    for i, id in enumerate(body['userPieceIdList']):
        targetUserPieceSet['userPieceId'+str(i+1)] = id

    dataUtil.setUserObject('userPieceSetList', body['setNum'], targetUserPieceSet)

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