from mitmproxy import http
from mitmproxy.script import concurrent
import requests
import os
from api import page, gacha, userCard, user, gameUser, userChara, friend, userPiece, userPieceSet, userLive2d

isLoggingIn = False

def serveAsset(flow):
    versionless = flow.request.path.split('?')[0]
        
    if not flow.request.path.startswith('/magica/resource'):
        if not os.path.exists('assets'+versionless):
            if not os.path.exists(os.path.dirname('assets'+versionless)):
                os.makedirs(os.path.dirname('assets'+versionless))
            asset_request = requests.get('https://en.rika.ren'+flow.request.path)
            print('requested ' + flow.request.path)
            if (asset_request.status_code == 200):
                print('writing to assets' + versionless)
                with open('assets'+versionless, 'wb+') as f:
                    f.write(asset_request.content)
            else:
                print('status code was not 200 D:')
                flow.response = http.HTTPResponse.make(304, "", {})
        else:
            with open('assets'+versionless, 'rb') as f:
                text = f.read()
            flow.response = http.HTTPResponse.make(200, text, {})
    elif versionless.endswith('.json.gz'):
        flow.response = http.HTTPResponse.make(304, "", {})
    else:
        # This is suuuuuuuper slow because it doesn't run in parallel...
        asset_request = requests.get('https://en.rika.ren'+flow.request.path)
        flow.response  = http.HTTPResponse.make(200, asset_request.content, {})

@concurrent
def request(flow: http.HTTPFlow) -> None:
    global isLoggingIn
    if not flow.request.pretty_host.endswith("magica-us.com"):
        return
    if flow.request.path.startswith('/search'):
        # TODO: implement search
        return
    if flow.request.path.startswith('/magica/api'):
        # TODO: implement the rest
        apis = {'/magica/api/gacha': gacha.handleGacha,
                '/magica/api/userCard': userCard.handleUserCard,
                '/magica/api/user/': user.handleUser,
                '/magica/api/gameUser': gameUser.handleGameUser,
                '/magica/api/userChara': userChara.handleUserChara,
                '/magica/api/friend': friend.handleFriend,
                '/magica/api/userPiece/': userPiece.handleUserPiece,
                '/magica/api/userPieceSet/': userPieceSet.handleUserPieceSet,
                '/magica/api/userLive2d': userLive2d.handleUserLive2d}
        if flow.request.path.startswith('/magica/api/test/error'):
            flow.response = http.HTTPResponse.make(200, '{"resultCode": "success"}', {})
            return
        if flow.request.path.startswith('/magica/api/page'):
            apiResponse = page.handlePage(flow.request, isLoggingIn)
            if isLoggingIn: isLoggingIn = False
            flow.response = http.HTTPResponse.make(200, apiResponse, {})
        for endpoint in apis.keys():
            if flow.request.path.startswith(endpoint):
                try:
                    apis[endpoint](flow)
                except:
                    flow.response = http.HTTPResponse.make(500, '{"errorTxt": "Had some trouble with '+endpoint+'","resultCode": "error","title": "Error"}', {})
                    raise
        return
        
    if flow.request.path.startswith('/magica'):
        # index.html is the title page -- logins only happen at midnight and when the title page is requested
        if flow.request.path == '/magica/index.html':
            isLoggingIn = True
        serveAsset(flow)

    else:
        flow.response = http.HTTPResponse.make(404, "", {})