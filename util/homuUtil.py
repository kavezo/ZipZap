# welcome to microservice naming 101
# homuUtil is homuUtil because homuhomu controls time

from datetime import datetime, timedelta, date
import math
import copy
import schedule
import threading
import time

from util import dataUtil as dt
import logging

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

# ------ Cron jobs ------

def resetShop():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if today.day != 1:
        return
    lastMonth = (today - timedelta(days=1)).month
    skipTypes = ['PIECE', 'MAXPIECE', 'FORMATION_SHEET', 'CARD']

    shopList = dt.readJson('data/shopList.json')
    for shopIdx in range(4): # magia chips, mirrors coins, support pts, daily coins
        shopItems = shopList[shopIdx]['shopItemList']
        deleteIdxs = [i for i in range(len(shopItems)) 
            if 'endAt' in shopItems[i] 
                and (datetime.strptime(shopItems[i]['endAt'], DATE_FORMAT).month == lastMonth
                    or datetime.strptime(shopItems[i]['endAt'], DATE_FORMAT).year < today.year)
                and not shopItems[i]['shopItemType'] in skipTypes]
        for i in reversed(deleteIdxs):
            del shopItems[i]
        
        # from Stack Overflow
        endOfMonth = today.replace(day=28) + timedelta(days=4)
        endOfMonth = (endOfMonth - timedelta(days=endOfMonth.day).replace(hour=23, minutes=59, seconds=59)).strftime(DATE_FORMAT)
        newItems = []

        alreadyCopied = set([])
        for item in shopItems:
            if 'endAt' not in item \
                or item['endAt']!= "2050/01/01 00:00:00" \
                or item['shopItemType'] in skipTypes \
                or item['genericId'] in alreadyCopied:
                continue
            alreadyCopied.add(item['genericId'])
            newItem = copy.deepcopy(item)
            newItem['startAt'] = today.strftime(DATE_FORMAT)
            newItem['endAt'] = endOfMonth

            newItems.append(newItem)
        
        shopList[shopIdx]['shopItemList'] += newItems
    
    dt.saveJson('data/shopList.json', shopList)

def changeLogName():
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
    logLevel = dt.readJson('config.json')['logLevel']
        
    date = nowstr().split(' ')[0].replace('/', '_')
    hour = datetime.now().hour
    logging.basicConfig(
        level=logLevel,
        filename='logs/{0}-{1}.log'.format(date, hour), 
        format='%(asctime)s %(levelname)s %(name)s : %(message)s')

def cronThread():
    while True:
        try:
            time.sleep(1)
            schedule.run_pending()
        except:
            return

def startCron():
    changeLogName()
    resetShop()

    schedule.every().hour.at(':00').do(changeLogName)
    schedule.every().day.at('00:00').do(resetShop) # can't make it happen only once a month, but at least we can check every day

    thread = threading.Thread(target=cronThread)
    thread.start()