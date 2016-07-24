# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 18:37:28 2015

Southwest Checkin

@author: Glenn
"""
import time
from selenium.webdriver import Chrome
import sys
import messages
from threading import Timer

CHROME_DRIVER_PATH = 'C:\ChromeDriver\chromedriver.exe'
#CHECKIN_BUTTON_XPATH = '//input[@type="submit" and @title="Check In"]'
CHECKIN_BUTTON_XPATH = '//input[@type="submit" and @value="Check In"]'
#CHECKIN_BUTTON_XPATH = '//input[@name="submitbutton" and @type="submit" and @value="Check In"]'
EMAIL_RADIO_BUTTON_XPATH = '//input[@type="radio" and @value="optionEmail"]'
FINAL_BUTTON_XPATH = '//button[@type="submit" and @id="checkin_button"]'
MAIN_SW_URL = 'https://www.southwest.com/flight/retrieveCheckinDoc.html?int=HOME-BOOKING-WIDGET-AIR-CHECKIN'

def test_credentials(info):
    print('Testing credentials')
    #checkin(info)
    return True
    ### sign into southwest make sure you get the too early page!!

def preCheckIn(info):
    """
    This will run about a minute before running the checkinMain.
    The purpose of this is to alert the user that the program is working
    and will check them in.
    """
    messageText = messages.preCheckIn(info['preCheckInSecs'])
    try:
        info['api'].send_direct_message(screen_name=info['screen_name'],
                                text=messageText)
    except:
        print('Error sending pre check in direct message.')
        print(messageText)
        print(sys.exc_info()[0])
    #run the check in thread
    Timer(info['SecondsToCheckIn'], checkinMain, (info,)).start()

def checkinMain(info):
    checkinResults = checkin(info)
    if checkinResults[0] == -1:
        #try again
        time.sleep(3)
        checkinResults = checkin(info)
    messageText = 'Hey ' + info['screen_name'] +'! ' + checkinResults[1]
    try:
        info['api'].send_direct_message(screen_name=info['screen_name'],
                                text=messageText)
    except:
        print('Error sending direct message.')
        print(messageText)
        print(sys.exc_info()[0])
        
def emailCheckIn(info):
    checkinResults = checkin(info)
    checkinTry = 1
    if checkinResults[0] == -1:
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(0.5)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(0.4)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(1)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(3)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(3)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(3)
        checkinResults = checkin(info)
        checkinTry = checkinTry + 1
    if checkinResults[0] == -1:
        time.sleep(5)
        checkinResults = checkin(info,keepOpen=True)
        checkinTry = checkinTry + 1
    print checkinTry
    
    
def checkin(info,keepOpen=False):
    url = MAIN_SW_URL + '&confirmationNumber=' + info['confNum'] + \
        '&lastName=' + info['lastName'] + '&firstName=' + info['firstName']
    try:
        browser = Chrome(CHROME_DRIVER_PATH) 
        browser.get(url)
        time.sleep(0.5)
        buttonCheckIn = browser.find_element_by_xpath(CHECKIN_BUTTON_XPATH)
        buttonCheckIn.click()
        time.sleep(0.5)
        radioButtonEmail = browser.find_element_by_xpath(EMAIL_RADIO_BUTTON_XPATH)
        radioButtonEmail.click()
        time.sleep(0.1)    
        buttonFinal = browser.find_element_by_xpath(FINAL_BUTTON_XPATH)    
        buttonFinal.click()
        time.sleep(0.5)
        if not keepOpen:
            #browser.close()
            browser.quit()
        print('successful checkin!')
        report = messages.successfulCheckIn()
        status = 1
    except:
        if not keepOpen:
            #browser.close()
            browser.quit()
        report = messages.failedCheckIn()
        status = -1
    return [status, report]