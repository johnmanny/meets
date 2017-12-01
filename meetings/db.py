"""
author: John Nemeth
sources: Heavy reference from starter code, previous assignments
description: file for database functions to be used by flask_main
"""

from pymongo import MongoClient
from bson.objectid import ObjectId
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
                    "invitees": invitees,
                    "status": 'pending'
                  }
    collection.insert_one(newmeeting)

#func to remove from DB
def removefromDB(datetime):
    memodate = arrow.get(datetime).naive
    collection.delete_one({ "date": memodate})

# check if meeting is confirmed (all invites approved)
def checkMeetingConfirm(idsDict):
    meeting = collection.find_one({ '_id': ObjectId(idsDict['meetID']) })

    if meeting['status'] == 'pending':
        if all(invitee['status'] == 'accepted' for invitee in meeting['invitees']):
            meeting['status'] = 'confirmed'
    collection.save(meeting)

# modify status of invitee to accepted or rejected
def modifyStatus(idsDict, changeto):
    """
    # idsDict : { 'inviteID': 'calendarid', 'meetID': 'objID }
    collection.find_one_and_update( {'_id': ObjectId(idsDict['meetID']) },
                           {'invitees': { idsDict['inviteID'] :
    """
    record = collection.find_one({ '_id' : ObjectId(idsDict['meetID']) })
    for invitee in record['invitees']:
        if invitee['id'] == idsDict['inviteID']:
            invitee['status'] = changeto
    collection.save(record)

# func to return list of meetings
def getMeetings():
    records = []
    for record in collection.find({ "type": "meeting" }).sort('start'):
        records.append(record)
    return records

# get list of meeting owners
def getOwners():
    records = getMeetings()
    ownerList = []
    for meeting in records:
        ownerList.append(meeting['owner'])
    return ownerList

# get list of meeting invitiees
def getInvitees():
    records = getMeetings()
    inviteeList = []
    for meeting in records:
        for invitee in meeting['invitees']:
            inviteeList.append(invitee)
    return inviteeList

# to implement flask variable used to check if should put 'list' button in template 
def checkIsOwner(calendars):
    ownerlist = getOwners()
    for calendar in calendars:
        if calendar['id'] in ownerlist:
            return True

    return False

# check if any owned calendar is invitee to meeting
def checkIsInvited(calendars):
    invitees = getInvitees()
    for cal in calendars:
        for invitee in invitees:
            if invitee['id'] == cal['id']:
                return True

    return False


# separate new meetinglist based on ownership of meetings
def getOwnedMeetings(ownedcals):
    meetinglist = getMeetings()
    ownedmeetings = []
    for meeting in meetinglist:
        if meeting['owner'] in ownedcals:
           ownedmeetings.append(meeting)
    
    return ownedmeetings


#separate meetinglist based on invitee status of meetings
def getInvitedMeetings(ownedcals):
    records = getMeetings()
    invitedmeetings = []
    for meeting in records:
        meetingappended = False
        for invitee in meeting['invitees']:
            if invitee['id'] in ownedcals and meetingappended == False:
                invitedmeetings.append(meeting)
                meetingappended = True
    return invitedmeetings
