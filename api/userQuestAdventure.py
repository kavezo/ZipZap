import flask
from util import dataUtil

def regist():
    return flask.jsonify({
        "userQuestAdventureList": [
            {
                "adventureId": flask.request.json['adventureId'],
                "createdAt": "",
                "skipped": False,
                "userId": dataUtil.userId
            }
        ]
    })
    
def handleUserQuestAdventure(endpoint):
    if endpoint.endswith('skip'):
        return '{}'
    elif endpoint.endswith('regist'):
        return regist()
    else:
        print('userQuestAdventure' + endpoint)
        flask.abort(501, description="Not implemented")