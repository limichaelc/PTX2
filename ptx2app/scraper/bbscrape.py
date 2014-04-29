import urllib
import urllib2
from cookielib import CookieJar
import sys

baseURL = 'https://blackboard.princeton.edu/webapps/pu-readinglist-bb_bb60/main.do?course_id='
loginURL = 'https://blackboard.princeton.edu/webapps/login/'
post_data = {'action':'guest_login'}

# set up the cookie jar and opener
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

# log into BB. Basically just saves the session cookies in the opener
def login():
    sys.stderr.write('Logging into Blackboard...')
    data = urllib.urlencode(post_data)
    resp = opener.open(loginURL, data)
    sys.stderr.write('Logged into Blackboard.')

#return the page as a string. Log in as necessary
def get_page(courseid):
    sys.stderr.write('Getting page for courseid %s' % str(courseid))
    page = opener.open(baseURL + str(courseid)).read()
    
    # if we're not logged in, this will be true
    if page.startswith('<script>'):
        login()
        page = opener.open(baseURL + str(courseid)).read()

    return page
