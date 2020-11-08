import json
import flask
import datetime
from mitmproxy import http


def arenaStart(response):
    with open('data/arenaStartDummy.json') as f:
        dummyResponse=json.load(f)
    response["resultCode"]="success"
    #response["userArenaBattleMatch"]=dummyResponse["userArenaBattleMatch"]
    response["userArenaBattleResultList"]=dummyResponse["userArenaBattleResultList"]
    response["userArenaBattleResultList"][0]["createdAt"]=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    response["userQuestBattleResultList"]=dummyResponse["userQuestBattleResultList"]
    response["userQuestBattleResultList"][0]["createdAt"]=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    print(response)
    with open('data/user/userQuestBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(response["userQuestBattleResultList"][0], f, ensure_ascii=False)
    
    #This actually matches with UserArenaBattle in /native/send/result
    with open('data/user/userArenaBattleResult.json', 'w+', encoding='utf-8') as f:
        json.dump(response["userArenaBattleResultList"][0], f, ensure_ascii=False)

def arenaReload(response):
#same as page/ArenaFreeRank?
    pass

def handleArena(endpoint):
    specialCases={
        'start':arenaStart,
        'reload':arenaReload
    }
    response={} 
    if endpoint in specialCases.keys():
        specialCases[endpoint](response)
        return flask.jsonify(response)

