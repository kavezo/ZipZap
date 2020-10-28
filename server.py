from mitmproxy import http
from mitmproxy.script import concurrent
import requests
import os
import json
from getUserData import data1, data2
from api import page, gacha, user, gameUser, userCard, userChara, friend, userPiece, \
    userPieceSet, userLive2d, money, shop, userDeck, quest

isLoggingIn = False
etag = 'thisisanetag'

def serveAsset(flow):
    with open('config.json') as f:
        diskAssets = json.load(f)['diskAssets']
    versionless = flow.request.path.split('?')[0]

    if versionless.endswith('.json.gz'):
        if flow.request.headers['if-none-match'] == etag:
            flow.response = http.HTTPResponse.make(304, "", {})
            return
    
    isAnnouncement = 'json/announcements' in flow.request.path

    if not diskAssets or not os.path.exists('assets'+versionless) or isAnnouncement:

        if diskAssets and not os.path.exists(os.path.dirname('assets'+versionless)) and not isAnnouncement:
            os.makedirs(os.path.dirname('assets'+versionless))

        asset_request = requests.get('https://zipzap-assets.s3.us-east-2.amazonaws.com'+flow.request.path)
        if asset_request.status_code == 200:
            flow.response = http.HTTPResponse.make(200, asset_request.content, {'etag': etag})
            if diskAssets and not isAnnouncement:
                print('writing to assets' + versionless)
                with open('assets'+versionless, 'wb+') as f:
                    f.write(asset_request.content)
        else:
            asset_request = requests.get('https://en.rika.ren'+flow.request.path)
            print('not on S3, requested ' + 'https://en.rika.ren' + flow.request.path)
            if asset_request.status_code == 200:
                flow.response = http.HTTPResponse.make(200, asset_request.content, {'etag': etag})
                if diskAssets and not isAnnouncement:
                    print('writing to assets' + versionless)
                    with open('assets'+versionless, 'wb+') as f:
                        f.write(asset_request.content)
            else:
                print('couldn\'t find on S3 or rika.ren D:')
                flow.response = http.HTTPResponse.make(asset_request.status_code, asset_request.content, {})
    else:
        with open('assets'+versionless, 'rb') as f:
            text = f.read()
        flow.response = http.HTTPResponse.make(200, text, {'etag': etag})

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
                '/magica/api/userLive2d': userLive2d.handleUserLive2d,
                '/magica/api/money': money.handleMoney,
                '/magica/api/shop': shop.handleShop,
                '/magica/api/userDeck': userDeck.handleUserDeck,
                '/magica/api/quest': quest.handleQuest}
        if flow.request.path.startswith('/magica/api/test/logger/error'):
            flow.response = http.HTTPResponse.make(200, '{"resultCode": "success"}', {})
            return
        if flow.request.path.startswith('/magica/api/page'):
            apiResponse = page.handlePage(flow, isLoggingIn)
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