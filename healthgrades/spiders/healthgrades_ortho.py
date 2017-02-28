import scrapy
from scrapy_splash import SplashRequest





class OrthoSpider(scrapy.Spider):
    name = "ortho"
    
    def start_requests(self):
        urls = [
            'https://www.healthgrades.com/usearch?where=Boston%2C%20MA%2002127&city=Boston&state=MA&zip=02127&pt=42.339%2C-71.0253&what=Orthopaedics&searchType=SpecialtyVertical&entityCode=SY00002FA3'
        ]
        for url in urls:
            yield SplashRequest(url=url,
                                callback=self.parse,
                                endpoint='render.html',
                                args={'wait': 5.0}
                                )

    def parse(self, response):
        page = response.url.split('/')[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('saved file %s' % filename)
