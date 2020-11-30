import json
import transferUserData
import flask
from uuid import uuid1
import logging

from util import dataUtil as dt

logger = logging.getLogger('app.user')

# TODO: actually figure out what this does
def isAnswered():
    response = {
        "resultCode": "success",
        'isAnswered': True
    }
    return flask.jsonify(response)

# TODO: actually set password
def setPassword():
    gameUser = dt.setGameUserValue('passwordNotice', False)
    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    return flask.jsonify(response)

def transfer():
    body = flask.request.json
    try:
        transferUserData.fetchData(body['personalId'], body['password'])
    except ValueError as e:
        flask.abort(400, description=str(e))
    return flask.jsonify({"resultCode": "success"})

def handleUser(endpoint):
    if endpoint.endswith('isAnswered'):
        return isAnswered()
    elif endpoint.endswith('setPassword'):
        return setPassword()
    elif endpoint.endswith('transfer'):
        return transfer()
    else:
        logging.error('Missing implementation: user/'+endpoint)
        flask.abort(501, description="Not implemented")