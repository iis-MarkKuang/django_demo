# test for ubuntu git
from facepp import API, File
from pyres import *
from pyres.worker import Worker
from string import Template
from PIL import Image
import getopt, sys, MySQLdb, pymongo, json, codecs, os, logging, ast, dateutil.parser

config_file_abs_path = os.getcwd() + '/' + 'config.json'
with open(config_file_abs_path, 'r') as f:
	config = json.load(f)
	r = ResQ(server=config['redis']['redis_server'], password=config['redis']['redis_password'])
	tracer = logging.getLogger(config['logger']['logger_name'])
	tracer.setLevel(logging.INFO)
	tracer.addHandler(logging.FileHandler(config['logger']['logging_file_handler']))
	api = API(config['facepp']['facepp_api_key'], config['facepp']['facepp_api_secret'])

def form_global_config(config_file_rel_path):
	config_file_abs_path = os.getcwd() + '/' + config_file_rel_path
	if not os.path.isfile(config_file_abs_path):
		print 'Config file not found: ' + config_file_abs_path
		sys.exit()
	with open(config_file_abs_path, 'r') as f:
		try:
			config = json.load(f)
		except:
			print 'not valid json format'
			sys.exit()
		
def setup_redis_and_logging():
	r = ResQ(server=config['redis']['redis_server'], password=config['redis']['redis_password'])
	tracer = logging.getLogger(config['logger']['logger_name'])
	tracer.setLevel(logging.INFO)
	tracer.addHandler(logging.FileHandler(config['logger']['logging_file_handler']))

def setup_facepp_api():
	api = API(config['facepp']['facepp_api_key'], config['facepp']['facepp_api_secret'])

# config parameter explain: 
# 	offset: the index of mysql records you want to start with
# 	payload: the number of records per job
#	upper_limit: the upper limit of mysql record index, when hit, stop
def schedule_and_run_resque():
	print 'scheduling'
	offset, upper_limit, payload = config['payload']['offset'], config['payload']['upper_limit'], config['payload']['payload']
	while(offset < upper_limit):
		r.enqueue(FaceppAPIFetcher, offset, payload)
		offset += payload
	Worker.run([config['redis']['resque_queue_name']], server=config['redis']['redis_server'])


