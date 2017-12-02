# proj10-meetings
Setting up meetings for between google calendar users

## Usage:



## Description:

***Revision Author:*** John Nemeth

***Sources:*** Previous projects, class material, API documentation 
and example code.

***Functionality:*** V1 Dev build is only guarenteed to work in -8 GMT.
App developed utilizing multiple calendars owned between 2 or 3 accounts.
Comparisons between calendars are made using the accessrole of the
given calendar. So, when invitations are managed, the accessrole the 
logged in account has (logged in through oauth2 system for google cals)
is used to determine who (aka what calendar) owns the meeting that is 
proposed. The owner of the event is the only one who can see each person 
(aka calendar) who was invited to the meeting. Invitees (aka calendars) 
can only accept or reject the invitation to the meeting (it starts out pending).
When the meeting is created, a record of it is stored on a mongoDB database.

