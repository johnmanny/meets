"""
author: John Nemeth
sources: Heavy reference from starter code, previous assignments
description: file for database functions to be used by flask_main
"""

#import pymongo
from pymongo import MongoClient
import arrow

#for config variables
import flask_main

#mongo URL
MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    flask_main.CONFIG.DB_USER,
    flask_main.CONFIG.DB_USER_PW,
    flask_main.CONFIG.DB_HOST, 
    flask_main.CONFIG.DB_PORT, 
    flask_main.CONFIG.DB)
print("Using URL '{}'".format(MONGO_CLIENT_URL))

# database connection for every server process
try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, flask_main.CONFIG.DB)
    collection = db.dated
except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

##########
# database functions accessed by flask_main

#func to enter in DB
def enterinDB(title, desc, start, end, ownerid, ownersum, invitees):
    rejected = []
    accepted = []
    newmeeting  = { "type": "meeting",
                    "title": title,
                    "desc": desc,
                    "start": start,
                    "end": end,
                    "owner": ownerid,
                    "ownersummary": ownersum,
                    "invitees": invitees
                  }
    collection.insert_one(newmeeting)

#func to remove from DB
def removefromDB(datetime):
    memodate = arrow.get(datetime).naive
    collection.delete_one({ "date": memodate})

#func to return list of memos
def getMeetings():
    records = []

    for record in collection.find({ "type": "meeting" }).sort('start'):
        del record['_id']
        records.append(record)
    return records

# get list of calendar owners
def getOwners(records):
    
    ownerList = []
    for meeting in records:
        ownerList.append(meeting['owner'])
    return ownerList

# to implement flask variable used to check if should put 'list' button in template 
def checkIsOwner(ownerlist, calendardict):
    
    for calendar in calendardict:
        if calendar['accessrole'] == 'owner' and calendar['id'] in ownerlist:
            return True

    return False

# separate new meetinglist based on ownership of meetings
def getOwnedMeetings(meetinglist, caldict):
    newmeetinglist = []
    for meeting in meetinglist:
        for cal, sumAndRole in caldict.items():
            if cal == meeting['owner'] and sumAndRole[1] == 'owner':
                newmeetinglist.append(meeting)
    print('NEW MEETING LIST: ', newmeetinglist)
    return newmeetinglist

