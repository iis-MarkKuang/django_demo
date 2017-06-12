from django.conf.urls import url
from gallery import views


urlpatterns = [
	
	# ex: /gallery/
	url(r'^$', views.index, name='index'),
	url(r'^imgs/(?P<image_id>[0-9]+)/detail/$', views.detail, name='detail'),
	# ex: /gallery/image/5/
	url(r'^imgs/(?P<image_id>[0-9]+)$', views.images_resource),

	# add/delete tags
	url(r'^imgs/(?P<image_id>[0-9]+)/tags/$', views.tags_resource),

	url(r'^imgs/(?P<image_id>[0-9]+)/size/$', views.size, name='size'),
	url(r'^imgs/(?P<image_id>[0-9]+)/bytesize/$', views.bytesize, name='bytesize'),
	
	url(r'^imgs/(?P<image_id>[0-9]+)/voteup/$', views.vote_up, name='vote_up'),
	url(r'^imgs/(?P<image_id>[0-9]+)/votedown/$', views.vote_down, name='vote_down'),
	url(r'^imgs/(?P<image_id>[0-9]+)/accounts/votes/$', views.user_vote, name='user_vote'),

	url(r'^imgs/(?P<image_id>[0-9]+)/viewcount/$', views.viewcount, name='viewcount'),
	url(r'^imgs/(?P<image_id>[0-9]+)/format/$', views.format, name='format'),

	url(r'^imgs/(?P<image_id>[0-9]+)/face_ids/$', views.face_ids, name='face_ids'),
	url(r'^imgs/(?P<image_id>[0-9]+)/comments/$', views.comments, name='comments'),

	url(r'^filtering/tags/', views.get_filter_tags, name='get_filter_tags'),
	url(r'^imgs/(?P<image_id>[0-9]+)/face/(?P<face_id>[A-Za-z0-9_]+)/landmark/$', views.landmark, name='landmark'),
	url(r'^imgs/(?P<image_id>[0-9]+)/face/(?P<face_id>[A-Za-z0-9_]+)/detection/$', views.detection, name='detection'),
]
	
