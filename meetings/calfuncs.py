"""
author: John Nemeth
sources: class material
description: some functions for common calendar operations
"""

####
# split invitee id and meeting id
def splitIds(ids):
    parts = ids.split(',')
    newIds = { 'inviteID': parts[0],
               'meetID': parts[1]
             }
    return newIds

##
# create dict of owned cals from HTML
def getCalsFromHTML(calendars):
    
    calsdict = {} 
    for cal in calendars:
       calparts = []
       calparts = cal.split(',')
       calsdict[calparts[0]] = calparts[1]

    return calsdict

##
# create dict of selected cals for storing in session 
def getSelectedCals(calendars):
    ##
    # Calsdict layout: 
    # calsdict = {'longcalendarid':'calendarsummary',
    #             'longcalid2': 'calsum2', ...
    #            } 
    calsdict = {} 
    for cal in calendars:
       calparts = []
       calinfo = []
       calparts = cal.split(',')
       calinfo.append(calparts[1])
       calinfo.append(calparts[2])
       calsdict[calparts[0]] = calinfo

    return calsdict

##
# Split summaries and ids of selected cals to different lists
#   to keep compatability with current implementation.
#   Will eventually need refactoring.
def getIdsAndSums(calsdict):
    calsums = []
    calids = []
    for ids, info in calsdict.items():
        calsums.append(info[0])
        calids.append(ids)

    return calsums, calids

##
# get owned calendars from calendarlist
def getOwnedCals(cals):
    newcals = []
    for cal in cals:
        if cal['accessrole'] == 'owner':
            newcals.append(cal)

    return newcals
