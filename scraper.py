from bs4 import BeautifulSoup
from urllib2 import urlopen
from time import sleep 

BASE_URL = "http://www.amazon.com"

# returns the page source given a url
def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html)

# returns the main-image given an amazon url
def get_images(book_url):
    soup = make_soup(book_url)
    main_image = soup.find(id = "main-image")['src']
    print main_image

get_images("http://www.amazon.com/Practice-Programming-Addison-Wesley-Professional-Computing/dp/020161586X/ref=sr_1_1?s=books&ie=UTF8&qid=1396136819&sr=1-1&keywords=practice+of+programming")
