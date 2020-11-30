# welcome to microservice naming 101
# homuUtil is homuUtil because homuhomu controls time

from datetime import datetime, timedelta, date
import math

from util import dataUtil as dt

DATE_FORMAT = '%Y/%m/%d %H:%M:%S'

def thisWeek():
    today = date.today()
    lastMonday = today - timedelta(days=today.weekday())
    nextMonday = lastMonday + timedelta(weeks=1)
    return lastMonday, nextMonday

def nowstr():
    return datetime.now().strftime(DATE_FORMAT)

def updateStatus(status, now):
    maxstatus = dt.getUserObject('userStatusList', 'MAX_' + status['statusId'])
    if maxstatus is not None and status['point'] < maxstatus['point']:
        minutesPassed = (now-datetime.strptime(status['checkedAt'], DATE_FORMAT)) / timedelta(minutes=1)
        recoverPoints = math.floor(status['periodicPoint'] * (minutesPassed/status['checkPeriod']))
        status['point'] = min(status['point'] + recoverPoints, maxstatus['point'])

    status['checkedAt'] = now.strftime(DATE_FORMAT)
    status['createdAt'] = now.strftime(DATE_FORMAT)

    dt.setUserObject('userStatusList', status['statusId'], status)
    return status

def getStatus(statusId):
    status = dt.getUserObject('userStatusList', statusId)
    now = datetime.now().replace(microsecond=0)
    return updateStatus(status, now)

def getAllStatuses():
    allStatuses = dt.readJson('data/user/userStatusList.json')
    now = datetime.now().replace(microsecond=0)
    return [updateStatus(status, now) for status in allStatuses]

# currently unused, but will be great for events
def filterCurrValid(objectList, startKey=None, endKey=None):
    validObjects = []
    now = datetime.now().replace(microsecond=0)

    for objectDict in objectList:
        afterStart = True
        if startKey is not None:
            if type(startKey) == str: start = objectDict[startKey]
            if callable(startKey): start = startKey(objectDict)
            if type(start) == str: start = datetime.strptime(start, DATE_FORMAT)
            afterStart = now >= start

        beforeEnd = True
        if endKey is not None:
            if type(endKey) == str: end = objectDict[endKey]
            if callable(endKey): end = endKey(objectDict)
            if type(end) == str: end = datetime.strptime(end, DATE_FORMAT)
            beforeEnd = now <= end
        
        if afterStart and beforeEnd:
            validObjects.append(objectDict)
    
    return validObjects