import requests
import flask
import os
import json
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
    snaa_response = requests.get('http://endless.snaa.services/'+path, headers=headers)

    if snaa_response.status_code == 304 or ('Etag' in headers and snaa_response.headers['Etag'] == headers['Etag']):
        if os.path.exists('cache/'+path):
            return flask.send_from_directory('cache', path)
        flask.abort(500) # internal error, as we're supposed to have it, but we don't for some odd reason
    
    if snaa_response.status_code != 200:
        flask.abort(snaa_response.status_code, headers=snaa_response.headers)

    if 'Content-Encoding' in snaa_response.headers: headers['Content-Encoding'] = snaa_response.headers['Content-Encoding']
    if 'Content-Length' in snaa_response.headers: headers['Content-Length'] = snaa_response.headers['Content-Length']

    dirs = 'cache/'+os.path.split(path)[0]
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    with open('cache/'+path, 'wb+') as f:
        f.write(snaa_response.content)

    versions[path] = ((datetime.now() + EXPIRATION_TIME).isoformat(), snaa_response.headers['Etag'])
    Process(target=saveVersions).start()

    return flask.make_response(snaa_response.content, headers)


