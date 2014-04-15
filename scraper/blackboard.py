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

def get_labyrinth_price():
    txt = text.findAll(class_="shoppingCartInfo")
    prices = []
    first = True
    for j in txt:
        if first == True:
            first = False
            continue
        price = j.find(class_="textElementRight")
        if price != None:
            price = str(price.contents).split('$')[1]
            price2 = str(price).split('.')
            prices.append(price2[0]+'.'+price2[1][0:2])
        elif j.find(class_='textElementItalic') != None:
            prices.append(None)
    #print prices
    return prices

#get list of titles and isbn numbers (alternating) from blackboard
def get_titles_isbn():
    txt = text.findAll('td', {'width':'100%', 'class':'textBold'})
    list = []
    for i in txt:
        list.append(i.text)
    return list

def get_author():
    txt = text.findAll('td', {'class':'textItalic', 'width':'100%'})
    list = []
    for i in txt:
        if len(i.contents) != 0:
            list.append(i.contents[0])
        else:
            list.append(None)
    return list

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
    edition = edition.find(class_='content')
    if edition == None:
        return None
    edition = edition.findAll('li')
    if edition == None:
        return None
    editioncopy = edition
    edition = edition[2]
    edition = str(edition).split('</b>')[1]
    edition = str(edition).split('</li>')[0]
    if edition == ' English':
        edition = editioncopy[1]
        edition = str(edition).split('</b>')[1]
        edition = str(edition).split('</li>')[0]
    return edition

def main():
    page = open('page.txt')
    soup = BeautifulSoup(page)
    table = soup.find('table')
    rows = table.findAll('tr')
    length = len(rows)
    #for each class
    finallist = []
    first = True
    for i in range(1, length):
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
        currentrow['coursedesig'] = (course_desig)
        #course name
        name = columns[2].contents[0]
        name = name.encode('utf-8').strip()
        currentrow['coursename'] = (name)
        
        #get page url for reading lists
        pageurl = columns[11].find('a')['href']
        text = get_books_page(pageurl)
        
        #get the required books information for this class
        thiscoursesbooks = []
        #all labyrinth prices
        lab_prices = get_labyrinth_price()
        
        #all titles and isbns(alterating)
        titles = get_titles_isbn()
        #authors
        authors = get_author()
        #print titles
        numbooks = len(titles)/2
        numlabprices = len(lab_prices)
        n = 0
        mismatch = False
        while n < numbooks:
            #each book is a dictionary that contains:
            #titles, isbn10, isbn13, lab_price, amazonprice, edition,
            #author, picture 
            thisbook = {}
            thisbook['title'] = (titles[2*n])
            isbn10 = titles[(2*n)+1]
            if not isbn10.isdigit():
                thiscoursesbooks.append("error")
                break
            thisbook['author'] = (authors[n])
            isbn13 = pyisbn.convert(isbn10)
            thisbook['isbn10'] = (isbn10)
            thisbook['isbn13'] = (isbn13)
            if n >= numlabprices:
                labprice = None
            else:
                labprice = lab_prices[n]
            thisbook['labprice'] = labprice
            thisbook['amazonprice']=(get_amazon_price(isbn13))
            thisbook['image'] = (get_amazon_image())
            thisbook['edition'] = (get_amazon_edition())
            n = n+1
            thiscoursesbooks.append(thisbook)
        currentrow['booklist'] = (thiscoursesbooks)
        if (first == True):
            f = open('text.txt', 'r+')
            #f.write( "[\n")
            first = False
        f.write(str(currentrow) + ",\n")
        print currentrow
    #    finallist.append(currentrow)
    f.write( "]")

main()
