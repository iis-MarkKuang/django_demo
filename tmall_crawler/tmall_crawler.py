# -*- coding: utf-8 -*-
import MySQLdb, urllib, urllib2, os, codecs, sys, re, string, datetime, time
from selenium import webdriver
from lxml import etree
from cookielib import CookieJar
reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(current_dir, '/tmall_rotate_images/')
pages = 100

class TmallFramesSpider:
	#start_url1 = 'https://list.tmall.com/search_product.htm?spm=a220m.1000858.0.0.RLPrMN&cat=50023064&s=120&q=%%BE%%B5%%BC%%DC&start_price=70&sort=s&style=g&search_condition=7&sarea_code=310100&from=mallfp..pc_1_searchbutton&shopType=any&industryCatId=50023064&type=pc&smToken=68fee19a3d2b4a7ab2c43b374e42ad6a&smSign=l%%2BL%%2FtHDh%%2BTmi1%%2F%%2B8MLYD%%2Fw%%3D%%3D'
	start_url_pt1 = 'https://list.tmall.com/search_product.htm?type=pc&q=%BE%B5%BC%DC&search_condition=7&totalPage=100&sort=s&style=g&from=sn_1_rightnav'
	def __init__(self):
		self.db = MySQLdb.connect("localhost", "root", "passw0rd", "test_db")
		self.db.set_character_set('utf8')
		uaList = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
	    	'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    		'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0']

		cap = webdriver.DesiredCapabilities.PHANTOMJS
		cap["phantomjs.page.settings.userAgent"] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586'
		cap["phantomjs.page.settings.resourceTimeout"] = 10000
		self.driver = webdriver.PhantomJS(desired_capabilities=cap)
		
		cursor = self.db.cursor()
		cursor.execute('select count(distinct item_name) as records_count from tmall_items_info')
		records_count = cursor.fetchone()
		self.items = int(records_count[0]) if records_count else 0
		self.page = self.items / 60 + 1
		self.img_serial_number = 1681

		cursor.close()

	def parse(self):
		while(self.page < pages):
			request_url = self.start_url_pt1 + '&jumpto=' + `self.page` + '#J_crumbs'
			self.driver.get(request_url)
			print request_url

			try:
				detail_urls_eles = self.driver.find_elements_by_xpath('//a[@class="productImg"]')
			except:
				print 'Error analyzing the html list.tmall.com'
				continue

			detail_urls = []
			print len(detail_urls_eles)
			for detail_url_element in detail_urls_eles:
				detail_urls.append(detail_url_element.get_attribute('href'))
			self.page += 1
			 
			for detail_url in detail_urls:
				print 'detail_url:' + detail_url
				self.driver.get(detail_url)
				time.sleep(5)
				open('listpage.txt', 'wb').write(self.driver.page_source)
				
				try:
					item_info_bean = {
						'item_name': self.driver.find_element_by_xpath('//div[@class="tb-detail-hd"]//h1').text.replace("'", "''").encode('utf-8'),
						'tags': self.driver.find_element_by_xpath('//div[@class="tb-detail-hd"]//p').text.replace("'", "''").encode('utf-8'),
						'original_price': float(self.driver.find_element_by_xpath('//dl[contains(@class, "tm-price-panel")]//span[@class="tm-price"]').text),
						'sale_count': int(self.driver.find_element_by_xpath('//li[contains(@class,"sellCount")]//span[@class="tm-count"]').text),
						'review_count': int(self.driver.find_element_by_xpath('//li[contains(@class,"reviewCount")]//span[@class="tm-count"]').text),
						'tm_point_info': self.driver.find_element_by_xpath('//li[contains(@class,"emPointCount")]//span[@class="tm-count"]').text,
						'rotate_img_urls': self.driver.find_elements_by_xpath('//ul[@id="J_UlThumb"]//a//img'),
						'attributes': self.driver.find_elements_by_xpath('//ul[@id="J_AttrUL"]/li'),
					}

					brand_info_reg_list = re.findall(r'(?:\"brand\":\")([^"]+)(?:\",)', self.driver.page_source)
					item_info_bean['brand_info'] = brand_info_reg_list[0].encode('gbk') if brand_info_reg_list else 'Default brand'
				except:
					print 'error analyzing the detail page elements'
					continue

				# coupon element doesn't always exist
				try:
					item_info_bean['coupon_info'] = self.driver.find_element_by_xpath('//div[@class="tm-coupon-panel"]').text.encode('utf-8')
				except:
					item_info_bean['coupon_info'] = 'No coupons'				

				# discount price element doesn't always exist
				try:
					item_info_bean['discount_price'] = float(self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[@class="tm-price"]').text)
				except:
					item_info_bean['discount_price'] = item_info_bean['original_price']

				directory = []
				rotate_img_urls_list = []
				attributes_list = []
				for img in item_info_bean['rotate_img_urls']:
					print img.get_attribute('src')
					img_byte_content = urllib2.urlopen(img.get_attribute('src')).read()
					directory.append(self.save_image(img_byte_content))
					rotate_img_urls_list.append(img.get_attribute('src'))

				for attribute in item_info_bean['attributes']:
					attributes_list.append(attribute.text)

				item_info_bean['rotate_img_urls'] = ', '.join(rotate_img_urls_list)
				item_info_bean['attributes'] = ', '.join(attributes_list).encode('utf-8')
				item_info_bean['rotate_img_local_directories'] = ', '.join(directory)
				self.save_item_info_mysql(item_info_bean);

	def save_image(self, img_byte_content):
		directory = img_dir + `self.img_serial_number` + '.jpg'
		img_stream = open(directory, 'wb')
		img_stream.write(img_byte_content)
		img_stream.close()
		self.img_serial_number += 1;
		return directory

	def save_item_info_mysql(self, item_info_bean):
		cursor = self.db.cursor()
		sql = "INSERT INTO tmall_items_info(item_name, tags, coupon_info, original_price, discount_price, sale_count, review_count, tm_point_info, rotate_img_urls, brand_info, attributes, rotate_img_local_directories, create_time) \
		VALUES ('%s', '%s', '%s', '%f', '%f', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%s')" % \
		(item_info_bean['item_name'], item_info_bean['tags'], item_info_bean['coupon_info'], item_info_bean['original_price'], item_info_bean['discount_price'], item_info_bean['sale_count'], item_info_bean['review_count'], item_info_bean['tm_point_info'], item_info_bean['rotate_img_urls'], item_info_bean['brand_info'], item_info_bean['attributes'], item_info_bean['rotate_img_local_directories'], datetime.datetime.now())
		open('listpage.txt', 'wb').write(sql)
		try:
			print 'INSERT INTO DATABASE ' + sql
			cursor.execute(sql)
			self.db.commit()
		except:
			print 'insert failure, probably a single quote messed it up'
			self.db.rollback()
			raise
		finally:
			cursor.close()

	def __del__(self):
		self.db.close()

tfs = TmallFramesSpider()
tfs.parse()