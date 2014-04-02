from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep 
import re

BASE_URL = "http://www.amazon.com/gp/product/"
BASE_2 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="
BASE_3 = "http://registrar.princeton.edu/course-offerings/search_results.xml?term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR&submit=Search"

recoursenumber = re.compile('course_details*')
recourselink = re.compile('http://blackboard.princeton.edu*')
recourselink2=re.compile('https://blackboard.princeton.edu*')
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html)

def get_blackboard():
    url = BASE_3
    soup = make_soup(url)
    coursenumber = soup.find(href = recoursenumber).find('u').findAll(text=True)
    #print coursenumber
    

get_blackboard()
