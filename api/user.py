import json
import transferUserData
from mitmproxy import http
from uuid import uuid1
import requests

def isAnswered(flow):
    response = {
        "resultCode": "success",
        'isAnswered': True
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

def setPassword(flow):
    with open('data/user/gameUser.json', 'w+', encoding='utf-8') as f:
        gameUser = json.load(f)
        gameUser['passwordNotice'] = False
        json.dump(gameUser, f, ensure_ascii=False)

    response = {
        "resultCode": "success",
        'gameUser': gameUser
    }
    flow.response = http.HTTPResponse.make(200, json.dumps(response, ensure_ascii=False), {"Content-Type": "application/json"})

def transfer(flow):
    body = json.loads(flow.request.text)
    try:
        transferUserData.fetchData(body['personalId'], body['password'])
    except ValueError as e:
        flow.response = http.HTTPResponse.make(400, str(e), {"Content-Type": "application/json"})
    flow.response = http.HTTPResponse.make(200, '{"resultCode": "success"}', {"Content-Type": "application/json"})

def handleUser(flow):
    endpoint = flow.request.path.replace('/magica/api/user', '')
    if endpoint.endswith('/isAnswered'):
        isAnswered(flow)
    elif endpoint.endswith('/setPassword'):
        setPassword(flow)
    elif endpoint.endswith('/transfer'):
        transfer(flow)
    else:
        print(flow.request.path)
        flow.response = http.HTTPResponse.make(501, "Not implemented", {})