import flask
from util import dataUtil as dt
from util.homuUtil import nowstr
import logging

logger = logging.getLogger('app.userQuestAdventure')

def regist():
    adventureId = flask.request.json['adventureId']
    newAdventure = {
        "adventureId": adventureId,
        "createdAt": nowstr(),
        "skipped": False,
        "userId": dt.userId
    }
    dt.setUserObject('userQuestAdventureList', adventureId, newAdventure)
    return flask.jsonify({
        "userQuestAdventureList": [newAdventure]
    })
    
def handleUserQuestAdventure(endpoint):
    if endpoint.endswith('skip'):
        return '{}'
    elif endpoint.endswith('regist'):
        return regist()
    else:
        logger.error('Missing implementation: userQuestAdventure/' + endpoint)
        flask.abort(501, description="Not implemented")