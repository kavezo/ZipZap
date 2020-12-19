import flask
import logging

from api.questEndpoints.start import start
from api.questEndpoints.get import get
from api.questEndpoints.send import send
from util import dataUtil as dt

logger = logging.getLogger('app.quest')

def check():
    userQuestBattleResult = dt.readJson('data/user/userQuestBattleResult.json')
    userSection = dt.getUserObject('userSectionList', userQuestBattleResult['questBattle']['sectionId'])
    response = {
        'resultCode': 'success',
        'gameUser': dt.readJson('data/user/gameUser.json'), 
        'user': dt.readJson('data/user/user.json'),
        'userQuestBattleResultList': [userQuestBattleResult],
        'userQuestBattleList': [dt.getUserObject('userQuestBattleList', userQuestBattleResult['questBattleId'])],
        'userSectionList': [userSection],
        'userChapterList': []
    }
    chapter = dt.getUserObject('userChapterList', userSection['section']['genericId'])
    if chapter is not None:
        response['userChapterList'] = [chapter]
    return flask.jsonify(response)

def handleQuest(endpoint):
    if endpoint.startswith('start'):
        return start()
    elif endpoint.startswith('native/get'):
        return get()
    elif endpoint.startswith('native/result/send'):
        return send()
    elif endpoint.startswith('native/resume/check'):
        return check()
    else:
        logger.error('Missing implementation: quest/'+endpoint)
        flask.abort(501, description="Not implemented")