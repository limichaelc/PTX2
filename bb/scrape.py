import urllib
import urllib2
from cookielib import CookieJar

baseURL = 'https://blackboard.princeton.edu/webapps/pu-readinglist-bb_bb60/main.do?course_id='
loginURL = 'https://blackboard.princeton.edu/webapps/login/'
post_data = {'action':'guest_login'}

courseid = '213159'

# set up the cookie jar and opener
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

data = urllib.urlencode(post_data)
req = urllib2.Request(loginURL, data)
resp = opener.open(loginURL, data)
print '============LOGIN================'
print resp.read()
print '================================='




print opener.open(baseURL+courseid).read()
