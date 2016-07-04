# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 00:19:23 2015

@author: Glenn
"""

import imaplib
import email
import emailKeys
import time
import dateutil.parser as parser
import checkin
import pytz
import messages
from threading import Timer
import datetime
import threading
import Queue
import smtplib
from email.mime.text import MIMEText
import re
import enchant
import timezoneParser

username = emailKeys.username
password = emailKeys.password
nyc = pytz.timezone("America/New_York")
deltaTime = datetime.timedelta(days=1,microseconds=50)
queue = Queue.Queue()

def signIn(verbose=False):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username,password)
    if verbose:
        print('Signed into ' + username)
    return mail

def getSenderFromEmail(emailData):
    msg = email.message_from_string(emailData[0][1])
    sender = msg['From'][msg['From'].find('<')+1:
                         msg['From'].find('>')]
    return sender

def getUnreadMessages(mail):
    mail.select()
    typ, data = mail.search(None,'UnSeen')
    if (len(data) == 1) and data[0] == '':
        data = []
    return data

def getEmailText(emailRaw):
    try:
        emailStringRaw = emailRaw.decode('utf-8')
    except:
        emailStringRaw = emailRaw.decode()
    emailMessage = email.message_from_string(emailStringRaw)
    emailString = []
    for part in emailMessage.walk():
        if part.get_content_type() == 'text/plain':
            body = part.get_payload(decode=True)
            try:
                emailString.append(body.decode('utf-8'))
            except:
                emailString.append(body)
    return emailString

def getEmailType(emailData):
    subject = email.message_from_string(emailData[0][1])['Subject']
    if 'Gmail Forwarding Confirmation' in subject:
        messageType = 'Gmail Forwarding'
    elif 'Your trip is around the corner' in subject:
        messageType = 'Southwest Confirmation'
    elif 'Ticketless Travel Passenger Itinerary' in subject:
        messageType = 'Southwest Confirmation'
    elif 'Flight reservation' in subject:
        messageType = 'Info In Subject'
    elif 'UPDATED flight reservation' in subject:
        messageType = 'Info In Subject'
    else:
        messageType = 'Unknown'
    return messageType
    
def getGmailForwardInfo(emailData):
    msgTextList = getEmailText(emailData[0][1])
    for msgText in msgTextList:
        if 'Confirmation code:' in msgText:
            strIndexStart = msgText.find('Confirmation code:')+19
            confCode = str(msgText[strIndexStart:strIndexStart+\
                           msgText[strIndexStart:strIndexStart+50].find('\r')])
        if 'has requested' in msgText:
            toaddr = str(msgText[0:msgText.find('has requested')-1])
    try:
        message = messages.gmailForwardingSendCode(confCode)
        info = {'message':message,
                'toaddr':toaddr}
    except:
        message = messages.problemWithGmailForwarding()
        info = {'message':message,
                'toaddr':''}
        print('Problem getting confirmation code from gmail forwarding')        
    return info
        
def getConfNum(msgText):
    #get the confirmation number
    if 'confNum=' in msgText:
        strIndexStart = msgText.find('confNum=')+8
        strIndexEnd = strIndexStart+6
        confNum = str(msgText[strIndexStart:strIndexEnd])
    else:
        #get dictionary
        d = enchant.Dict("en_US")
        pattern = re.compile(r'(?<![A-Za-z0-9])[A-Z0-9]{6}(?![A-Za-z0-9])')
        msgTextConfNumSearch = msgText[200:]
        regExSearch = pattern.search(msgTextConfNumSearch)
        while regExSearch:
            #see if the found string is a real word
            possibleConfNum = regExSearch.group()
            if not d.check(possibleConfNum):
                confNum = str(possibleConfNum)
                break
            else:
                msgTextConfNumSearch = msgTextConfNumSearch[regExSearch.end():]
                regExSearch = pattern.search(msgTextConfNumSearch)
    return confNum

def getCheckInTime(msgText):
    if 'Southwest Airlines at *' in msgText:
        strIndexStart = msgText.find('Southwest Airlines at *')+23
        checkInTime = msgText[strIndexStart:strIndexStart+\
                      msgText[strIndexStart:strIndexStart+10].find('*')]
        #see if there is another checkInTime
        if 'Southwest Airlines at *' in msgText[strIndexStart+1:]:
            strIndexStart = msgText[strIndexStart+1:].find('Southwest Airlines at *')+ \
                            23+strIndexStart+1
            checkInTime = [checkInTime, msgText[strIndexStart:strIndexStart+\
                           msgText[strIndexStart:strIndexStart+10].find('*')]]
        else:
            checkInTime = [checkInTime]
    else:
        strIndexStart = msgText.find('Southwest Airlines at') + 22
        checkInTime = str(msgText[strIndexStart:strIndexStart+\
                        msgText[strIndexStart:strIndexStart+10].find(' ')])
                    #see if there is another checkInTime
        if 'Southwest Airlines at' in msgText[strIndexStart+1:]:
            strIndexStart = msgText[strIndexStart+1:].find('Southwest Airlines at')+ \
                            22+strIndexStart+1
            checkInTime = [checkInTime, msgText[strIndexStart:strIndexStart+\
                           msgText[strIndexStart:strIndexStart+10].find(' ')]]
        else:
            checkInTime = [checkInTime]
    return checkInTime
    
def getCheckInDate(msgText):
    msgTextSplit = msgText.split()
    departIndex = msgTextSplit.index('Depart')
    checkInDateList = msgTextSplit[departIndex-4:departIndex-1]
    #make sure we got the date
    if checkInDateList[1] == '>':
        checkInDateList = msgTextSplit[departIndex-6:departIndex-3]
    checkInDate = checkInDateList[0] + ' ' + checkInDateList [1] + ' ' + checkInDateList[2]
    #see if there is a return flight
    if 'Depart' in msgTextSplit[departIndex+1:]:
        departIndex = msgTextSplit[departIndex+1:].index('Depart') + departIndex + 1
        checkInDateList = msgTextSplit[departIndex-4:departIndex-1]
        #make sure we got the date
        if checkInDateList[1] == '>':
            checkInDateList = msgTextSplit[departIndex-6:departIndex-3]
        checkInDate = [checkInDate, checkInDateList[0] + ' ' + \
                       checkInDateList [1] + ' ' + checkInDateList[2]]
    else:
        checkInDate = [checkInDate]
    return checkInDate

def getCheckInCity(msgText):
    msgTextSplit = msgText.split()
    departIndex = msgTextSplit.index('Depart')    
    checkInCity = msgTextSplit[departIndex+1]
    if 'Depart' in msgTextSplit[departIndex+1:]:
        departIndex = msgTextSplit[departIndex+1:].index('Depart') + departIndex + 1
        checkInCity = [checkInCity, msgTextSplit[departIndex+1]]
    else:
        checkInCity = [checkInCity]
    return checkInCity
    
def getInfoFromEmail(emailData):
    msgTextList = getEmailText(emailData[0][1])
    for msgText in msgTextList:
        confNum = getConfNum(msgText)
        #see if there are multiple itineraries
        msgTextSplit = msgText.split()
        if confNum in msgTextSplit:
            confNumIndex = msgTextSplit.index(confNum)
        else:
            confNumIndex = msgTextSplit.index('*'+confNum+'*')
        firstName = msgTextSplit[confNumIndex+1]
        lastName =  msgTextSplit[confNumIndex+2]
        #see if there are < formatting issues
        if firstName == '>':
            firstName = msgTextSplit[confNumIndex+2]
            lastName = msgTextSplit[confNumIndex+4]
        possible2ndConf = msgTextSplit[confNumIndex+3][1:-1]
        if len(possible2ndConf) == 6 and \
        not enchant.Dict("en_US").check(possible2ndConf):
            confNum = [confNum,str(possible2ndConf)]
            firstName = [firstName, str(msgTextSplit[confNumIndex+4])]
            lastName = [lastName, str(msgTextSplit[confNumIndex+5])]
        else:
            confNum = [confNum]
            firstName = [firstName]
            lastName = [lastName]        
                #get the time you need to check in
        checkInTime = getCheckInTime(msgText)
        checkInDate = getCheckInDate(msgText)
        checkInCity = getCheckInCity(msgText)
#            
#   OLD WAY TO GET FIRST AND LAST NAMES!! (NEED TO CHECK ON FREEDS EMAIL)
#        
#        
#        if ('firstName=' in msgText) and ('lastName=' in msgText):
#            strIndexStart = msgText.find('firstName=')+10
#            strIndexEnd = msgText.find('&lastName=')
#            firstName = str(msgText[strIndexStart:strIndexEnd])
#            strIndexStart = msgText.find('lastName=')+9
#            lastName = str(msgText[strIndexStart:strIndexStart+50])
#            strIndexEnd = max(lastName.find('&'),lastName.find('Check'))
#            print(lastName.find('&'))
#            print(lastName.find('Check'))
#            lastName = lastName[0:strIndexEnd]
#        else:
#            confNumIndex = msgText.find(confNum)
#            print confNumIndex
#            msgSearch = msgText[confNumIndex+6:confNumIndex+200]
#            print msgSearch
#            msgSearch = msgSearch.strip()
#            firstName, lastName = msgSearch.split(' ')
#            firstName = str(firstName)
#            lastName = str(lastName)
        
#        if 'Arrival\r\n' in msgText:
#            strIndexStart = msgText.find('Arrival\r\n')+9
#            checkInDate = msgText[strIndexStart:strIndexStart+\
#                          msgText[strIndexStart:strIndexStart+20].find('\r')]
#        else:
#            strIndexStart = msgText.find('Departure/Arrival')
#            msgSplit = msgText[strIndexStart:].split('\n')[1:]
#            for msgLine in msgSplit:
#                if len(msgLine.strip()) > 0:
#                    checkInDate = msgLine.strip()
#                    break
#        if '\r\nDepart ' in msgText:
#            strIndexStart = msgText.find('\r\nDepart ') + 10
#            checkInCity = msgText[strIndexStart:strIndexStart+\
#                          msgText[strIndexStart:strIndexStart+50].find(' (')]
#        else:
#            strIndexStart = msgText.find(checkInDate)
#            msgSplit = msgText[strIndexStart:].split('\n')[1:]
#            numNoWhiteLines = 0
#            for msgLine in msgSplit:
#                if len(msgLine.strip()) > 0:
#                    checkInCity = msgLine.strip()
#                    numNoWhiteLines += 1
#                    if numNoWhiteLines == 2:
#                        msgDepartInfo = msgLine.split(' ')
#                        checkInCity = str(msgDepartInfo[1])
#                        checkInTime = str(msgDepartInfo[-3]+ ' ' + msgDepartInfo[-2])
#                        break
                    
                    
        try:
            infoList = []
            for j in xrange(len(checkInDate)):
                for i in xrange(len(firstName)):                        
                    info = {'confNum':confNum[i],
                            'firstName':firstName[i],
                            'lastName':lastName[i],
                            'datetime':parser.parse(checkInDate[j] + ' ' + \
                                                    checkInTime[j]),
                            'city':checkInCity[j]}
                    infoList.append(info)
        except:
            infoList = []
        print('info from email:')
        print(infoList)
        return infoList

def sendEmail(emailText, emailData=None, toaddr=None, subject=''):
    if (emailData is None) and (toaddr is None):
        print('Must supply a recipiant address or the email data')
        return
    if toaddr is None:
        toaddr = getSenderFromEmail(emailData)
    fromaddr = username + '@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    msg = MIMEText(emailText)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr
    print(subject)
    print(fromaddr)
    print(toaddr)
    server.sendmail(fromaddr,toaddr,msg.as_string())
    return
    
def sendEmailScheduled(emailData,infoList):
    #get the sender
    print(messages.emailScheduled(infoList))
    sendEmail(messages.emailScheduled(infoList),emailData=emailData,
              subject='We got it!')
    return
    
def sendEmailGmailForwarding(emailData):
    #get the forwarding info
    info = getGmailForwardInfo(emailData)
    sendEmail(info['message'], emailData=emailData,
              subject='Almost there!',toaddr=info['toaddr'])
    return

def getInfoFromSubject(emailData):
    subject = email.message_from_string(emailData[0][1])['Subject']
    subjectSplit = subject.split('|')
    confNum = subject[subject.find('(')+1:subject.find(')')]
    firstName = subject[subject.find('/')+1:]
    lastName = subjectSplit[3][1:subjectSplit[3].find('/')]
    checkInDate = subjectSplit[1][1:-1]
    #get the check in time from the email text
    msgText = getEmailText(emailData[0][1])[0]
    startIndex = msgText.find('Southwest Airlines at *')+23
    checkInTimeSegment = msgText[startIndex:startIndex+10]
    checkInTime = checkInTimeSegment[0:checkInTimeSegment.find('*')]
    checkInCity = subjectSplit[2][1:4]
    print checkInDate
    info = {'confNum':confNum,
            'firstName':firstName,
            'lastName':lastName,
            'datetime':parser.parse(checkInDate[0:2] + ' ' + \
                                    checkInDate[2:5] + ' 20' + \
                                    checkInDate[5:] + ' ' + \
                                    checkInTime),
            'city':checkInCity}
    print info
    return [info]
    
def monitorEmail(mail,verbose=False,sendConfirmationEmail=False):
    if verbose:
        print('Starting to monitor email...')
    #start a while loop to read emails    
    while True:
        try:
            unreadMsgs = getUnreadMessages(mail)[0].split()
            #go through all the messagse
            for messageNum in unreadMsgs:
                #get the message text
                typ, emailData = mail.fetch(messageNum, '(RFC822)')
                #see what type of email it is
                emailType = getEmailType(emailData)
                infoList = []
                if verbose:
                    print(emailType)
                if emailType == 'Southwest Confirmation':
                    infoList = getInfoFromEmail(emailData)
                elif emailType == 'Gmail Forwarding':
                    sendEmailGmailForwarding(emailData)
                elif emailType == 'Info In Subject':
                    infoList = getInfoFromSubject(emailData)
                elif verbose:
                    print('Unknown email!')
                #see if info is the correct length
                if len(infoList) > 0:
                    for info in infoList:                    
                        #we have the correct information!
                        #start the scheduler
                        report = startCheckInThread(info)
                        if verbose:
                            print(report)
                    #send the person an email
                    if sendConfirmationEmail:
                        sendEmailScheduled(emailData,infoList)
        except:
            'Error! (probably a connection error)'
            time.sleep(30) #sleep for an extra 30 seconds, for a total of 1 min
        time.sleep(30)

def startCheckInThread(info):
    if len(info) >= 4:
        dtNow = datetime.datetime.now(timezoneParser.getTimeZone(info['city'])).replace(tzinfo=None)
        deltaT = (info['datetime']-timezoneParser.timeDelta-dtNow).total_seconds()
        info['SecondsToCheckIn'] = deltaT
        print(deltaT)
        #check to make sure the information is correct
        if checkin.test_credentials(info) and deltaT != 0:
            print('passed credential test!')
            Timer(deltaT, checkin.emailCheckIn, (info,)).start()
            messageString = messages.startedScheduler(info)
        else:
            messageString = messages.wrongInfo()
    else:
        messageString = messages.badInput()
    return messageString

if __name__ == "__main__":
    #sign into email
    mail = signIn(verbose=True)

    sendMail = input("Do you want to send confirmation emails (1 = yes)? \n")
    if sendMail == 1:
        sendConfEmail = True
        print("We will send confirmation emails")
    else:
        sendConfEmail = False
        print("Will not send confirmation emails")
    
    threads = []
    
    emailThread = threading.Thread(target=monitorEmail,args = (mail,),
                                   kwargs = {'verbose':True,
                                   'sendConfirmationEmail':sendConfEmail})
    time.sleep(1)
    threads.append(emailThread)
    emailThread.start()
    #p = re.compile(r'(?<![A-Z0-9])[A-Z0-9]{6}(?![A-Z0-9])')
