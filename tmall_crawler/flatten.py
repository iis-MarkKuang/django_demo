import MySQLdb, string, sys, os, datetime, chardet

reload(sys)
sys.setdefaultencoding('utf-8')


def flatten(resultset):
	for row in resultset:
		attr_str = row['attributes']
		attr_list = attr_str.split(', ')
		for attr_k_v in attr_list:
			attr_k_v_list = attr_k_v.split(': ')

			key_name = ''
			if attr_k_v_list[0] == unicode('上市时间'):
				key_name = 'marketed_itme'
			elif attr_k_v_list[0] == unicode('是否商场同款'):
				key_name = 'sold_offline'
			elif attr_k_v_list[0] == unicode('货号'):
				key_name = 'serial_number'
			elif attr_k_v_list[0] == unicode('镜架材质'):
				key_name = 'material'
			elif attr_k_v_list[0] == unicode('颜色分类'):
				key_name = 'color_variations'
			elif attr_k_v_list[0] == unicode('镜架款式'):
				key_name = 'styles'
			elif attr_k_v_list[0] == unicode('品牌'):
				key_name = 'brand'
			elif attr_k_v_list[0] == unicode('镜面宽度'):
				key_name = 'lens_width'
			elif attr_k_v_list[0] == unicode('鼻梁宽度'):
				key_name = 'bridge_width'
			elif attr_k_v_list[0] == unicode('镜框高度'):
				key_name = 'lens_height'
			elif attr_k_v_list[0] == unicode('镜腿长度'):
				key_name = 'temple_length'
			elif attr_k_v_list[0] == unicode('适用性别'):
				key_name = 'advised_gender'
			elif attr_k_v_list[0] == unicode('服务内容'):
				key_name = 'warrenty'
			
			row[key_name] = attr_k_v_list[1].replace("'", "''")
			
	return resultset

try:
	db = MySQLdb.connect("localhost", "root", "passw0rd", "test_db", charset="utf8")
except:
	raise
	os._exit(1)
else:
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	select_sql = 'select item_name, tags, coupon_info, original_price, discount_price, sale_count, review_count, \
			tm_point_info, rotate_img_urls, brand_info, attributes, rotate_img_local_directories, is_active, \
			is_active, create_time, update_time from tmall_items_info order by item_info_id'
	cursor.execute(select_sql)
	results = cursor.fetchall()
	flattened_results = flatten(results)
	

	for row in flattened_results:
		print row
		if not 'marketed_time' in row.keys():
			row['marketed_time'] = 'no value'
		if not 'sold_offline' in row.keys():
			row['sold_offline'] = 0
		else:
			row['sold_offline'] = 1 if row['sold_offline'] == '\xe6' else 0
		if not 'serial_number' in row.keys():
			row['serial_number'] = 'no value'
		if not 'material' in row.keys():
			row['material'] = 'no value'
		if not 'color_variations' in row.keys():
			row['color_variations'] = 'no value'
		if not 'styles' in row.keys():
			row['styles'] = 'no value'
		if not 'brand' in row.keys():
			row['brand'] = 'no value'
		if not 'lens_width' in row.keys():
			row['lens_width'] = 'no value'
		if not 'bridge_width' in row.keys():
			row['bridge_width'] = 'no value'
		if not 'lens_height' in row.keys():
			row['lens_height'] = 'no value'
		if not 'temple_length' in row.keys():
			row['temple_length'] = 'no value'
		if not 'advised_gender' in row.keys():
			row['advised_gender'] = 'no value'
		if not 'warrenty' in row.keys():
			row['warrenty'] = 'no value'
		row['frame_name'] = row['item_name']
		insert_sql = "insert into tmall_frames_info (frame_name, tags, coupon_info, original_price, discount_price, \
				sale_count, review_count, tm_point_info, rotate_img_urls, brand_info, marketed_time, sold_offline, \
				serial_number, material, color_variations, styles, brand, lens_width, bridge_width, lens_height, temple_length, \
				advised_gender, warrenty, img_local_directories, create_time) \
				VALUES ('%s', '%s', '%s', '%f', '%f', '%d', '%d', '%s', '%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', \
				 '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
				(row['frame_name'].replace("'","''"), row['tags'].replace("'","''"), row['coupon_info'].replace("'","''"), row['original_price'], row['discount_price'], row['sale_count'], 
					row['review_count'], row['tm_point_info'], row['rotate_img_urls'], row['brand_info'].replace("'","''"), row['marketed_time'], 
					row['sold_offline'], row['serial_number'], row['material'], row['color_variations'], row['styles'], row['brand'], row['lens_width'], 
					row['bridge_width'], row['lens_height'], row['temple_length'], row['advised_gender'],
					  row['warrenty'], row['rotate_img_local_directories'], datetime.datetime.now())
		try:
			print 'INSERT INTO DATABASE ' + insert_sql
			cursor.execute(insert_sql)
			db.commit()
		except:
			print 'Insert failure, probably a single quote messed it up'
			db.rollback()
			raise
		
	cursor.close()


