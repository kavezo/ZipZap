import requests
import flask
import os
import json
from multiprocessing import Process

if not os.path.exists('cache'):
    os.mkdir('cache')
if os.path.exists('cache/versions.json'):
    with open('cache/versions.json') as f:
        versions = json.load(f)
else:
    versions = {}

# doing this in a separate thread to speed things up
def saveVersions():
    global versions
    with open('cache/versions.json', 'w+') as f:
        json.dump(versions, f)

def getFile(path):
    global versions

    if path in versions:
        headers = {'Etag': versions[path]}
    else:
        headers = {}
    snaa_response = requests.get('https://endless.snaa.services'+path, headers=headers)

    if snaa_response.status_code == 304 or ('Etag' in headers and snaa_response.headers['Etag'] == headers['Etag']):
        if os.path.exists('cache/'+path):
            return flask.send_from_directory('cache', path)
        flask.abort('304')

    if 'Content-Encoding' in snaa_response.headers: headers['Content-Encoding'] = snaa_response.headers['Content-Encoding']
    if 'Content-Length' in snaa_response.headers: headers['Content-Length'] = snaa_response.headers['Content-Length']

    versions[path] = snaa_response.headers['Etag']
    Process(target=saveVersions).start()

    return flask.make_response(snaa_response.content, headers)


