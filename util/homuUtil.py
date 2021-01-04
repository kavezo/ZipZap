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

def strToDateTime(time): return datetime.strptime(time, DATE_FORMAT)

def beforeToday(time):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return datetime.strptime(time, DATE_FORMAT) < today

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

def pruneLabyrinths(userSectionList=[], userQuestBattleList=[]):
    from util import newUserObjectUtil as newtil # importing here to avoid circular imports

    todayIndex = min(6, date.today().weekday() + 1) # because Saturday and Sunday are both 6

    # delete existing sections and battles for other days
    for dayIndex in range(1, 7):
        removeSections = [i for i in range(len(userSectionList)) 
                    if str(userSectionList[i]['sectionId']).startswith(f'4000{dayIndex}')]

        if dayIndex != todayIndex:
            for i in reversed(sorted(removeSections)):
                del userSectionList[i]

        # if these are today's quests and they don't exist yet, make them
        elif len(removeSections) == 0 and len(userSectionList)>0:
            for labType in range(1, 3):
                sectionId = int(f'4000{dayIndex}{labType}')
                newSection, _ = newtil.createUserSection(sectionId)
                dt.setUserObject('userSectionList', sectionId, newSection)
                userSectionList.append(newSection)

        removeBattles = [i for i in range(len(userQuestBattleList)) 
                    if str(userQuestBattleList[i]['questBattleId']).startswith(f'4000{dayIndex}')]

        if dayIndex != todayIndex:
            for i in reversed(sorted(removeBattles)):
                del userQuestBattleList[i]

        elif len(removeBattles) == 0 and len(userQuestBattleList)>0:
            for labType in range(1, 3):
                for j in range(1, 5): # for each level
                    battleId = int(f'4000{dayIndex}{labType}{j}')
                    newBattle, _ = newtil.createUserQuestBattle(battleId)
                    dt.setUserObject('userQuestBattleList', battleId, newBattle)
                    userQuestBattleList.append(newBattle)

    return userSectionList, userQuestBattleList

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
    lastMonth = today.month - 1
    skipTypes = ['PIECE', 'MAXPIECE', 'FORMATION_SHEET', 'CARD'] # afaik these don't need to be reset...

    shopList = dt.readJson('data/shopList.json')

    # figure out if it needs to be reset (reset date is not this month), then reset it
    # kinda hacky way to get the last time the shop was reset
    # finds the first limited (and available) item in the mirrors coins shop, then takes its end time
    for shopItem in shopList[1]['shopItemList']:
        if 'endAt' in shopItem:
            shopExpiryTime = shopItem['endAt']
            if shopExpiryTime != "2050/01/01 00:00:00":
                continue
            elif datetime.strptime(shopExpiryTime, DATE_FORMAT).month == today.month:
                return
            else:
                break
            
    if datetime.strptime(shopExpiryTime, DATE_FORMAT).month == today.month:
        return

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
        endOfMonth = ((endOfMonth - timedelta(days=endOfMonth.day)).replace(hour=23, minute=59, second=59)).strftime(DATE_FORMAT)
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

            # also need to clear out the user's history
            dt.deleteUserObject('userShopItemList', newItem['id'])
        
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