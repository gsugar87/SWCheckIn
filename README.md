# SWCheckIn
This project contains two programs.  One is a twitterController that will look for direct messages from twitter and set up a scheduler to sign someone into a southwest flight.  The other is a main program that will call a scheduler to sign you in (in the gui folder).  The twitter program is more robust since it does not require the main program to be running on your computer all the time.  This is the program I'm focusing on now.  The twitter program is intended to be ran on a raspberry Pi-like device that is low power and is always connected to the internet, so that it can check twitter and use the souwthwest website whenever it wants.

In order to use the twitter program, you will need to create a twitterKeys.py file that has the following:

consumerKey = 'xxxxxxxxxxxxxxxxxx'

consumerSecret = 'xxxxxxxxxxxxxxxxxxx'

accessToken = 'xxxxxxxxx-xxxxxxxxxxxxxxxx'

accessTokenSecret = 'xxxxxxxxxxxxxxxxxxxxx'

username = '@xxxxxx'

This is the twitter account's information. Google how to make a twitter app if you have questions about the above variables.

The program requires the chrome browser driver available here:
https://sites.google.com/a/chromium.org/chromedriver/downloads

The second program (which is the better one) is emailControl.py. This will check a gmail account for forwarded SW confirmation emails.  You need to make a file called emailKeys that has the login information.
