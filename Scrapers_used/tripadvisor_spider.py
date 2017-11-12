import scrapy
from hotel_sentiment.items import HotelSentimentItem

#TODO use loaders
class TripadvisorSpider(scrapy.Spider):
    '''
		Name of the spider
    '''
    name = "tripadvisor"
    '''
		Starting URL's for the spider to scrape for.
    '''
    start_urls = [
		"https://www.tripadvisor.com/Hotels-g304551-New_Delhi_National_Capital_Territory_of_Delhi-Hotels.html",
		"https://www.tripadvisor.com/Hotels-g304554-Mumbai_Bombay_Maharashtra-Hotels.html",
		"https://www.tripadvisor.com/Hotels-g186338-London_England-Hotels.html",
		"https://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g32655-Los_Angeles_California-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g187323-Berlin-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g297586-Hyderabad_Hyderabad_District_Telangana-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g12392950-Bangalore_District_Karnataka-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g304556-Chennai_Madras_Chennai_District_Tamil_Nadu-Hotels.html",
		"https://www.tripadvisor.in/Hotels-g304556-Chennai_Madras_Chennai_District_Tamil_Nadu-Hotels.html"]
	'''
		Function to parse pages of hotels in a city
	'''
    def parse(self, response):
        for href in response.xpath('//div[@class="listing_title"]/a/@href'):
			#item['average_rating'] = response.xpath('//span[starts-with(@class,"ui_bubble_rating")]').extract()[0]
			url = response.urljoin(href.extract())
			yield scrapy.Request(url, callback=self.parse_hotel)

        next_page = response.xpath('//div[@class="unified pagination standard_pagination"]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse)
	'''
		Parses for all the reviews present of that hotel
	'''
    def parse_hotel(self, response):
        for href in response.xpath('//div[starts-with(@class,"quote")]/a/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_review)

        next_page = response.xpath('//div[@class="unified pagination "]/child::*[2][self::a]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_hotel)

	'''
		Parses various things mentioned from a particular review.
	'''
	
    #to get the full review content I open its page, because I don't get the full content on the main page
    #there's probably a better way to do it, requires investigation
    def parse_review(self, response):
		item = HotelSentimentItem()
		locationcontent = response.xpath('//div[starts-with(@class,"locationContent")]')
		item['hotel_name'] = locationcontent.xpath('//div[starts-with(@class,"surContent")]/a/text()').extract()[0]
		item['title'] = response.xpath('//div[@class="quote"]/text()').extract()[0][1:-1] #strip the quotes (first and last char)
		item['content'] = '\n'.join([line.strip() for line in response.xpath('(//div[@class="entry"])[1]//p/text()').extract()])
		item['stars'] = response.xpath('//span[starts-with(@class,"ui_bubble_rating")]').extract()[0]
		item['average_rating'] = response.xpath('//div[@class="rs rating"]/span').extract()[0]
		try:
			item['reviewer_name']= response.xpath('//div[@class="username mo"]/span/text()').extract()[0]
			item['location_of_reviewer'] = response.xpath('//div[@class="location"]/span/text()').extract()[0]
			item['helpful_votes']= response.xpath('//div[@class="memberBadgingNoText"]/span/text()').extract()[0]
			#item['number_of_reviews']= response.xpath('//div[@class="memberBadgingNoText"]/span/text()').extract()[0]
		except:
			pass
		return item
