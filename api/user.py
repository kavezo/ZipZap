import json
import transferUserData
import flask
from uuid import uuid1

# TODO: actually figure out what this does
def isAnswered():
    response = {
        "resultCode": "success",
        'isAnswered': True
    }
    return flask.json.dumps(response, ensure_ascii=False)

# TODO: actually set password
def setPassword():
    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        gameUser = json.load(f)
        gameUser['passwordNotice'] = False
        json.dump(gameUser, f, ensure_ascii=False)

    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    return flask.json.dumps(response, ensure_ascii=False)

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
        print('user/'+endpoint)
        flask.abort(501, description="Not implemented")