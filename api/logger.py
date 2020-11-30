import flask
import json
from datetime import datetime
import logging

log = logging.getLogger('app.logger')

def handleError():
    log.error(f"App logged error: {str(flask.request.data)}")
    return {}
