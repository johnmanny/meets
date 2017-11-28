"""
Revision Author: John Nemeth
Sources: python documentation, class material
DescriptiOn: main file for flask server
"""
import flask
from flask import render_template
from flask import request
from flask import url_for
import uuid
import json
import logging
# Date handling 
import arrow
# for interpreting local times
from dateutil import tz
# OAuth2  - Google library implementation for convenience
from oauth2client import client
# used in oauth2 flow
import httplib2
# Google API for services 
from apiclient import discovery

import times
import agenda

###
# Globals
###
import config
if __name__ == "__main__":
    CONFIG = config.configuration()
else:
    CONFIG = config.configuration(proxied=True)

app = flask.Flask(__name__)
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)
app.secret_key=CONFIG.SECRET_KEY

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = CONFIG.GOOGLE_KEY_FILE  ## You'll need this
APPLICATION_NAME = 'MeetMe class project'

#############################
#  Pages (routed from URLs)
#############################

@app.route("/")
@app.route("/index")
def index():
  app.logger.debug("Entering index")
  if 'begin_date' not in flask.session:
    init_session_values()
  return render_template('index.html')

#######
# huge choose route that deals constantly with valid credentials
#   and auth routing. all input to webpage goes through here and
#   if request method is post, grab eventlist.
@app.route("/choose", methods=['POST', 'GET'])
def choose():
    app.logger.debug("Checking credentials for Google calendar access")
    credentials = valid_credentials()
    if not credentials:
      app.logger.debug("Redirecting to authorization")
      return flask.redirect(flask.url_for('oauth2callback'))
    
    #get calendars before method check to use cal summary
    gcal_service = get_gcal_service(credentials)
    app.logger.debug("Returned from get_gcal_service")
    flask.g.calendars = list_calendars(gcal_service)

    #request is from submission of selected calendars
    if request.method == 'POST':
        calendarids = request.form.getlist('calendar')

        #grab summaries for each calendar id to output as header of events per calendar(in separate module file)     
        calsummaries = getSummaries(calendarids, flask.g.calendars)

        #create events
        events = getEvents(calendarids, calsummaries, credentials, gcal_service)
        flask.g.events = events

        # create list of days
        daysList = agenda.getDayList(flask.session['begin_date'], flask.session['end_date'])

        """
        # populate dict of daysAgenda by calendar summary
        daysAgendaByCal = timeblock.populateDaysAgendaByCal(daysList, events)
        """
        # populate agenda with consolidated events
        daysAgenda = agenda.populateDaysAgenda(daysList, events)
        flask.g.agenda = agenda.getEventsInRange(daysAgenda, flask.session['begin_time'], flask.session['end_time'])

    return render_template('index.html')

###
# ADDED FUNCTION:
# get events, to get events from calendars chosen in template
###
def getEvents(calid, calsum, credentials, service):
    app.logger.debug("Entering getEvents")
    eventsbycalendar = {}
    for count, ids in enumerate(calid):
        events = service.events().list(calendarId=ids,
                                       singleEvents=True,
                                       orderBy='startTime',
                                       timeMin=flask.session['begin_date'],
                                       timeMax=flask.session['end_date']).execute()
        eventclasslist = []
        for event in events['items']:
            if 'transparency' not in event:
                starttime = event['start']
                endtime = event['end']
                
                #to determine whether is all day event or if times specified
                if 'dateTime' in starttime:
                    start = starttime['dateTime']
                    end = endtime['dateTime']
                else:
                    start = starttime['date']
                    end = endtime['date']
                if 'summary' in event:
                    summ = event['summary']
                else:
                    summ = 'no title'
                eventclass = times.timeblock(start, end, 'event', summ)
                
                # to split events if they include multiple days
                passedEvent = agenda.fixEventTimes(eventclass)
                try:
                    for aEvent in passedEvent:
                        eventclasslist.append(aEvent)
                except TypeError:
                    eventclasslist.append(passedEvent)
        
        eventsbycalendar[calsum[count]] = eventclasslist
        app.logger.debug("Leaving getEvents")
    return eventsbycalendar

# ADDED FUNCTION:
# get summaries of calendar from object dict
def getSummaries(calendarid, calendardict):
    calsummaries = []
    for ids in calendarid:
        for calendars in calendardict:
            if ids in calendars['id']:
                calsummaries.append(calendars['summary'])
    return calsummaries

###
# google credential and service object functions
###

#checks for valid credentials
def valid_credentials():
   
    # will eventually redirect to oauth2callback
    if 'credentials' not in flask.session:
      return None
    
    # will convert
    credentials = client.OAuth2Credentials.from_json(
        flask.session['credentials'])
    
    if (credentials.invalid or
        credentials.access_token_expired):
      return None
    return credentials

# retrieve the service object for google calendar
def get_gcal_service(credentials):
  app.logger.debug("Entering get_gcal_service")
  http_auth = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http_auth)
  app.logger.debug("Returning service")
  return service

