# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 16:46:20 2015

@author: Glenn
"""
import random
import timezoneParser as tzp
import datetime

def insultGenerator():
    #insults = ['dumbass', 'asshole', 'idiot', 'moron', 'ya cunt', 'mush',
    #           'cheif', 'champ']
    #return random.choice(insults)
    return ''
    
def lateCheckin():
#    messageStr = 'Check in time should be in the future ' + \
#                insultGenerator() + '.  Anyways, I will try to check you in now.'
    messageStr = 'Check in time should be in the future.  Anyways, I will try to check you in now.'
    return messageStr
    
def startedScheduler(info):
    dt = info['datetime']-datetime.timedelta(days=1)
    messageStr = 'The scheduler started.  You will be checked in at ' + \
                 dt.strftime('%Y-%m-%d %I:%M:%S %p ') + \
                 tzp.shortName(tzp.getTimeZone(info['city']))
    return messageStr

def wrongInfo():
    messageStr = 'Your name or confirmation number is wrong.  Try again.'
    return messageStr

def badInput():
    messageStr = r"I can't understand what you wrote.  Do FirstName, LastName, ConfNum, date, time."
    return messageStr
    
def successfulCheckIn():
    messageStr = 'You are now checked in! Check your email.'
    return messageStr

def failedCheckIn():
    messageStr = 'There was an issue checking you in.  Do it yourself.'
    return messageStr

def preCheckIn(secs):
    messageStr = 'In %d seconds we will try to check you in.' % secs
    return messageStr

def emailScheduled(infoList):
    numItineraries = len(infoList)
    messageStr = 'I received your flight information ' + \
                     infoList[0]['firstName'].title() + '.  '
    #different messages for 1 vs more
    if numItineraries == 1:
        info = infoList[0]
        messageStr = messageStr + 'You are leaving on ' + \
                     info['datetime'].strftime('%b %d, at %I:%M:%S %p') + ' ' + \
                     tzp.shortName(tzp.getTimeZone(info['city'])) + '\n'
        messageStr = messageStr + 'You will be checked in 24 hours before your flight departure time.'
    else:
        messageStr = messageStr + 'I found ' + str(numItineraries) + \
                     ' itineraries in your email:' + '\n'
        for info in infoList:
            messageStr = messageStr + info['firstName'].title() + ' ' + info['lastName'].title() + \
            ', depart at ' + info['datetime'].strftime('%b %d, %I:%M:%S %p') + ' ' + \
            tzp.shortName(tzp.getTimeZone(info['city'])) + '\n'
        messageStr = messageStr + 'You will be checked in 24 hours before your flight departure times.'
    return str(messageStr)

def problemWithGmailForwarding():
    messageStr = 'Sorry, there was an issue with parsing the gmail forwarding email.  We are working on solving the issue and will get back to you soon!'
    return messageStr
    
def gmailForwardingSendCode(confCode):
    messageStr = 'Thanks for setting up Gmail forwarding!  You are almost done.  ' + \
                'Please enter the confirmation code: ' + confCode + ' into the field in Gmail > settings >  Forwarding and POP/IMAP > Forwarding > Verify swcheckinhelper@gmail.com'
    return messageStr