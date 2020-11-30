import requests
import flask
import os
import json
import re
import lzma
from threading import Thread
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('app.webcache')

if not os.path.exists('cache'):
    os.mkdir('cache')
if os.path.exists('cache/versions.json'):
    with open('cache/versions.json') as f:
        versions = json.load(f)
else:
    versions = {}

EXPIRATION_TIME = timedelta(hours=8)

# doing this in a separate thread to speed things up
def saveVersions():
    global versions
    with open('cache/versions.json', 'w+') as f:
        json.dump(versions, f)

def cacheFilePath(etag):
    return 'cache/'+etag.strip('"')+'.snaa'

def getRemoteUrl(path):
    asset_type = 'snaa'
    return 'https://endless.snaa.services'+re.sub(r"^(.*)\.json\.gz", r"/magica/resource/download/asset/"+asset_type+r"/\1.json.xz", path)

def decodeFile(body):
    return lzma.decompress(body)

def getFile(path):
    global versions
    logger.info('getting file ' + path)

    RsH = {'Content-Type': 'application/json'}
    RqH = {}
    if path in versions:
        RsH['ETag'] = RqH['If-None-Match'] = versions[path][1]
        cachefile = cacheFilePath(RsH['ETag'])
        if datetime.now() < datetime.fromisoformat(versions[path][0]):
            if os.path.exists(cachefile):
                with open(cachefile, 'rb') as f:
                    snaa_file = f.read()
                return flask.make_response(snaa_file, RsH) # cached response
            flask.abort(500)

    snaa_response = requests.get(getRemoteUrl(path), headers=RqH, verify=False)

    if snaa_response.status_code == 304 or ('If-None-Match' in RqH and snaa_response.headers['ETag'] == RqH['If-None-Match']):
        RsH['ETag'] = snaa_response.headers['ETag']
        cachefile = cacheFilePath(RsH['ETag'])
        if os.path.exists(cachefile):
            versions[path] = ((datetime.now() + EXPIRATION_TIME).isoformat(), RsH['ETag'])
            Thread(target=saveVersions).start()
            with open(cachefile, 'rb') as f:
                snaa_file = f.read()
            return flask.make_response(snaa_file, RsH) # cache renew
        flask.abort(500) # internal error, as we're supposed to have it, but we don't for some odd reason

    if snaa_response.status_code != 200:
        flask.abort(snaa_response.status_code) # 403/404 or something

    snaa_file = decodeFile(snaa_response.content)
    RsH['ETag'] = snaa_response.headers['Etag']
    cachefile = cacheFilePath(RsH['ETag'])

    with open(cachefile, 'wb+') as f:
        f.write(snaa_file)

    versions[path] = ((datetime.now() + EXPIRATION_TIME).isoformat(), RsH['ETag'])
    Thread(target=saveVersions).start()

    return flask.make_response(snaa_file, RsH) # fresh file
