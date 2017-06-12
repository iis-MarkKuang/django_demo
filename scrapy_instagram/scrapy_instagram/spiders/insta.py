import scrapy, codecs, time, sys, json, requests, datetime, re, MySQLdb, urllib, cStringIO, os, ast
from facepp import API, File
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.utils.project import get_project_settings
from string import Template
from pyres import ResQ

reload(sys)
settings = get_project_settings()
sys.setdefaultencoding('utf-8')
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)
db = MySQLdb.connect(
	settings['MYSQL_HOST'], 
	settings['MYSQL_USER'], 
	settings['MYSQL_PASSWORD'], 
	settings['MYSQL_DB']
)
# path = os.path.abspath(os.path.dirname(sys.argv[0]))
current_dir = os.path.dirname(__file__)
images_dir = os.path.join(current_dir, '/instagram_images/')
headshot_url = "https://www.instagram.com/explore/tags/headshot/"
selfie_url = "https://www.instagram.com/explore/tags/selfie/"
glasses_url = "https://www.instagram.com/explore/tags/glassses/"
eyewear_url = "https://www.instagram.com/explore/tags/eyewear/"
rayban_url = "https://www.instagram.com/explore/tags/rayban"
eyeglasses_url = "https://www.instagram.com/explore/tags/eyeglasses/"
sunglasses_url = "https://www.instagram.com/explore/tags/sunglasses/"
dogs_url = "https://www.instagram.com/explore/tffags/dogs/"
chosen_url = sunglasses_url

