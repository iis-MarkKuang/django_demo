from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.template import loader, RequestContext
from django.forms.formsets import formset_factory
from django.conf import settings
from django.db.models import Q
from mongoengine.queryset.visitor import Q as MQ

from gallery.models import Image, UserVote, ImageView
from bson import json_util
from bson.objectid import ObjectId
from mongoengine.base import BaseDocument
from urllib import unquote
import json, re, time, os, objectpath, ast

images_per_page = settings.IMAGES_PER_PAGE
sort_choices = ['user_posted_time',
				'-user_posted_time',
				'instagram_likes',
				'-instagram_likes',
				'enlarge_times',
				'-enlarge_times']

class MongoEncoder(json.JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs)

# acts as router based on request's http method
# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def tags_resource(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	if request.method.lower() == 'get':
		return tags(request, image_id)
	elif request.method.lower() == 'post':
		return add_tag(request, image_id)
	elif request.method.lower() == 'delete':
		return delete_tag(request, image_id)

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def add_tag(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	content = request.GET.get('content')
	if not content:
		return HttpResponse('Please input your tags content', content_type='text/plain', status=400)
	image.tags.append(content)
	length = len(image.tags)
	image.save()
	return HttpResponse(length - 1, content_type='text/plain')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def delete_tag(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	idx = request.GET.get('idx')
	if not idx:
		return HttpResponse('Please identify tag idx to delete', content_type='text/plain', status=400)
	else:
		try:
			idx = int(idx)
			result = image.tags[idx]
			image.tags.pop(idx)
			image.save()
			return HttpResponse(result, content_type='text/plain', status=201)
		except IndexError:
			return HttpResponse('index out of range', content_type='text/plain', status=400)

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def tags(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	return HttpResponse(json.dumps(image.tags, cls=MongoEncoder), content_type='application/json')


# acts as router based on request's http method
# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def images_resource(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	if request.method.lower() == 'get':
		return detail(request, image_id)
	elif request.method.lower() == 'delete':
		return delete_img(request, image_id)

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def index(request):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	sort = request.GET.get('sort')
	if sort and sort in sort_choices:
		images = Image.objects(is_25p=0,active=1,quality=1,repeated=0).exclude('face_info').order_by(sort)
	else:
		images = Image.objects(is_25p=0,active=1,quality=1,repeated=0).exclude('face_info')

	# search and filter
	search_str = request.GET.get('search')
	search_str = unquote(search_str) if search_str else search_str

	if search_str:
		search_params_list = re.split('; |, | |,|\n', search_str)
		images = images(tags__in=search_params_list)

	filter_str = request.GET.get('filter')
	filter_str = unquote(filter_str) if filter_str else filter_str
	try:
		json_obj = json.loads(open(os.path.dirname(__file__) + '/tags.json').read())
		json_tree = objectpath.Tree(json_obj)
	except:
		raise

	if filter_str:
		filter_params_list = re.split('; |, | |,|\n', filter_str)

		for filter_param in filter_params_list:
			try:
				node = list(json_tree.execute('$..options[@.id is"' + filter_param + '"]'))[0]
			except:
				print 'error finding ' + filter_param + ' in tags.json file'
				continue

			key_value = node['query'].split('=')
			mapping = {}
			mapping[str(key_value[0])] = ast.literal_eval(key_value[1])
			images = images(**mapping)

	response = json.loads('{}')
	response['total'] = images.count()

	limit = request.GET.get('limit')
	limit = limit if limit else images_per_page

	paginator = Paginator(images, limit)
	page = request.GET.get('page')

	try:
		images = paginator.page(page)
	except PageNotAnInteger:
		images = paginator.page(1)
	except EmptyPage:
		images = paginator.page(paginator.num_pages)

	# get account voting infomation
	response['images_list'] = json.loads(images.object_list.to_json())
	for image in response['images_list']:
		try:
			image['user_vote'] = UserVote.objects.get(username=request.user.username, image_id=int(image['_id'])).vote
		except:
			image['user_vote'] = 0
	return HttpResponse(json.dumps(response), content_type='application/json')

def format(request, image_id):
	image = Image.objects.get(_id=image_id)
	try:
		image_format = image.image_local_path.split('.')[-1].upper()
	except:
		image_format = ''
	return HttpResponse(image_format, content_type='text/plain')

def image_viewed_times_plus(image_id):
	image = Image.objects.get(_id=image_id)
	image.enlarge_times += 1
	image.save()
	today_date_str = time.strftime('%Y%m%d', time.localtime())
	image_views = ImageView.objects(image_id=image_id, date=today_date_str)
	if image_views.count() == 0:
		image_view = ImageView(image_id=image_id, date=today_date_str, times = 1).save()
	else:
		image_view = image_views[0]
		image_view.times += 1
		image_view.save()

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def detail(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		image_viewed_times_plus(image_id)
	except:
		raise
	image = json.loads(Image.objects.get(_id=image_id).to_json())
	try:
		image['user_vote'] = UserVote.objects.get(username=request.user.username, image_id=image_id).vote
	except:
		image['user_vote'] = 0
	image['format'] = image['image_local_path'].split('.')[-1]
	return HttpResponse(json.dumps(image), content_type='application/json')

#deprecated
# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def size(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	size_info_tuple = Image.objects.get(_id=image_id).size_result_tuple
	return HttpResponse(str(size_info_tuple[0]) + ' X ' + str(size_info_tuple[1]) + ' px', content_type='application/json')

#deprecated
# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def bytesize(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	bytesize_info = Image.objects.get(_id=image_id).bytesize_result
	return HttpResponse(bytesize_info, content_type='application/json')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def landmark(request, image_id, face_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	if image.face_info:
		for face_info in image.face_info:
			if face_info.face_id == face_id:
				return HttpResponse(json.dumps(face_info.landmark_result, cls=MongoEncoder), content_type='application/json')

	raise Http404('No landmark info with given params found')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def detection(request, image_id, face_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	if image.face_info:
		for face_info in image.face_info:
			if face_info.face_id == face_id:
				return HttpResponse(json.dumps(face_info.detect_result, cls=MongoEncoder), content_type='application/json')

	raise Http404('No detection info with given params found')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def vote_up(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	return handle_account_votes(request, int(image_id), 1)

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def vote_down(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	return handle_account_votes(request, int(image_id), -1)

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def viewcount(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	return HttpResponse(image.enlarge_times, content_type='text_plain')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def face_ids(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	images = Image.objects.filter(_id=image_id)
	face_ids = []
	for image in images:
		face_ids.append(image.detect_result.face_id)
	return HttpResponse(json.dumps(face_ids), content_type='application/json')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def comments(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	image = Image.objects.get(_id=image_id)
	return HttpResponse(json.dumps(image.comments, cls=MongoEncoder), content_type='application/json')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def delete_img(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	if request.method == 'DELETE':
		image = Image.objects.get(_id=image_id)
		if image.active == 0:
			return HttpResponse('Image info already deleted', content_type='text/plain', status=400)
		image.active = 0
		image.save()
		return HttpResponse(image_id, content_type='text/plain')

def handle_account_votes(request, image_id, vote):
	try:
		today_date_str = time.strftime('%Y%m%d', time.localtime())
		user_votes = UserVote.objects(username=request.user.username, image_id=image_id)
		image = Image.objects.get(_id=image_id)
		original_likes = image.likes
		original_dislikes = image.dislikes
		if user_votes.count() == 0:
			user_vote = UserVote(username=request.user.username, image_id=image_id, vote = vote, date = today_date_str).save()
			if vote == 1:
				image.likes += 1
			elif vote == -1:
				image.dislikes += 1
		else:
			user_vote = user_votes[0]

			# cancel vote
			if user_vote.vote == vote:
				user_vote.vote = 0
				if vote == -1:
					image.dislikes -= 1
				elif vote == 1:
					image.likes -= 1

			# change vote to opposite
			elif user_vote.vote == -vote:
				user_vote.vote = vote
				image.dislikes -= vote
				image.likes += vote

			# from 0 to upvote or downvote
			else:
				user_vote.vote = vote
				if vote == 1:
					image.likes += 1
				elif vote == -1:
					image.dislikes += 1
		if image.likes < 0 or image.dislikes < 0:
			#rollback
			image.likes = original_likes
			image.dislikes = original_dislikes
			print 'minus figure exception, rollback to original'
	except:
		#rollback
		image.likes = original_likes
		image.dislikes = original_dislikes
		image.save()
		raise
	else:
		user_vote.date = today_date_str
		user_vote.save()
		image.save()
		print 'save success: vote param: ' + str(vote) + ' and mongo likes: ' + str(image.likes) + ' and mongo dislikes: ' + str(image.dislikes)
		return HttpResponse('success')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def user_vote(request, image_id):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		user_vote = UserVote.objects.get(username=request.user.username, image_id=image_id)
	except:
		return HttpResponse('No posts yet', content_type='application/json')

# @login_required(login_url=settings.INTERNAL_LOGIN_URL)
def get_filter_tags(request):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		json_obj = json.loads(open(os.path.dirname(__file__) + '/tags.json').read())
		json_tree = objectpath.Tree(json_obj)
		return HttpResponse(json.dumps(json_obj), content_type='application/json')
	except Exception, e:
		return HttpResponse(e, content_type='text/plain', status=500)