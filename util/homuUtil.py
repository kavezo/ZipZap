# welcome to microservice naming 101
# homuUtil is homuUtil because homuhomu controls time

from datetime import datetime, timedelta
import math

from util import dataUtil as dt

DATE_FORMAT = '%Y/%m/%d %H:%M:%S'

def nowstr():
    return (datetime.now()).strftime(DATE_FORMAT)

def updateStatus(status, now):
    maxstatus = dt.getUserObject('userStatusList', 'MAX_' + status['statusId'])
    if maxstatus is not None and status['point'] < maxstatus['point']:
        minutesPassed = (now-datetime.strptime(status['checkedAt'], DATE_FORMAT)) / timedelta(minutes=1)
        recoverPoints = math.floor(status['periodicPoint'] * (minutesPassed/status['checkPeriod']))
        status['point'] += recoverPoints # yum mutability

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