from bs4 import BeautifulSoup
import urllib2
import sys

#write into a file named name
def write(name):
    sys.stderr.write('Getting courses from registrar (this could take a while...)\n')
    page = urllib2.urlopen("https://registrar.princeton.edu/course-offerings/search_results.xml?submit=Search&term=1144")
    #soup = BeautifulSoup(page)
    fp = open(name,'wb')
    #fp = open('page.txt', 'wb')
    #fp.write(soup.prettify('UTF-8'))
    fp.write(page.read())
    sys.stderr.write('Wrote courses to file %s\n' % name)
    fp.close()

if __name__ == '__main__':
    write('page.txt')
