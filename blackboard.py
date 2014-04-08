from urllib import urlopen
import urllib, urllib2
from bs4 import BeautifulSoup
from time import sleep 
import re
import bbscrape

BASE_URL = "http://www.amazon.com/gp/product/"
BASE_2 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="
BASE_3 = "http://registrar.princeton.edu/course-offerings/search_results.xml?term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR&submit=Search"

recoursenumber = re.compile('course_details*')
recourselink = re.compile('http://blackboard.princeton.edu*')
recourselink2 = re.compile('https://blackboard.princeton.edu*')
recoursetitle = re.compile('/webapps/blackboard/execute*')
rebr = re.compile('^<.*')
text = ""

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html)

def get_books_page(url):
    url = make_soup(url).a['href']
    length = len(url)
    idnum = url[(length-8):(length-2)]
    global text
    text = BeautifulSoup(bbscrape.cookie(idnum))
    return text

def get_labyrinth_price():
    txt = text.findAll(class_="textElementRight")
    print txt

def main():
    page = open('page.txt')
    soup = BeautifulSoup(page)
    table = soup.find('table')
    rows = table.findAll('tr')
    length = len(rows)
    for i in range(1, length):
        currentrow = []
        thisrow = rows[i]
        columns = thisrow.findAll('td')
        
        #make list of course designations i.e. MAE 305
        classes = columns[1].find('u')
        course_desig = []
        for c in classes:
            if c != '<br//>':
                c = re.sub(' +','', str(c))
                c = re.sub('\n', '', c)
                course_desig.append(c)
        
        currentrow.append(course_desig)
        currentrow.append(columns[2].contents[0])
        #get page url
        pageurl = columns[11].find('a')['href']
        text = get_books_page(pageurl)
        print get_labyrinth_price()
        
main()
