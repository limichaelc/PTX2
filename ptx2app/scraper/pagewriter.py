from bs4 import BeautifulSoup
import urllib2

def write(name):
    page = urllib2.urlopen("https://registrar.princeton.edu/course-offerings/search_results.xml?submit=Search&term=1144")
    soup = BeautifulSoup(page)
    fp = open(name,'wb')
    fp.write(soup.prettify('UTF-8'))
