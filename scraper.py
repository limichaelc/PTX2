from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep 

BASE_URL = "http://www.amazon.com/gp/product/"
BASE_2 = "http://www.labyrinthbooks.com/all_detail.aspx?isbn="
BASE_3 = "view-source:http://registrar.princeton.edu/course-offerings/search_results.xml?term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR&submit=Search"

# returns the page source given a url
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html)

# returns the main-image given an amazon url
def get_images(isbn):
    url = BASE_URL+isbn
    soup = make_soup(url)
    main_image = soup.find(id = "main-image")['src']
    print main_image

#returns description (with html tags) given an amazon url
def get_description(isbn):
    url = BASE_URL+isbn
    soup = make_soup(url)
    description = soup.find(id = "postBodyPS").contents
    print description

#amazon price given isbn
def get_price(isbn):
    url = BASE_URL+isbn
    soup = make_soup(url)
    price = soup.find(class_="rentPrice").text
    print price

#title from amazon given isbn
def get_title(isbn):
    url = BASE_URL+isbn
    soup = make_soup(url)
    title = soup.find(id="btAsinTitle").text
    print title

# get labyrinth price ****not using isbn10 like amazon does
def get_lab_price(isbn):
    url = BASE_2 + isbn
    soup = make_soup(url)
    lab_price = soup.find(id = "ctl02_rptDetails_ctl00_lblWhere").text
    print lab_price

#test for images
#get_images("020161586X")

#test for description
#get_description("020161586X")

#test for price
#get_lab_price("9780471982326")
