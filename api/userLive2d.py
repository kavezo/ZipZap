import json
import flask

def setLive2d():
    body = flask.request.json
    with open('data/user/userCharaList.json', encoding='utf-8') as f:
        userCharaList = json.load(f)

    response = {
        "resultCode": "success"
    }
    for i in range(len(userCharaList)):
        if userCharaList[i]['charaId'] == body['charaId']:
            userCharaList[i]['live2dId'] = body['live2dId']
            response['userCharaList'] = [userCharaList[i]]

    with open('data/user/userCharaList.json', 'w+', encoding='utf-8') as f:
        json.dump(userCharaList, f, ensure_ascii=False)

    return flask.jsonify(response)

def handleUserLive2d(endpoint):
    if endpoint.endswith('set'):
        return setLive2d()
    else:
        print('userLive2d/'+endpoint)
        flask.abort(501, description="Not implemented")