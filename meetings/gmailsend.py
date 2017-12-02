"""
Author: John Nemeth
Sources: google API and web resources
Description: file to hold minor email functions
"""
import httplib2
import email.mime.text
import base64
import arrow

# append additional information to description messaage
def appendMsgToHeader(start, end, title, message, serverport):
    meetdate = arrow.get(start)
    meetdate = meetdate.format("ddd MM/DD")
    meetstart = meetdate.format("h:mm a")
    meetend = arrow.get(end)
    meetend = meetend.format("h:mm a")
    time = " Date/Time: " + meetdate + " " + meetstart + " - " + meetend + '\n'
    newmessage = time + '\n Title: ' + title + '\n\n Description: ' + message
    appSignature = '\n\n Sent using Meeting Invitation app V1 (CIS322 Project 10, UofO) '
    addresslink = '\n http://localhost:' + str(serverport) + ' (link is placeholder for V1 dev build)'
    newmessage = newmessage + appSignature + addresslink
    return newmessage

# create message with gmail requirements of MIME text and base64 encoding
def createMessage(to, subject, message):
  
    message = email.mime.text.MIMEText(message)
    message['to'] = to
    message['from'] = "me"
    message['subject'] = 'Meeting invitation: ' + subject
    message = base64.urlsafe_b64encode(message.as_bytes())
    message = message.decode()
    return {'raw': message} 

# send message with gmail service
def sendMessage(service, message):
  try:
    message = (service.users().messages().send(userId= "me", body=message)
               .execute())
    print ('Message Id: %s' % message['id'])
    return message
  except httplib2.HttpLib2Error:
    print ('An error occurred: %s' % error)