class InstaSpider(scrapy.Spider):
	image_serial_number = 159235
	upper_limit = 170000
	offset = 0
	name = "insta"
	allowed_domains = ["www.instagram.com"]
	start_urls = [
		chosen_url,
	]
	queue = "Scrapy"

	def init(self):
		cursor = db.cursor()
		cursor.execute("select max(convert(SUBSTRING_INDEX(image_local_path, '/', -1), UNSIGNED INTEGER)) AS max_image_num from insta_selfie_pics_info;")
		result = cursor.fetchone()
		self.image_serial_number = 1 if result is None else int(result[0]) + 1
		self.upper_limit = self.image_serial_number + self.offset
		cursor.close()

	def parse_next_page(self, response):
		json_obj = json.loads(response.xpath('.//script[not(@src) and @type="text/javascript"]').extract()[3].lstrip('<script type="text/javascript">window._sharedData = ').rstrip(';</script>'))
		max_id = json_obj["entry_data"]["TagPage"][0]["tag"]["media"]["page_info"]["end_cursor"]
		yield scrapy.Request(chosen_url + "?max_id=" + max_id, callback=self.parse)

	def parse(self, response):
		#self.init()
		json_obj = json.loads(response.xpath('.//script[not(@src) and @type="text/javascript"]').extract()[3].lstrip('<script type="text/javascript">window._sharedData = ').rstrip(';</script>'))
		max_id = json_obj["entry_data"]["TagPage"][0]["tag"]["media"]["page_info"]["end_cursor"]
		if not max_id:
			return
		if self.check_mysql_field_exists('insta_max_id', 'insta_max_id', max_id):
			print 'This page is reserved for other crawlers, moving on...'
			self.logger.info('Page with max_id ' + max_id + ' is already crawled, moving on...')
			yield scrapy.Request(chosen_url + "?max_id=" + max_id, callback=self.parse_next_page)
			return
		
		self.save_mysql_single_string_field('insta_max_id', 'insta_max_id', max_id)
		top_posts = json_obj["entry_data"]["TagPage"][0]["tag"]["top_posts"]["nodes"]
		# assume that the hot posts on instagram changes every 100 grabs, that's about every 2 hours and 50 minutes
		if self.image_serial_number % 1000 == 0:
			for node in top_posts:
				post_id = node["code"]
				if self.check_mysql_field_exists('insta_post_id', 'insta_post_id', post_id):
					print 'This top post is already crawled, moving on...'
					self.logger.info('Post with post_id ' + post_id + ' is already crawled, moving on...')
					continue
				else:
					self.save_mysql_single_string_field('insta_post_id', 'insta_post_id', post_id)	
					yield scrapy.Request("https://www.instagram.com/p/" + node["code"] + '/', callback=self.parse_detail_page)
		else:
			latest_posts = json_obj["entry_data"]["TagPage"][0]["tag"]["media"]["nodes"]
			for node in latest_posts:
				post_id = node["code"]
				if self.check_mysql_field_exists('insta_post_id', 'insta_post_id', post_id):
					print 'This latest post is already crawled, moving on...'
					self.logger.info('Post with post_id ' + post_id + ' is already crawled, moving on...')
					continue
				else:
					self.save_mysql_single_string_field('insta_post_id', 'insta_post_id', post_id)
					yield scrapy.Request("https://www.instagram.com/p/" + node["code"] + '/', callback=self.parse_detail_page_latest)
		yield scrapy.Request(chosen_url + "?max_id=" + max_id, callback=self.parse)

			
	def parse_detail_page(self, response):
		json_obj = json.loads(response.xpath("//body//script[not(@src) and @type='text/javascript']").extract()[0].lstrip('<script type="text/javascript">window._sharedData = ').rstrip(';</script>')).get('entry_data').get('PostPage')[0].get("media")
		# if json_obj["caption"].find('glasses') != -1:
		# 	print 'filtering glasses headshots...'
		# 	return
		image_byte_content = urllib.urlopen(json_obj["display_src"]).read()
		directory = self.save_image(image_byte_content)
		image_info_bean = {
    		"username": json_obj["owner"]["username"].replace('\\', '\\\\'),
			"pic_url": json_obj["display_src"],
			"pic_type": 1,
    		"likes": json_obj["likes"]["count"],
    		"tags": json.dumps(re.findall(r'(?:(?<=#))(?:[ ]*)([^\s#]*)(?:[ ]*)(?:(?=#)|(?=$))', json_obj["caption"])).replace('\\', '\\\\'),
    		"comments": ', '.join(json.dumps(json_obj["comments"]["nodes"])).replace('\\', '\\\\'),
    		"posted_time": datetime.datetime.fromtimestamp(json_obj["date"]).strftime('%Y-%m-%d %H:%M:%S'),
    		"image_local_path": directory,
		}
		self.save_image_info_mysql(image_info_bean)
		return

	def parse_detail_page_latest(self, response):
		json_obj = json.loads(response.xpath("//body//script[not(@src) and @type='text/javascript']").extract()[0].lstrip('<script type="text/javascript">window._sharedData = ').rstrip(';</script>')).get('entry_data').get('PostPage')[0].get("media")
		# if json_obj["caption"].find('glasses') != -1:
		# 	print 'filtering glasses headshots...'
		# 	return
		image_byte_content = urllib.urlopen(json_obj["display_src"]).read()
		directory = self.save_image(image_byte_content)
		image_info_bean = {
    		"username": json_obj["owner"]["username"],
			"pic_url": json_obj["display_src"],
			"pic_type": 2,
    		"likes": json_obj["likes"]["count"],
    		"tags": json.dumps(re.findall(r'(?:(?<=#))(?:[ ]*)([^\s#]*)(?:[ ]*)(?:(?=#)|(?=$))', json_obj["caption"])),
    		"comments": json.dumps(json_obj["comments"]["nodes"]),
    		"posted_time": datetime.datetime.fromtimestamp(json_obj["date"]).strftime('%Y-%m-%d %H:%M:%S'),
    		"image_local_path": directory,
		}
		self.save_image_info_mysql(image_info_bean)
		return

	def save_image_info_mysql(self, image_info_bean):
		cursor = db.cursor()
		sql = "INSERT INTO insta_glasses_pics_info(username, pic_url, pic_type, likes, tags, comments, user_posted_time, create_time, image_local_path, analyzed) \
			VALUES ('%s', '%s', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%d')" % \
			(image_info_bean['username'], image_info_bean['pic_url'], image_info_bean['pic_type'], image_info_bean['likes'], image_info_bean['tags'], image_info_bean['comments'], image_info_bean['posted_time'], datetime.datetime.now(), image_info_bean['image_local_path'], 1)
		try:
			print 'INSERT INTO DATABASE ' + sql
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()
		finally:
			cursor.close()

	def save_image(self, image_byte_content):
		if(self.image_serial_number > self.upper_limit):
			sys.exit(2)
		directory = images_dir + `self.image_serial_number` + '.jpg'
		output = open(directory, 'wb')
		output.write(image_byte_content)
		output.close()
		self.image_serial_number += 1
		return directory

	def save_mysql_single_string_field(self, table_name, field_name, field_value):
		cursor = db.cursor()
		sql = "INSERT INTO " + table_name + "( " + field_name + ") values ('%s')" % (field_value)
		try:
			print 'INSERT INTO DATABASE ' + sql
			cursor.execute(sql)
			db.commit()
		except:
			print 'INSERT FAILED, ROLLBACK'
			db.rollback()
		finally:
			cursor.close()

	def check_mysql_field_exists(self, table_name, field_name, field_value):
		if not field_value:
			return 0
		cursor = db.cursor()
		sql = 'SELECT * from ' + table_name + ' where ' + field_name + ' = \"' + field_value + '\"'
		cursor.execute(sql)
		print sql
		result = cursor.fetchone()
		cursor.close()
		return 0 if result is None else 1
