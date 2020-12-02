import json
from datetime import datetime
import os
import shutil

def createDefaultUser():
    if not os.path.exists('data/user'):
        print('Copying over default user...') # logging isn't set up yet, and also it's not too important to have in logs
        shutil.copytree('data/default_user', 'data/user')

def addAllDailies():
    with open('data/dailyChallengeList.json', encoding='utf-8') as f:
        challenges = json.load(f)
    with open('data/user/userDailyChallengeList.json', encoding='utf-8') as f:
        userChallenges = json.load(f)
    with open('data/user/user.json', encoding='utf-8') as f:
        userId = json.load(f)['id']
    
    userChallengeIds = {userChallenge['challengeId'] for userChallenge in userChallenges}
    missingChallenges = [challenge for challenge in challenges if not challenge['id'] in userChallengeIds]
    userChallenges += [{
        'userId': userId,
        'challengeId': challenge['id'],
        'challenge': challenge,
        'clearedCount': 0,
        'receivedAt': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        'update': False
    } for challenge in missingChallenges]

    with open('data/user/userDailyChallengeList.json', 'w+', encoding='utf-8') as f:
        json.dump(userChallenges, f, ensure_ascii=False)