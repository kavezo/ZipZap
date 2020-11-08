import flask
app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False

import os
import shutil
if not os.path.exists('./data/user/'):
    print('Copying over default user...')
    shutil.copytree('data/default_user', 'data/user')

from api import friend, gacha, gameUser, money, page, quest, shop, \
    user, userCard, userChara, userDeck, userLive2d, userPiece, userPieceSet, arena,logger
    
app.add_url_rule('/page/<path:endpoint>', view_func=page.handlePage, methods=['GET', 'POST'])
app.add_url_rule('/friend/<path:endpoint>', view_func=friend.handleFriend, methods=['GET', 'POST'])
app.add_url_rule('/gacha/<path:endpoint>', view_func=gacha.handleGacha, methods=['GET', 'POST'])
app.add_url_rule('/money/<path:endpoint>', view_func=money.handleMoney, methods=['GET', 'POST'])
app.add_url_rule('/gameUser/<path:endpoint>', view_func=gameUser.handleGameUser, methods=['GET', 'POST'])
app.add_url_rule('/quest/<path:endpoint>', view_func=quest.handleQuest, methods=['GET', 'POST'])
app.add_url_rule('/shop/<path:endpoint>', view_func=shop.handleShop, methods=['GET', 'POST'])
app.add_url_rule('/arena/<path:endpoint>', view_func=arena.handleArena, methods=['GET', 'POST'])

app.add_url_rule('/user/<path:endpoint>', view_func=user.handleUser, methods=['GET', 'POST'])
app.add_url_rule('/userCard/<path:endpoint>', view_func=userCard.handleUserCard, methods=['GET', 'POST'])
app.add_url_rule('/userChara/<path:endpoint>', view_func=userChara.handleUserChara, methods=['GET', 'POST'])
app.add_url_rule('/userDeck/<path:endpoint>', view_func=userDeck.handleUserDeck, methods=['GET', 'POST'])
app.add_url_rule('/userLive2d/<path:endpoint>', view_func=userLive2d.handleUserLive2d, methods=['GET', 'POST'])
app.add_url_rule('/userPiece/<path:endpoint>', view_func=userPiece.handleUserPiece, methods=['GET', 'POST'])
app.add_url_rule('/userPieceSet/<path:endpoint>', view_func=userPieceSet.handleUserPieceSet, methods=['GET', 'POST'])
app.add_url_rule('/test/logger/error', view_func=logger.handleError, methods=['POST'])

@app.route('/search/<path:endpoint>', methods=['GET', 'POST'])
def dummysearch(endpoint):
    return flask.jsonify({
        "_shards": {
            "failed": 0,
            "successful": 0,
            "total": 0
        },
        "hits": {
            "hits": [],
            "max_score": 0,
            "total": 0
        },
        "timed_out": False,
        "took": 2
    })

if __name__ == "__main__":
    app.run(host='127.0.0.1')
