# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 01:27:48 2015

Twitter control

@author: Glenn
"""
import twitterKeys as tk
import tweepy
import datetime
import pytz
import checkin
import dateutil.parser as parser
from threading import Timer
import time
import threading
import random
import sys
import messages

#set timezone
nyc = pytz.timezone("America/New_York")
#set pre checkin status time
preCheckInTime = 60 #seconds


def signIn():
    consumer_key = tk.consumerKey
    consumer_secret = tk.consumerSecret
    access_token = tk.accessToken
    access_token_secret = tk.accessTokenSecret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    return(api)
    
def monitorMentions(api):
    print('Starting monitor mentions.')
    #create a datetime for comparison
    previousDatetime = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
    while True:
        #look at mentions
        mentions = api.mentions_timeline()
        #go through all mentions
        for mention in mentions:
            #make sure the mention is after the previousDatetime
            if mention.created_at > previousDatetime:
                #we have a new mention!
                #parse the mention text
                info = parseText(mention.text)
                info['api'] = api
                info['screen_name'] = mention.user.screen_name
                report = startCheckInThread(info)
                messageBack(report, api, mention.user.screen_name)
                #tweetBack(report,api,mention)
                previousDatetime = mention.created_at
        time.sleep(60)

def monitorDirectMessages(api):
    print('Starting direct message monitor')
    while True:
        #look at mentions
        directMessages = api.direct_messages()
        #go through all mentions
        for directMessage in directMessages:
            print('Direct message received.')
            #we have a new directMessage!
            #save the direct message
            with open("directMessages.txt", "a") as myfile:
                myfile.write(directMessage.text + '\n')
            #parse the directMessage text
            info = parseText(directMessage.text)
            if len(info) > 1:            
                info['api'] = api
                info['screen_name'] = directMessage.sender_screen_name
                info['preCheckInSecs'] = preCheckInTime
                report = startCheckInThread(info)
                messageBack(report, api, directMessage.sender_screen_name)
            directMessage.destroy()
        time.sleep(60)
                
def parseText(textStr):
    #break text up into a list
    textStr = textStr.replace(', ',' ')
    textStr = textStr.replace(',', ' ')
    textList = textStr.split(' ')
    result = [-1]
    print(textList)
    #see if there is a usename
    if tk.username in textList:
        textList.pop(textList.index(tk.username))
    if len(textList) >= 5:
        firstName = textList[0]
        lastName = textList[1]
        confNum = textList[2]
        date = textList[3]
        time = textList[4]
        print(date + ' ' + time)
        #see if there is am or pm
        if 'AM' in (name.upper() for name in textList):
            time = time + ' AM'
        elif 'PM' in (name.upper() for name in textList):
            time = time + ' PM'
        #ADD TIMEZONE FUNCTIONALITY HERE
    
        try:
            datetimeCheckin = parser.parse(date+' '+time)
            result = {'firstName':firstName, 'lastName':lastName,
                      'confNum':confNum, 'datetime':datetimeCheckin}
            print(result)
        except:
            print('date and time are in terrible formats')
            print(sys.exc_info()[0])
    else:
        print('Not enough inputs.')
    return result

def startCheckInThread(info):
    if len(info) >= 4:
        dtNow = datetime.datetime.now(nyc).replace(tzinfo=None)
        deltaT = (info['datetime']-dtNow).total_seconds()
        info['SecondsToCheckIn'] = deltaT
        #check to make sure the information is correct
        if checkin.test_credentials(info):
            #Timer(deltaT, checkin.checkinMain, (info,)).start()
            if deltaT <= 0:
                Timer(deltaT, checkin.checkinMain, (info,)).start()
                messageString = messages.lateCheckin()
            else:
                Timer(deltaT-info['preCheckInSecs'], checkin.preCheckIn, (info,)).start()
                messageString = messages.startedScheduler(info['datetime'])
        else:
            messageString = messages.wrongInfo()
    else:
        messageString = messages.badInput()
    return messageString
    
def tweetBack(api,mention):
    #this will tweet back that the scheduler has been called
    print('work on this!')

def messageBack(report, api, screen_name):
    #send the report back
    messageText = 'Hey ' + screen_name +'! ' + report
    try:
        api.send_direct_message(screen_name=screen_name, text=messageText)
    except:
        print('Error sending direct message.')
        print(sys.exc_info()[0])
         
if __name__ == "__main__":
    #sign in
    api = signIn()
    
    threads = []
    
    dmThread = threading.Thread(target=monitorDirectMessages,args = (api,))
    threads.append(dmThread)
    dmThread.start()
    
    #mentionThread = threading.Thread(target=monitorMentions,args = (api,))
    #threads.append(mentionThread)
    #mentionThread.start()
    
    