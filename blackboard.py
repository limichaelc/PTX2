from urllib import urlopen
import urllib, urllib2
from bs4 import BeautifulSoup
from time import sleep 
import re
import bbscrape
import pyisbn

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
    txt = text.findAll(class_="shoppingCartInfo")
    prices = []
    for j in txt:
        price = j.find(class_="textElementRight")
        if price != None:
            price = str(price.contents).split('$')[1]
            prices.append(price)
    return prices

#get list of titles and isbn numbers (alternating) from blackboard
def get_titles_isbn():
    txt = text.findAll('td', {'width':'100%', 'class':'textBold'})
    list = []
    for i in txt:
        list.append(i.text)
    return list

def main():
    page = open('page.txt')
    soup = BeautifulSoup(page)
    table = soup.find('table')
    rows = table.findAll('tr')
    length = len(rows)
    #for each class
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
        
        #get page url for reading lists
        pageurl = columns[11].find('a')['href']
        text = get_books_page(pageurl)
        
        #get the required books information for this class
        thiscoursesbooks = []
           #all labyrinth prices
        lab_prices = get_labyrinth_price()
        print lab_prices
           #all titles and isbns(alterating)
        titles = get_titles_isbn()
        print titles
        numbooks = len(lab_prices)
        print "books " + str(numbooks)
        n = 0
        while n < numbooks:
            #each book is a dictionary that contains:
            #titles, isbn10, isbn13, lab_price, amazonprice, edition,
            #author, course used in 
            thisbook = []
            thisbook.append(titles[2*n])
            isbn10 = titles[(2*n)+1]
            print isbn10
            thisbook.append(isbn10)
            isbn13 = pyisbn.convert(isbn10)
            thisbook.append(isbn13)
            thisbook.append(lab_prices[n])
            #amazon prices
            
            n = n+1

main()