class FaceppAPIFetcher:
	queue = config['redis']['resque_queue_name']
	@staticmethod
	def perform(start, limit):
		resultset = FaceppAPIFetcher.fetchMysqlResults(start, limit)
		FaceppAPIFetcher.checkMongoDbDuplicate(resultset[0])
		facepp_results = FaceppAPIFetcher.getFaceppResults(resultset)
		store_result = []
		for facepp_result in facepp_results:
			try:
				store_result.append(FaceppAPIFetcher.storeMongoDb(facepp_result))
			except:
				continue
				
	@classmethod
	def fetchMysqlResults(self, start, limit, tablename = 'insta_glasses_pics_info'):
		try:
			db = MySQLdb.connect(
				config['mysql']['mysql_host'], 
				config['mysql']['mysql_usr'], 
				config['mysql']['mysql_pwd'], 
				config['mysql']['mysql_db']
			)
		except: 
			raise
			os._exit(1)
		else:
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
			sql = 'select username, insta_pic_info_id, pic_url, pic_type, instagram_likes, tags, comments,\
			 		 unix_timestamp(create_time) as create_time, unix_timestamp(update_time) as update_time,\
			 		 image_local_path, instagram_img_id, unix_timestamp(user_posted_time) as user_posted_time,\
			 		 enlarge_times, likes, dislikes from insta_glasses_pics_info group by pic_url \
			 		 order by insta_pic_info_id limit ' + str(start) + ' , ' + str(limit)
			cursor.execute(sql)
			results = cursor.fetchall()
			cursor.close()
			db.close()
			return results

	@classmethod
	def getFaceppResults(self, results):
		result = []
		for row in results:
			image_dir = config['images_dir'] + row['image_local_path']
			if not os.path.isfile(image_dir):
				print 'no such file as ' + image_dir + ' , moving on...'
				continue
			if os.stat(image_dir).st_size == 0:
				print image_dir + ' File is empty, moving on...'
				continue

			# facepp throws errors for some .jpg formats, adding this to unblock jobs
			try:
				detect_result = self.getFaceppResult(row)
			except:
				continue

			flat_detect_result = self.flattenJson(detect_result)
			size_result = self.getImageSizeInfo(image_dir)
			bytesize_result = os.stat(image_dir).st_size
			if detect_result['face']:
				result_one = self.getResultTemplate(row)
				result_one['face_info'] = []
				result_one['race_info'] = []
				result_one['age_info'] = []
				result_one['gender_info'] = []
				result_one['smiling_info'] = []
				result_one['glass_info'] = []
				result_one['face_ids'] = []
				for single_face in detect_result['face']:
					face_info = {}

					# facepp throws errors for some .jpg formats
					try:
						landmark_result = self.getFaceppResult(row, single_face['face_id'])
					except:
						continue

					face_info['face_id'] = single_face['face_id']
					face_info['detect_result'] = self.flattenJson(single_face)
					#face_info['landmark_result'] = self.flattenJson(landmark_result['result'][0])
					face_info['landmark_result'] = json.dumps(landmark_result['result'][0])
					result_one['face_info'].append(face_info)
					
					if face_info['detect_result']['attribute_race_value'] == 'Asian':
						result_one['race_info'].append('1')
					elif face_info['detect_result']['attribute_race_value'] == 'White':
						result_one['race_info'].append('2')
					else:
						result_one['race_info'].append('3')

					#AGE_INFO
					if face_info['detect_result']['attribute_age_value'] < 15:
						#adolescent
						result_one['age_info'].append('1')
					elif face_info['detect_result']['attribute_age_value'] < 40:
						#youth
						result_one['age_info'].append('2')
					elif face_info['detect_result']['attribute_age_value'] < 60:
						#middle-age
						result_one['age_info'].append('3')
					else:
						#elderly
						result_one['age_info'].append('4')
					
					#GENDER_INFO
					if face_info['detect_result']['attribute_gender_value'] == 'Male':
						result_one['gender_info'].append('1')
					else:
						result_one['gender_info'].append('2')
					if face_info['detect_result']['attribute_smiling_value'] > 50.0:
						result_one['smiling_info'].append('1')
					else:
						result_one['smiling_info'].append('2')
					
					#GLASSES_INFO
					# sunglasses
					if face_info['detect_result']['attribute_glass_value'] == 'Dark':
						result_one['glass_info'].append('1')
					# eyeglasses
					elif face_info['detect_result']['attribute_glass_value'] == 'Normal':
						result_one['glass_info'].append('2')
					# noglasses
					else:
						result_one['glass_info'].append('3')
					
					result_one['face_ids'].append(single_face['face_id'])
				result.append(result_one)
			else:
				result_one = self.getResultTemplate(row)
				result_one['detect_result'] = flat_detect_result
				result.append(result_one)
		return result

	@classmethod
	def getResultTemplate(self, row):
		result_one = {}
		# result_one['_id'] = row['insta_pic_info_id']
		result_one['25p'] = 1
		result_one['quality'] = 0
		result_one['repeated'] = 1
		result_one['instagram_img_id'] = row['instagram_img_id']
		result_one['instagram_likes'] = row['instagram_likes']
		result_one['user_posted_time'] =row['user_posted_time']
		result_one['image_local_path'] = row['image_local_path']
		result_one['insta_pic_info_id'] = row['insta_pic_info_id']
		try: 
			result_one['tags'] = ast.literal_eval(row['tags']) 
		except:
			result_one['tags'] = row['tags'].split(', ')
		try:
			result_one['comments'] = ast.literal_eval(row['comments'])
		except:
			result_one['comments'] = []

		image_size_tuple = self.getImageSizeInfo(row['image_local_path'])
		result_one['size_result_tuple'] = image_size_tuple
		#small images rule: height and width both less than or equal 640 pixels
		if image_size_tuple[0] <= 640 and image_size_tuple[1] <= 640:
			result_one['size_result'] = '1'
		#large images rule: height and width both more than or equal 1080 pixels
		elif image_size_tuple[0] >= 1080 and image_size_tuple[1] >= 1080:
			result_one['size_result'] = '3'
		else:
			result_one['size_result'] = '2'

		result_one['bytesize_result'] = os.stat(row['image_local_path']).st_size
		result_one['likes'] = row['likes']
		result_one['dislikes'] = row['dislikes']
		result_one['pic_url'] = row['pic_url']
		result_one['pic_type'] = row['pic_type']
		result_one['create_time'] = row['create_time']
		result_one['update_time'] = row['update_time']
		result_one['enlarge_times'] = row['enlarge_times']
		result_one['active'] = 1
		return result_one

	@classmethod
	def getFaceppResult(self, result_row, face_id = None, image_field_name = 'image_local_path'):
		# not null field in mysql 'image_local_path' so there must be value
		image_file = open(config['images_dir'] + result_row[image_field_name], 'rb')
		image_byte_content = image_file.read()
		try:
			result = self.callFaceppApi(image_byte_content, face_id)
		except:
			raise
		return result

	@classmethod
	def callFaceppApi(self, image_byte_content, face_id = None):
		for attempts in range(5):
			try:
				# face_id is a necessary parameter to the landmark api, so if it's passed in here, it's a landmark invoke
				if face_id:
					print 'Uploading image to facepp api for landmark.'
					result = api.detection.landmark(img=File('b.jpg', image_byte_content), face_id=face_id, type='25p')
				else:
					print 'Uploading image to facepp api for detection.'
					result = api.detection.detect(img=File('b.jpg', image_byte_content), mode = 'normal', attribute = 'glass,pose,gender,age,race,smiling')
				return result
			except:
				print 'DEBUG, upload image failed, timeout, retrying...'
		else:
			print 'ERROR, all attempts to call facepp api failed, timeout.'
			

	@classmethod
	def storeMongoDb(self, data):
		mongo = pymongo.MongoClient(config['mongodb']['mongodb_host'], config['mongodb']['mongodb_port'])
		db = mongo.test
		collection = db.image_info
		result = collection.insert(data)
		# result = collection.insert_many(data)
		mongo.close()
		return result

	@classmethod
	def checkMongoDbDuplicate(self, data):
		mongo = pymongo.MongoClient(config['mongodb']['mongodb_host'], config['mongodb']['mongodb_port'])
		db = mongo.test
		result = db.image_info.find_one({'_id':data['insta_pic_info_id']})
		if result:
			sys.exit(2)

	@classmethod
	def getImageSizeInfo(self, image_local_path):
		image = Image.open(image_local_path)
		return image.size

	@classmethod
	def flattenJson(self, json):
		result = {}
		def flatten(node, label=''):
			if type(node) is dict:
				for key in node:
					flatten(node[key], label + key + '_')
			elif type(node) is list:
				idx = 0
				for item in node:
					flatten(item, label + str(idx) + '_')
					idx += 1
			else:
				result[label[:-1]] = node
		flatten(json)
		return result


def usage():
	print 'This script is used to turn instagram image records stored in mysql to'
	print 'mongodb records, and upload image to facepp API for detection and'
	print 'landmark detection, using pyres as task scheduler and redis as database'
	print 'to monitor the process. This script takes one argument'
	print 'the path of the config file'
	print 'e.g type "python facepp_script.py config.json"'

def main():
	# try:
	# 	opts, args = getopt.getopt(argv, '')
	# except getopt.GetoptError:
	# 	usage()
	# 	raise

	# config_file = args[0]
	# form_global_config(config_file)
	# setup_redis_and_logging()
	# setup_facepp_api()
	schedule_and_run_resque()

if __name__ == '__main__':
	# main(sys.args[1:])
	main()