# oauth2callback directs to google for valid credentials
@app.route('/oauth2callback')
def oauth2callback():
  app.logger.debug("Entering oauth2callback")
  flow =  client.flow_from_clientsecrets(
      CLIENT_SECRET_FILE,
      scope= SCOPES,
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  
  app.logger.debug("Got flow")
  if 'code' not in flask.request.args:
    app.logger.debug("Code not in flask.request.args")
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    app.logger.debug("Code was in flask.request.args")
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    app.logger.debug("Got credentials")
    return flask.redirect(flask.url_for('choose'))

#####
# routes to affect things on page
#####

@app.route('/setrange', methods=['POST'])
def setrange():
    """
    User chose a date range with the bootstrap daterange
    widget.
    """
    app.logger.debug("Entering setrange")  
    flask.flash("Setrange gave us '{}'".format(
      request.form.get('daterange')))
    daterange = request.form.get('daterange')
    flask.session['daterange'] = daterange
    daterange_parts = daterange.split()
    flask.session['begin_date'] = interpret_date(daterange_parts[0])
    flask.session['end_date'] = interpret_date(daterange_parts[2])
    app.logger.debug("Setrange parsed {} - {}  dates as {} - {}".format(
      daterange_parts[0], daterange_parts[1], 
      flask.session['begin_date'], flask.session['end_date']))
    end = arrow.get(flask.session['end_date'])
    end = end.shift(minutes=-1)
    #print('END DATE CEILING: ', end.ceil('day').isoformat())
    flask.session['end_date'] = end.ceil('day').isoformat()
    flask.session["begin_time"] = interpret_time(request.form.get('timestart'))
    flask.session["end_time"] = interpret_time(request.form.get('timeend'))
    return flask.redirect(flask.url_for("choose"))

####
#  Initialize session variables 
####

# must be run in app context. can't call from main
def init_session_values():
    # Default date span = tomorrow to 1 week from now
    now = arrow.now('local')
    tomorrow = now.replace(days=+1)
    nextweek = now.replace(days=+7)
    flask.session["begin_date"] = tomorrow.floor('day').isoformat()
    flask.session["end_date"] = nextweek.ceil('day').isoformat()
    flask.session["daterange"] = "{} - {}".format(
        tomorrow.format("MM/DD/YYYY"),
        nextweek.format("MM/DD/YYYY"))
    # Default time span each day, 8 to 5
    flask.session["begin_time"] = interpret_time("9am")
    flask.session["end_time"] = interpret_time("5pm")

def interpret_time( text ):
    """
    Read time in a human-compatible format and
    interpret as ISO format with local timezone.
    May throw exception if time can't be interpreted. In that
    case it will also flash a message explaining accepted formats.
    """
    app.logger.debug("Decoding time '{}'".format(text))
    time_formats = ["ha", "h:mma",  "h:mm a", "H:mm"]
    try: 
        as_arrow = arrow.get(text, time_formats).replace(tzinfo=tz.tzlocal())
        as_arrow = as_arrow.replace(year=2016) #HACK see below
        app.logger.debug("Succeeded interpreting time")
    except:
        app.logger.debug("Failed to interpret time")
        flask.flash("Time '{}' didn't match accepted formats 13:30 or 1:30pm"
              .format(text))
        raise
    return as_arrow.isoformat()
    #HACK #Workaround
    # isoformat() on raspberry Pi does not work for some dates
    # far from now.  It will fail with an overflow from time stamp out
    # of range while checking for daylight savings time.  Workaround is
    # to force the date-time combination into the year 2016, which seems to
    # get the timestamp into a reasonable range. This workaround should be
    # removed when Arrow or Dateutil.tz is fixed.
    # FIXME: Remove the workaround when arrow is fixed (but only after testing
    # on raspberry Pi --- failure is likely due to 32-bit integers on that platform)


def interpret_date( text ):
    """
    Convert text of date to ISO format used internally,
    with the local time zone.
    """
    try:
      as_arrow = arrow.get(text, "MM/DD/YYYY").replace(
          tzinfo=tz.tzlocal())
    except:
        flask.flash("Date '{}' didn't fit expected format 12/31/2001")
        raise
    return as_arrow.isoformat()

def next_day(isotext):
    """
    ISO date + 1 day (used in query to Google calendar)
    """
    as_arrow = arrow.get(isotext)
    return as_arrow.replace(days=+1).isoformat()

####
#
#  Functions (NOT pages) that return some information
#
####
  
def list_calendars(service):
    app.logger.debug("Entering list_calendars")  
    calendar_list = service.calendarList().list().execute()["items"]
    result = [ ]
    for cal in calendar_list:
        kind = cal["kind"]
        id = cal["id"]
        if "description" in cal: 
            desc = cal["description"]
        else:
            desc = "(no description)"
        
        summary = cal["summary"]
        # Optional binary attributes with False as default
        selected = ("selected" in cal) and cal["selected"]
        primary = ("primary" in cal) and cal["primary"]

        result.append(
          { "kind": kind,
            "id": id,
            "summary": summary,
            "selected": selected,
            "primary": primary
            })
        app.logger.debug("Leaving list_calendars")
    return sorted(result, key=cal_sort_key)


def cal_sort_key( cal ):
    """
    Sort key for the list of calendars:  primary calendar first,
    then other selected calendars, then unselected calendars.
    (" " sorts before "X", and tuples are compared piecewise)
    """
    if cal["selected"]:
       selected_key = " "
    else:
       selected_key = "X"
    if cal["primary"]:
       primary_key = " "
    else:
       primary_key = "X"
    return (primary_key, selected_key, cal["summary"])


#################
#
# Functions used within the templates
#
#################

@app.template_filter( 'fmtdate' )
def format_arrow_date( date ):
    try: 
        normal = arrow.get( date )
        return normal.format("ddd MM/DD")
    except:
        return "(bad date)"

@app.template_filter( 'fmttime' )
def format_arrow_time( time ):
    try:
        normal = arrow.get( time )
        return normal.format("HH:mm")
    except:
        return "(bad time)"
    
#############


if __name__ == "__main__":
  # App is created above so that it will
  # exist whether this is 'main' or not
  # (e.g., if we are running under green unicorn)
  app.run(port=CONFIG.PORT,host="0.0.0.0")
    
