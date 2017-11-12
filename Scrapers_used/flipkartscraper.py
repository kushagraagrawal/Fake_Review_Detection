from selenium import webdriver
from selenium.webdriver.common.by import By
from contextlib import closing
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import urllib2
import re
from bs4 import BeautifulSoup
import unicodedata
import sys
print sys.path
file = open("review-file3.txt", "w")
def remove_non_ascii_1(text):

    return ''.join([i if ord(i) < 128 else ' ' for i in text])
def parseflipkart(site):
	with closing(Firefox()) as browser:
		#site = "https://www.flipkart.com/apple-iphone-5s-space-grey-16-gb/product-reviews/itmeuyd8ngnpzjg8?pid=MOBDPPZZPXVDJHSQ"
		browser.get(site)
	
		
	
		for count in range(1, 10):
			nav_btns = browser.find_elements_by_class_name('_33m_Yg')
	
			button = ""
	
			for btn in nav_btns:
				number = int(btn.text)
				if(number==count):
					button = btn
					break
	
			button.send_keys(Keys.RETURN)
			WebDriverWait(browser, timeout=10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "_2xg6Ul")))
	
			read_more_btns = browser.find_elements_by_class_name('_1EPkIx')
			
	
			for rm in read_more_btns:
				browser.execute_script("return arguments[0].scrollIntoView();", rm)
				browser.execute_script("window.scrollBy(0, -150);")
				rm.click()
	
			page_source = browser.page_source
	
			soup = BeautifulSoup(page_source, "lxml")
			ans = soup.find_all("div", class_="_3DCdKt")
			print ans
	
			for tag in ans:
				title = unicode(tag.find("p", class_="_2xg6Ul").string).replace(u"\u2018", "'").replace(u"\u2019", "'")
				title = remove_non_ascii_1(title)
				title.encode('ascii','ignore')
				content = tag.find("div", class_="qwjRop").div.prettify().replace(u"\u2018", "'").replace(u"\u2019", "'")
				content = remove_non_ascii_1(content)
				content.encode('ascii','ignore')
				content = content[15:-7]
	
				votes = tag.find_all("span", class_="_1_BQL8")
				upvotes = int(votes[0].string)
				downvotes = int(votes[1].string)
	
				file.write("Review Title : %s\n\n" % title )
				file.write("Upvotes : " + str(upvotes) + "\n\nDownvotes : " + str(downvotes) + "\n\n")
				file.write("Review Content :\n%s\n\n\n\n" % content )
	
		
start_urls = [
	"https://www.flipkart.com/moto-e3-power-white-16-gb/product-reviews/itmekgt23fgwdgkg?pid=MOBEKGT2SVHPAHTM",
	"https://www.flipkart.com/jbl-c300si-wired-headphones/product-reviews/itmehdhzk76gmzjg?pid=ACCEHDHZHXMD8GUH",
	"https://www.flipkart.com/jbl-t450black-wired-headphones/product-reviews/itmenm5tagjtqzsz?pid=ACCENM5SWQZQFZNP",
]
for url in start_urls:
	parseflipkart(url)
file.close()
#parseflipkart("https://www.flipkart.com/apple-iphone-5s-space-grey-16-gb/product-reviews/itmeuyd8ngnpzjg8?pid=MOBDPPZZPXVDJHSQ")
# https://www.flipkart.com/apple-iphone-se-space-grey-16-gb/product-reviews/itmehgsc5shnyanv?pid=MOBEHGSBRMGJFXFC
# https://www.flipkart.com/samsung-galaxy-on5-gold-8-gb/product-reviews/itmedhx3uy3qsfks?pid=MOBECCA5FHQD43KA
# https://www.flipkart.com/ant-vr-designed-lenovo/product-reviews/itmeguc3ejpccgc9?pid=SGAEGUC3DZNZHWFQ
# https://www.flipkart.com/canon-eos-1300d-dslr-camera-body-ef-s-18-55-ii/product-reviews/itmegt8fab5fsvx8?pid=CAMEGT8FR9ZXZVYM	
