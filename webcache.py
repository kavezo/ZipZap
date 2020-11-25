import requests
import flask
import os
import json
import re
import lzma
from multiprocessing import Process
from datetime import datetime, timedelta

if not os.path.exists('cache'):
    os.mkdir('cache')
if os.path.exists('cache/versions.json'):
    with open('cache/versions.json') as f:
        versions = json.load(f)
else:
    versions = {}

EXPIRATION_TIME = timedelta(days=7)

# doing this in a separate thread to speed things up
def saveVersions():
    global versions
    with open('cache/versions.json', 'w+') as f:
        json.dump(versions, f)

def getFile(path):
    global versions
    print('getting file ' + path)

    if path in versions:
        if datetime.now() < datetime.fromisoformat(versions[path][0]):
            if os.path.exists('cache/'+path):
                return flask.send_from_directory('cache', path) 
            flask.abort(500)
        headers = {'Etag': versions[path][1]}
    else:
        headers = {}

    fullpath = 'https://endless.snaa.services/'+re.sub(r"^magica/resource/download/asset/master/(.*)\.json\.gz", r"magica/resource/download/asset/snaa/\1.json.xz", path)
    snaa_response = requests.get(fullpath, headers=headers, verify=False)

    if snaa_response.status_code == 304 or ('Etag' in headers and snaa_response.headers['Etag'] == headers['Etag']):
        if os.path.exists('cache/'+path):
            return flask.send_from_directory('cache', path) # TODO: headers
        flask.abort(500) # internal error, as we're supposed to have it, but we don't for some odd reason

    if snaa_response.status_code != 200:
        flask.abort(snaa_response.status_code, headers=snaa_response.headers)

    # we don't do that here
    #if 'Content-Encoding' in snaa_response.headers: headers['Content-Encoding'] = snaa_response.headers['Content-Encoding']
    #if 'Content-Length' in snaa_response.headers: headers['Content-Length'] = snaa_response.headers['Content-Length']

    snaa_file = lzma.decompress(snaa_response.content)

    headers['Content-Type'] = 'application/json'
    headers['Content-Length'] = len(snaa_file)
    headers['Etag'] = snaa_response.headers['Etag']

    dirs = 'cache/'+os.path.split(path)[0]
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    with open('cache/'+path, 'wb+') as f:
        f.write(snaa_file)

    versions[path] = ((datetime.now() + EXPIRATION_TIME).isoformat(), snaa_response.headers['Etag'])
    Process(target=saveVersions).start()

    return flask.make_response(snaa_file, headers)


