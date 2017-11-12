'''
	Script to scrape from amazon. Takes product name as input from user and scrapes the first page of amazon search results for product reviews.
	Stored in reviews3.json.
	
	To run - 
	python Amazon_scraper.py
	<product name>
'''
'''
	Dependencies:
		Requests
		LXML
		SYS
		OS 
		JSON
		RE
		EXCEPTIONS
'''
import requests
from lxml import html
import sys
import os,json,re
from time import sleep
from dateutil import parser as dateparser
from exceptions import ValueError
reload(sys)
sys.setdefaultencoding('utf8')

'''
	Function to get reviews from amazon given the product ASIN
	ASIN is the unique identification number Amazon assigns to each product.
	input: ASIN
	output: data in a dict, else error 
'''
def getReview(asin):
	url = "https://www.amazon.com/dp/" + asin
	header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
	'''
		Requesting amazon for the page, possible that it can be refused.
		Amazon is not a fan of being scraped, should not be used too many times in an hour.
	'''
	try:
		r = requests.get(url,headers = header)
	except requests.exceptions.ConnectionError:
		r.status_code = "Connection refused"
	for i in range(5):
		try:
			'''
				getting html from the page
			'''
			doc = html.fromstring(r.content)
			'''
				Getting the XML paths from the html. reviews gets multiple hits so it is looped through later.
			'''
			XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
			XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
			XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
			XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
			XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
			XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'
			
			raw_product_price = doc.xpath(XPATH_PRODUCT_PRICE)
			product_price = ''.join(raw_product_price).replace(',','')
			
			raw_product_name = doc.xpath(XPATH_PRODUCT_NAME)
			product_name = ''.join(raw_product_name).strip()
			total_ratings = doc.xpath(XPATH_AGGREGATE_RATING)
			reviews = doc.xpath(XPATH_REVIEW_SECTION_1)
			if not reviews:
				reviews = doc.xpath(XPATH_REVIEW_SECTION_2)
			ratings_dict = {}
			reviews_list = []
			if not reviews:
				raise ValueError('no reviews here')
				
			
			for ratings in total_ratings:
				extracted_rating = ratings.xpath('./td//a//text()')
				if extracted_rating:
					rating_key = extracted_rating[0]
					raw_rating_value = extracted_rating[1]
					rating_value = raw_rating_value
					if rating_key:
						ratings_dict.update({rating_key:rating_value})
			'''
				Parsing through reviews for all the reviews and storing them in a dictionary.
			'''
			for review in reviews:
				XPATH_RATING = './/i[@data=hook="review-star-rating"]//text()'
				XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
				XPATH_REVIEW_POSTED_DATE = './/a[contains(@href,"/profile/")]/parent::span/following-sibling::span/text()'
				XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
				XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
				XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
				XPATH_AUTHOR  = './/a[contains(@href,"/profile/")]/parent::span//text()'
				XPATH_REVIEW_TEXT_3  = './/div[contains(@id,"dpReviews")]/div/text()'
				raw_review_author = review.xpath(XPATH_AUTHOR)
				raw_review_rating = review.xpath(XPATH_RATING)
				raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
				raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
				raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
				raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
				raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)
				
				author = ' '.join(' '.join(raw_review_author).split()).strip('By')
				
				review_rating = ''.join(raw_review_rating).replace('out of 5 stars','')
				review_header = ' '.join(' '.join(raw_review_header).split())
				review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
				review_text = ' '.join(' '.join(raw_review_text1).split())
	
				#grabbing hidden comments if present
				if raw_review_text2:
					json_loaded_review_data = json.loads(raw_review_text2[0])
					json_loaded_review_data_text = json_loaded_review_data['rest']
					cleaned_json_loaded_review_data_text = re.sub('<.*?>','',json_loaded_review_data_text)
					full_review_text = review_text + cleaned_json_loaded_review_data_text
				else:
					full_review_text = review_text
				if not raw_review_text1:
					full_review_text = ' '.join(' '.join(raw_review_text3).split())
				
				raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
				review_comments = ''.join(raw_review_comments)
				review_comments = re.sub('[A-Za-z]','',review_comments).strip()
				review_dict = { 'review_comment_count':review_comments,'review_text':full_review_text,'review_posted_date':review_posted_date,'review_header':review_header,'review_rating':review_rating,'review_author':author}
				reviews_list.append(review_dict)
			data = { 'ratings':ratings_dict,'reviews':reviews_list,'url':url,'price':product_price,'name':product_name}
			#print data['reviews'][0].keys()
			return data
		except Exception as e:
			print e
			#break

'''	
	Function to scrape for ASIN's from the first page of Amazon search results.
	Input: Item to be searched for
	Output: json containing all the reviews for the products.
'''	
def scraping_for_ASIN(search_item):
	url = "https://www.amazon.com/s?keywords=" + search_item
	try:
		htmltext = requests.get(url).content
		
	except requests.exceptions.ConnectionError:
		r.status_code = "Connection refused"
		print "didn't happen"
	'''
		regular expression to search for all ASIN's
	'''
	pattern = re.compile(r"https://www.amazon.com/.*/dp/(.*?)\"")
	asin = set(re.findall(pattern,htmltext))
	asin = list(asin)
	extracted_data = []
	for sin in asin:
		print "doing something"
		extracted_data.append(getReview(sin))
		'''	
			Sleep added so that it does not request amazon too frequently and is blocked
		'''
		sleep(5)
	'''
		Dumping the data into json file.
	'''
	f = open('reviews3.json','w')
	json.dump(extracted_data,f,indent = 4)
	#return extracted_data
'''
	Calling the function with input taken from user.
'''
scraping_for_ASIN(str(raw_input()))

