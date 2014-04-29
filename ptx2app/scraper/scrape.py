from urllib import urlopen
import urllib, urllib2
from bs4 import BeautifulSoup
from time import sleep 
import re
import bbscrape
import pyisbn
import json
from ptx2app.models import Course, Book
from django.core.exceptions import ObjectDoesNotExist
import os

BASE_URL = "http://www.amazon.com/gp/product/"
BASE_2 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="
BASE_REG = "http://registrar.princeton.edu/course-offerings/search_results.xml?term="
BASE_4 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="

recoursenumber = re.compile('course_details*')
recourselink = re.compile('http://blackboard.princeton.edu*')
recourselink2 = re.compile('https://blackboard.princeton.edu*')
recoursetitle = re.compile('/webapps/blackboard/execute*')
amazon = ""
quote = re.compile('"*')
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


###########TO BE IMPLEMENTED####################
# given a term ID (i.e. 1144), perform all scraping actions
def scrapeall(term, reg_filename = 'reg.html', force_reg = True):
    #first: get the page from the registrar's site. For future use, cache at given filename
    #if we're forcing a refresh or the file doesn't exist, get the page from the registrar
    import os.path
    if force_reg or not os.path.isfile(reg_filename):
        with open(reg_filename, 'w') as f:
            page = urllib2.urlopen(BASE_REG + str(term))
            f.write(page.read())

    #we have the registrar page. Now get all of the information from it
    f = open(reg_filename, 'r')


########################################################

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
    p = 1329
    for i in range(1329, length):
        print p
        p += 1
        currentrow = {}
        thisrow = rows[i]
        columns = thisrow.findAll('td')
        
        #make list of course designations i.e. MAE 305
        classes = columns[1].find('u')
        classes = classes.findAll(text = quote)
        course_desig = []
        #print classes
        for c in classes:
            c = re.sub(' +', '', c)
            c = re.sub('\n', '', c)
            if (str(c) != '<br/>'):
                if str(c) != "":
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
            f = open('text5.txt', 'r+')
            f.write( "[\n")
            first = False
        f.write(str(currentrow)+',\n')
        print currentrow
        finallist.append(currentrow)
    f.write( "]")


def makebook(book_info):
    b = Book(**{
        'isbn': book_info['isbn13'],
        'isbn10': book_info['isbn10'],
        'title': book_info['title'],
        'edition': 0, ######### editions are crazy. fix this in data?????
        'authors': book_info['author'],
        'amazon_price': book_info['amazonprice'][1:] if book_info['amazonprice'] else None, ####### trim off the '$'
        'labyrinth_price': book_info['labprice'],
        'lowest_student_price': None, ###### should be higher than any real student price,
                                        ###### which will be set when studet adds a physbook for sale
        'picture_link': book_info['image'],
        })
    b.save()
    return b

# take the data from the file with the given filename and save it into the database
def save(fromfilename='finalcopy.txt'):
    # get finalcopy.txt from the scraper directory, not the dir this is being run from
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fromfilename)
    with open(path, 'r') as f:
        l = eval(f.read())
 
    for course in l:
        books = []
        for book_info in course['booklist']:
            book_info['isbn10'], book_info['isbn13'] = book_info['isbn13'], book_info['isbn10'] ###### switch ISBN10 and 13 b/c they are messed up in current data
            try:
                book = Book.objects.get(isbn10 = book_info['isbn10'])
            except ObjectDoesNotExist:
                book = makebook(book_info)
            except Exception as e:
                print "Got exception while adding book:"
                print book_info
                raise e
            books.append(book)



        year = 2014 ############ UN-HARDCODE THESE
        term = 'S'  ############ UN-HARDCODE THESE
        course_props = {}
        course_props['name'] = course['coursename']
        course_props['year'] = year
        course_props['term'] = term


        # make an individual course entry for each crosslisting
        for desig in course['coursedesig']:
            dept = desig[:3]
            num = desig[3:]
            try:
                c = Course.objects.get(dept=dept, num=num, **course_props)
            except ObjectDoesNotExist:
                c = Course(dept = dept, num = num, **course_props)
                c.save()
            except Exception as e:
                print "Got exception while adding course:"
                print dept, num, course_props
                raise e

            for book in books:
                c.books.add(book)

if __name__ == '__main__':
    #scrape()
    scrape('page.txt')
