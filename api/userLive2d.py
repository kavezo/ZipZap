import json
import flask

from util import dataUtil

def setLive2d():
    body = flask.request.json

    response = {
        "resultCode": "success"
    }
    userChara = dataUtil.getUserObject('userCharaList', body['charaId'])
    userChara['live2dId'] = body['live2dId']
    response['userCharaList'] = [userChara]
    dataUtil.setUserObject('userCharaList', body['charaId'], userChara)

    return flask.jsonify(response)

def handleUserLive2d(endpoint):
    if endpoint.endswith('set'):
        return setLive2d()
    else:
        print('userLive2d/'+endpoint)
        flask.abort(501, description="Not implemented")