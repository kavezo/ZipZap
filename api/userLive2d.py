import json
import flask

from util import dataUtil as dt

def setLive2d():
    body = flask.request.json

    response = {
        "resultCode": "success"
    }
    userChara = dt.getUserObject('userCharaList', body['charaId'])
    userChara['live2dId'] = body['live2dId']
    response['userCharaList'] = [userChara]
    dt.setUserObject('userCharaList', body['charaId'], userChara)

    return flask.jsonify(response)

def handleUserLive2d(endpoint):
    if endpoint.endswith('set'):
        return setLive2d()
    else:
        print('userLive2d/'+endpoint)
        flask.abort(501, description="Not implemented")