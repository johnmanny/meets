# Meets
This project sets up meetings by analyzing the busy times of google calendars
and producing freetime slots which users can email directly to potential
attendees. Intended for usage in -8 GMT.

## Usage:
A user clicks to begin on the homescreen and specifies a date and time
range to look for free times between selected calendars in a list of
highlighted calendars that the user has. These calendars are not required 
to be owned by the user (meaning they could be read-only calendars other
people own). When a freetime is chosen, the user has the option to add emails
to receive the meeting invitation built. In the meeting invitation, the date and 
time of the meeting can be fine-tuned from the freetime that was initially chosen.

## Description:

***Author:*** John Nemeth

***Sources:*** Previous projects, class material, API documentation,
and other sources specifically listed in files.

***Unoriginal Files:*** LICENSE is unmodified and from prior iterations of the project.
config.py, and Makefile has minor modifications from a templage given in the class. flask_main.py heavily modified from
template given in prior project. All other files are original (outside of API documentation examples and specific 
sources listed in header of files)

***Functionality:*** V1 Dev build is only designed to work with -8 GMT events
and calendars(hence only one time sent in generated email). App developed utilizing multiple calendars owned between 2 
or 3 accounts. Comparisons between calendars are made using the accessrole of the
given calendar. So, when invitations are managed, the accessrole the 
logged in account has (logged in through oauth2 system for google cals)
is used to determine who (aka what calendar) owns the meeting that is 
proposed. The owner of the event is the only one who can see each person 
(aka calendar) who was invited to the meeting. Invitees (aka calendars) 
can only accept or reject the invitation to the meeting (it starts out pending).
When the meeting is created, a record of it is stored on a mongoDB database.
When all meeting invitations are accepted, the meeting status changes from
'pending' to 'confirmed'. Users have the option to list recipients of emails
in the meeting invitiation field. The email will be sent from the gmail connected
to the authed user. All authorization of users and security is handled by google's
services and their requirements.
