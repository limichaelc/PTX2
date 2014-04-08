from bs4 import BeautifulSoup
import urllib2

page = urllib2.urlopen("https://registrar.princeton.edu/course-offerings/search_results.xml?submit=Search&term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR")
soup = BeautifulSoup(page)
fp = open('file.txt','wb')
fp.write(soup.prettify('UTF-8'))
