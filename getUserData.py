from mitmproxy import http
from mitmproxy.script import concurrent
import json
import os
import requests
import time

# not GachaHistoryList, as we don't know what history they actually have
data1 = ['giftList','itemList','pieceList','gameUser','user','userCardList','userChapterList',
    'userCharaList','userDailyChallengeList','userDeckList','userDoppelList','userFollowList','userFormationSheetList',
    'userGiftList','userItemList']
data2 = ['userLimitedChallengeList','userList','userLive2dList','userPieceList','userPieceSetList','userPieceCollectionList',
    'userQuestAdventureList','userQuestBattleList','userSectionList', 'userArenaBattle',
    'userShopItem','userStatusList','userTotalChallengeList','userGachaGroupList'
    ]

# save old user data
if not os.path.exists('data/userBackup'):
    os.mkdir('data/userBackup')
for file in os.listdir('data/user'):
    if os.path.isfile(file):
        os.rename(os.path.join('data/user', file),
                    os.path.join('data/userBackup', file))

@concurrent
def request(flow: http.HTTPFlow) -> None:
    if 'magica-us.com/magica/api/page/TopPage' in flow.request.pretty_url:
        
        prefix = flow.request.pretty_url.split('?')[0]
        suffix = flow.request.pretty_url.split('&')[-1]
        url1 = prefix + '?value='+ (','.join(data1)) + '&' + suffix
        url2 = prefix + '?value='+ (','.join(data2)) + '&' + suffix
        
        headers = {key.decode('utf-8').replace(':', ''):value.decode('utf-8') for key, value in flow.request.headers.fields}

        time.sleep(1)
        request1 = requests.get(url1, headers = headers)
        time.sleep(1)
        request2 = requests.get(url2, headers = headers)

        # get data from server
        for dataName in data1:
            request1body = json.loads(request1.text)
            if dataName in request1body:
                print('writing ' + dataName)
                with open('data/user/'+dataName+'.json', 'w+', encoding='utf-8') as f:
                    json.dump(request1body[dataName], f, ensure_ascii=False)
        for dataName in data2:
            request2body = json.loads(request2.text)
            if dataName in request2body:
                print('writing ' + dataName)
                with open('data/user/'+dataName+'.json', 'w+', encoding='utf-8') as f:
                    json.dump(request2body[dataName], f, ensure_ascii=False)

        print('\ndone getting data')
