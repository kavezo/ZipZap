import flask
from util import dataUtil as dt
import logging

logger = logging.getLogger('app.userQuestAdventure')

def regist():
    return flask.jsonify({
        "userQuestAdventureList": [
            {
                "adventureId": flask.request.json['adventureId'],
                "createdAt": "",
                "skipped": False,
                "userId": dt.userId
            }
        ]
    })
    
def handleUserQuestAdventure(endpoint):
    if endpoint.endswith('skip'):
        return '{}'
    elif endpoint.endswith('regist'):
        return regist()
    else:
        logger.error('Missing implementation: userQuestAdventure/' + endpoint)
        flask.abort(501, description="Not implemented")