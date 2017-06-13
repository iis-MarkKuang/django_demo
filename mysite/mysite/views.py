from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import loader, RequestContext
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.conf import settings
from django.core import serializers
from django.db.models import Count
from gallery.models import UserProfile, AuthUser, UserVote, ImageView
from .forms import LoginForm, RegisterForm
import time, json, re

@csrf_exempt
def login(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(settings.EXTERNAL_INDEX_URL)
	current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	if request.method.lower() == 'post':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST.get('username', '')
			password = request.POST.get('password', '')
			
			username_filter_result = User.objects.filter(username=username)
			if len(username_filter_result) == 0:
				# check if user is using mobile number to log in
				pattern = re.compile(r'[0-9]{11}')
				match = pattern.match(username)
				error = None
				if not match:
					error = settings.ERROR_USERNAME_NOT_EXIST
				else:
					user_profile_result = UserProfile.objects.filter(phone=username)
					if len(user_profile_result) == 0:
						error = settings.ERROR_PHONE_NOT_EXIST
						
				if error:
					return render_to_response('login.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})
				else:
					username = User.objects.filter(id=user_profile_result[0].user_id)[0].username
			user = auth.authenticate(username = username, password = password)
			if user is not None and user.is_active:
				auth.login(request, user)
				if request.GET.has_key('next'):
					return HttpResponseRedirect(request.GET['next'])
				return HttpResponseRedirect(settings.EXTERNAL_INDEX_URL)

			else:
				# error = err_msg(form, [{'msg': 'password is wrong', 'password': password}])
				error = settings.ERROR_WRONG_PASSWORD
				# return HttpResponse(json.dumps(error), content_type='application/json')
				return render_to_response('login.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

		else:
			return render_to_response('login.html', {'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})
	else:
		form = LoginForm()
		return render_to_response('login.html', {'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

def logout(request):
	if not request.user.is_authenticated():
		# error = 'unauthorized'
		return HttpResponse('Not authorized', status=401)
		# return HttpResponseRedirect(settings.INTERNAL_LOGIN_URL + '?message=' + error)
	else:
		try:
			auth.logout(request)
		except Exception, e:
			return HttpResponse('Not authorized', status=401)
			# return HttpResponseRedirect(settings.INTERNAL_LOGIN_URL + '?message=' + str(e))
		else:
			return HttpResponse('Logout successful', status=200)
			# return HttpResponseRedirect(settings.INTERNAL_LOGIN_URL)


def logged_in(request):
	return HttpResponse('Logged in', content_type='text/plain', status=200)

@csrf_exempt
def register(request):
	current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

	if request.user.is_authenticated():
		return logged_in(request)
	try:
		if request.method.lower() == 'post':
			username = request.POST.get('username','')
			password = request.POST.get('password', '')
			password_repeat = request.POST.get('password_repeat', '')
			phone = request.POST.get('phone', '')

			form = RegisterForm(request.POST)
			if not form.is_valid():
				error = settings.ERROR_FORM_INVALID
				# return HttpResponse(json.dumps(error), content_type='application/json')
				return render_to_response('register.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

			elif password != password_repeat:
				error = settings.ERROR_PASSWORD_NOT_IDENTICAL
				# return HttpResponse(json.dumps(error), content_type='application/json')
				return render_to_response('register.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

			username_filter_result = User.objects.filter(username=username)
			if len(username_filter_result) > 0:
				error = settings.ERROR_USERNAME_TAKEN
				# return HttpResponse(json.dumps(error), content_type='application/json')
				return render_to_response('register.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

			phone_filter_result = UserProfile.objects.filter(phone=phone)
			if len(phone_filter_result) > 0:
				error = settings.ERROR_PHONE_TAKEN
				return render_to_response('register.html', {'error': error, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

			user = User()
			user.username = username
			user.set_password(password)
			user.save()

			user_profile = UserProfile()
			user_profile.user = user
			user_profile.phone = phone
			user_profile.save()

			new_user = auth.authenticate(username = username, password = password)
			if new_user is not None and user_profile is not None:
				auth.login(request, new_user)

				return HttpResponseRedirect(settings.EXTERNAL_INDEX_URL)

		else:
			form = RegisterForm()
	except Exception,e:
		# error = err_msg({}, [{'msg': str(e)}])
		return render_to_response('register.html', {'error': str(e), 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

		# return HttpResponse(json.dumps(error), content_type='application/json')

	return render_to_response('register.html', {'curtime': current_time, 'form': form, 'logo_img_name': settings.LOGO_IMG_NAME})

def profile(request):
	if not request.user.is_authenticated():
		return HttpResponse('Not authorized', status=401)

	user_obj = User.objects.get(username=request.user.username)
	# user_profile_obj = UserProfile.objects.get(user=request.user)
	result = json.loads('{}')
	result['user'] = json.loads(serializers.serialize('json', {user_obj}))
	# result['user_profile'] = json.loads(serializers.serialize('json', {user_profile_obj}))
	return HttpResponse(serializers.serialize('json', {user_obj}), content_type='application/json')

def get_user_data(request):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		raw_sql = 'select id, count(id) as user_count, date(date_joined) as day_joined from auth_user group by day_joined'
		users = AuthUser.objects.raw(raw_sql)
		users_info = []
		for user in users:
			user_info = json.loads('{}')
			user_info['date'] = str(user.day_joined)
			user_info['registered_users_count'] = user.user_count
			users_info.append(user_info)
		return HttpResponse(json.dumps(users_info), content_type='text/plain')
	except:
		raise

def get_votes_data(request, date):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		user_votes_records = UserVote.objects(date=date)
		user_votes_result = []
		for user_votes_record in user_votes_records:
			voting_info = json.loads('{}')
			voting_info['username'] = user_votes_record['username']
			voting_info['vote'] = user_votes_record['vote']
			voting_info['image_id'] = user_votes_record['image_id']
			user_votes_result.append(voting_info)
		return HttpResponse(json.dumps(user_votes_result), content_type='text/plain')
	except:
		raise

def get_image_views_data(request, date):
	if not request.user.is_authenticated():
		return HttpResponse('not authorized', status=401)
	try:
		image_views_records = ImageView.objects(date=date)
		image_views_result = []
		for image_views_record in image_views_records:
			views_info = json.loads('{}')
			views_info['image_id'] = image_views_record['image_id']
			views_info['viewed_times'] = image_views_record['times']
			image_views_result.append(views_info)
		return HttpResponse(json.dumps(image_views_result), content_type='text/plain')
	except:
		raise