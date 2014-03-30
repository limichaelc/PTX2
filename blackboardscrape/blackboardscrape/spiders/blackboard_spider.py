from scrapy.spider import Spider

class BlackBoardSpider(Spider):
    name = "blackboard"
    allowed_domains = ["blackboard.princeton.edu"]
    start_urls = [
        "http://registrar.princeton.edu/course-offerings/search_results.xml?submit=Search&term=1144&coursetitle=&instructor=&distr_area=&level=&cat_number=&sort=SYN_PS_PU_ROXEN_SOC_VW.SUBJECT%2C+SYN_PS_PU_ROXEN_SOC_VW.CATALOG_NBR%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_SECTION%2CSYN_PS_PU_ROXEN_SOC_VW.CLASS_MTG_NBR"
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2]
        open(filename, 'wb').write(response.body)