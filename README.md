# SWCheckIn
This project will check a gmail account for a forwarded southwest 
confirmation email and will check you in exactly 24 hours before your
flight.  You will need to set up a gmail account, and create a file
called emailKeys.py with the following information:

		username = 'your gmail username'
		password = 'your gmail password'
		
The main program you will run is called emailControl.py.  It will
regularly check a gmail account for forwarded southwest emails, and 
start a thread that will check in for a southwest flight at the
appropriate time.

The program requires the chromium browser driver available here:
https://sites.google.com/a/chromium.org/chromedriver/downloads

Download an unzip the appropriate chromedriver version for your machine.
You will then need to edit line 15 in checkin.py to set 
CHROME_DRIVER_PATH to the full path of the unzipped chromedriver.
