"""
Author: John Nemeth
Sources: google API and web resources
Description: file to hold minor email functions
"""
import httplib2
import email.mime.text
import base64
import arrow

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
    

def createMessage(to, subject, message):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = email.mime.text.MIMEText(message)
  message['to'] = to
  message['from'] = "me"
  message['subject'] = 'Meeting invitation: ' + subject
  message = base64.urlsafe_b64encode(message.as_bytes())
  message = message.decode()
  return {'raw': message} 

def sendMessage(service, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId= "me", body=message)
               .execute())
    print ('Message Id: %s' % message['id'])
    return message
  except httplib2.HttpLib2Error:
    print ('An error occurred: %s' % error)
