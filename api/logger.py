import flask
import json
from datetime import datetime


def handleError():
    print(f"App logged error: {str(flask.request.data)}")
    return {}
