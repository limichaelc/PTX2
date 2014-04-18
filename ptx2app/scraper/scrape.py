from urllib import urlopen
import urllib, urllib2
from bs4 import BeautifulSoup
from time import sleep 
import re
import bbscrape
import pyisbn
import json

BASE_URL = "http://www.amazon.com/gp/product/"
BASE_2 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="
BASE_3 = "http://registrar.princeton.edu/course-offerings/search_results.xml?term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR&submit=Search"
BASE_4 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="

recoursenumber = re.compile('course_details*')
recourselink = re.compile('http://blackboard.princeton.edu*')
recourselink2 = re.compile('https://blackboard.princeton.edu*')
recoursetitle = re.compile('/webapps/blackboard/execute*')
amazon = ""
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

def get_labyrinth_price(txt):
    txt = txt.find(class_="shoppingCartInfo")
    price = txt.find(class_="textElementRight")
    if price != None:
        price = str(price.contents).split('$')[1]
        price2 = str(price).split('.')
        price = price2[0]+'.'+price2[1][0:2]
    elif txt.find(class_='textElementItalic') != None:
        price = None
    #print prices
    return price

# returns the main-image given an amazon url
def get_amazon_image():
    main_image = amazon.find(id = "main-image")
    if main_image == None:
        main_image = amazon.find(id="imgBlkFront")
    if main_image != None:
        main_image = main_image['src']
    return main_image

#amazon price given isbn
def get_amazon_price(isbn13):
    url = BASE_URL+isbn13
    global amazon
    amazon = make_soup(url)
    price = amazon.find(class_="a-size-medium a-color-price offer-price a-text-normal")
    if price == None:
        price = amazon.find(class_="rentPrice")
    if price == None:
        price = amazon.find(class_="bb_price")
    if price != None:
        price = price.contents[0]
        price = re.sub(' +','', str(price))
        price = re.sub('\n', '', str(price))
    return price

def get_amazon_edition():
    edition = amazon.find(id='productDetailsTable')
    if edition == None:
        return None
    edition = edition.find(text = "Publisher:")
    if edition == None:
        return None
    edition = edition.next
    if edition == None:
        return None
    #print edition
    return edition

def scrape(name):
    #page = open(name)
    page = open('page.txt')
    soup = BeautifulSoup(page)
    table = soup.find('table')
    rows = table.findAll('tr')
    length = len(rows)
    #for each class
    finallist = []
    first = True
    previous = []
    p = 495
    for i in range(495, length):
        print p
        p += 1
        currentrow = {}
        thisrow = rows[i]
        columns = thisrow.findAll('td')
        
        #make list of course designations i.e. MAE 305
        classes = columns[1].find('u')
        course_desig = []
        for c in classes:
            if str(c) != '<br/>':
                c = re.sub(' +', '', c)
                c = re.sub('\n', '', c)
                course_desig.append(c)
        if course_desig == previous:
            continue
        else:
            previous = course_desig
        currentrow['coursedesig'] = (course_desig)
        #course name
        name = columns[2].contents[0]
        name = name.encode('utf-8').strip()
        currentrow['coursename'] = (name)
        
        #get page url for reading lists
        pageurl = columns[11].find('a')['href']
        #print pageurl
        text = get_books_page(pageurl)
        
        #get the required books information for this class
        thiscoursesbooks = []
        required = text.find(id = 'requiredList')
        if required != None:
            required = required.findAll(class_='viewReading')
            for g in required:
                thisbook = {}
                title = g.find(text = "Title: ")
                if title != None:
                    title = title.parent.findNext('td')
                    if title != None:
                        title = title.text
                else:
                    continue
                thisbook['title'] = title
                author = g.find(text = "Author: ")
                if author != None:
                    author = author.parent.findNext('td')
                    if author != None:
                        author = author.text
                #print author
                thisbook['author'] = author
                isbn10 = g.find(text= "ISBN: ")
                if isbn10 != None:
                    isbn10 = isbn10.parent.findNext('td')
                    if isbn10 != None:
                        isbn10 = isbn10.text
                #print isbn10
                if isbn10.isdigit():
                    isbn13 = pyisbn.convert(isbn10)
                else:
                    continue
                thisbook['isbn10'] = isbn10
                thisbook['isbn13'] = isbn13
                labprice = get_labyrinth_price(g)
                thisbook['labprice'] = labprice
                thisbook['amazonprice']=(get_amazon_price(isbn13))
                thisbook['image'] = (get_amazon_image())
                thisbook['edition'] = (get_amazon_edition())
                thisbook['required'] = True
                thiscoursesbooks.append(thisbook)
        recommended = text.find(id = 'recommendedListContainer')
        if recommended != None:
            recommended = recommended.findAll(class_='viewReading')
            for g in recommended:
                thisbook = {}
                title = g.find(text = "Title: ")
                if title != None:
                    title = title.parent.findNext('td')
                    if title != None:
                        title = title.text
                else:
                    continue
                thisbook['title'] = title
                author = g.find(text = "Author: ")
                if author != None:
                    author = author.parent.findNext('td')
                    if author != None:
                        author = author.text
                thisbook['author'] = author
                isbn10 = g.find(text= "ISBN: ")
                if isbn10 != None:
                    isbn10 = isbn10.parent.findNext('td')
                    if isbn10 != None:
                        isbn10 = isbn10.text
                if isbn10.isdigit():
                    isbn13 = pyisbn.convert(isbn10)
                else:
                    continue
                thisbook['isbn10'] = isbn10
                thisbook['isbn13'] = isbn13
                labprice = get_labyrinth_price(g)
                thisbook['labprice'] = labprice
                thisbook['amazonprice']=(get_amazon_price(isbn13))
                thisbook['image'] = (get_amazon_image())
                thisbook['edition'] = (get_amazon_edition())
                thisbook['required'] = False
                thiscoursesbooks.append(thisbook)            
        currentrow['booklist'] = (thiscoursesbooks)
        if (first == True):
            f = open('text3.txt', 'r+')
            f.write( "[\n")
            first = False
        f.write(str(currentrow)+',\n')
        print currentrow
        finallist.append(currentrow)
    f.write( "]")

if __name__ == '__main__':
    #scrape()
    scrape('page.txt')
