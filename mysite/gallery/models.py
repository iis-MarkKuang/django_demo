from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from mongoengine import *
from django.contrib.auth.models import User
# Create your models here.

# MySQL generated auth models
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class GalleryImage(models.Model):
    username = models.CharField(max_length=200)
    pic_url = models.CharField(max_length=255)
    pic_type = models.IntegerField()
    likes = models.IntegerField()
    tags = models.TextField()
    comments = models.TextField()
    create_time = models.DateTimeField()
    facepp_info = models.TextField()
    image_local_path = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'gallery_image'


class InstaGlassesPicsInfo(models.Model):
    insta_pic_info_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    pic_url = models.CharField(max_length=255, blank=True, null=True)
    pic_type = models.IntegerField()
    likes = models.IntegerField()
    is_active = models.IntegerField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField()
    facepp_info = models.TextField(blank=True, null=True)
    image_local_path = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'insta_glasses_pics_info'



# added mysql model to add phone to user profile
class UserProfile(models.Model):
    user = models.OneToOneField(User,unique=True)
    phone = models.CharField(unique=True, max_length=11)

connect('test')

class DetectResult(EmbeddedDocument):
	position_eye_left_y = FloatField()
	position_eye_left_x = FloatField()
	position_nose_y = FloatField()
	position_nose_x = FloatField()
	attribute_glass_value = StringField()
	tag = StringField()
	attribute_pose_yaw_angle_value = FloatField()
	position_eye_right_y = FloatField()
	position_eye_right_x = FloatField()
	attribute_gender_value = StringField()
	attribute_age_range = IntField()
	attribute_race_confidence = FloatField()
	attribute_gender_confidence = FloatField()
	position_height = FloatField()
	position_mouth_right_y = FloatField()
	position_mouth_right_x = FloatField()
	attribute_smiling_value = FloatField()
	attribute_pose_pitch_angle_value = FloatField()
	attribute_glass_confidence = FloatField()
	attribute_pose_roll_angle_value = FloatField()
	attribute_age_value = IntField()
	attribute_race_value = StringField()
	position_center_y = FloatField()
	position_center_x = FloatField()
	position_mouth_left_y = FloatField()
	position_mouth_left_x = FloatField()
	face_id = StringField()
	position_width = FloatField()
	meta = {'strict': False}

class LandmarkResult(EmbeddedDocument):
	landmark_mouth_lower_lip_left_contour1_y = FloatField()
	landmark_mouth_lower_lip_left_contour1_x = FloatField()
	landmark_contour_left4_x = FloatField()
	landmark_contour_left4_y = FloatField()
	landmark_left_eye_bottom_y = FloatField()
	landmark_left_eye_bottom_x = FloatField()
	landmark_nose_contour_right1_x = FloatField()
	landmark_nose_contour_right1_y = FloatField()
	landmark_nose_contour_left3_x = FloatField()
	landmark_nose_contour_left3_y = FloatField()
	landmark_right_eye_left_corner_x = FloatField()
	landmark_contour_right9_y = FloatField()
	landmark_left_eyebrow_lower_middle_y = FloatField()
	landmark_left_eyebrow_lower_middle_x = FloatField()
	landmark_mouth_lower_lip_top_y = FloatField()
	landmark_mouth_lower_lip_top_x = FloatField()
	landmark_contour_left6_x = FloatField()
	landmark_contour_left6_y = FloatField()
	landmark_left_eye_lower_left_quarter_x = FloatField()
	landmark_left_eye_lower_left_quarter_y = FloatField()
	landmark_right_eyebrow_lower_right_quarter_x = FloatField()
	landmark_right_eyebrow_lower_right_quarter_y = FloatField()
	landmark_mouth_lower_lip_bottom_x = FloatField()
	landmark_mouth_lower_lip_bottom_y = FloatField()
	landmark_contour_left2_x = FloatField()
	landmark_contour_left2_y = FloatField()
	landmark_mouth_lower_lip_right_contour2_x = FloatField()
	landmark_mouth_lower_lip_right_contour2_y = FloatField()
	landmark_left_eyebrow_upper_left_quarter_y = FloatField()
	landmark_left_eyebrow_upper_left_quarter_x = FloatField()
	landmark_contour_right1_y = FloatField()
	landmark_contour_right1_x = FloatField()
	landmark_mouth_left_corner_y = FloatField()
	landmark_mouth_left_corner_x = FloatField()
	landmark_right_eye_pupil_y = FloatField()
	landmark_contour_right6_x = FloatField()
	landmark_contour_right6_y = FloatField()
	landmark_right_eye_pupil_x = FloatField()
	landmark_contour_right5_y = FloatField()
	landmark_contour_right5_x = FloatField()
	landmark_left_eyebrow_lower_right_quarter_x = FloatField()
	landmark_left_eyebrow_lower_right_quarter_y = FloatField()
	landmark_mouth_right_corner_x = FloatField()
	landmark_left_eye_lower_right_quarter_x = FloatField()
	landmark_left_eye_lower_right_quarter_y = FloatField()
	landmark_contour_right3_y = FloatField()
	landmark_contour_right3_x = FloatField()
	landmark_mouth_upper_lip_left_contour2_y = FloatField()
	landmark_mouth_upper_lip_left_contour2_x = FloatField()
	face_id = StringField()
	landmark_left_eye_upper_left_quarter_y = FloatField()
	landmark_left_eye_upper_left_quarter_x = FloatField()
	landmark_contour_left3_y = FloatField()
	landmark_contour_left3_x = FloatField()
	landmark_mouth_lower_lip_left_contour3_y = FloatField()
	landmark_contour_chin_x = FloatField()
	landmark_contour_chin_y = FloatField()
	landmark_mouth_lower_lip_left_contour3_x = FloatField()
	landmark_left_eye_right_corner_x = FloatField()
	landmark_left_eyebrow_upper_right_quarter_y = FloatField()
	landmark_left_eyebrow_upper_right_quarter_x = FloatField()
	landmark_contour_left5_y = FloatField()
	landmark_contour_left5_x = FloatField()
	landmark_right_eye_upper_left_quarter_y = FloatField()
	landmark_mouth_upper_lip_left_contour1_x = FloatField()
	landmark_mouth_upper_lip_left_contour1_y = FloatField()
	landmark_right_eyebrow_upper_right_quarter_y = FloatField()
	landmark_right_eyebrow_upper_right_quarter_x = FloatField()
	landmark_right_eye_upper_left_quarter_x = FloatField()
	landmark_contour_left1_y = FloatField()
	landmark_contour_left1_x = FloatField()
	landmark_left_eyebrow_lower_left_quarter_x = FloatField()
	landmark_left_eyebrow_lower_left_quarter_y = FloatField()
	landmark_left_eye_center_y = FloatField()
	landmark_right_eye_center_y = FloatField()
	landmark_right_eye_center_x = FloatField()
	landmark_nose_contour_right2_y = FloatField()
	landmark_right_eye_right_corner_x = FloatField()
	landmark_right_eye_right_corner_y = FloatField()
	landmark_right_eye_top_x = FloatField()
	landmark_right_eye_top_y = FloatField()
	landmark_contour_right7_y = FloatField()
	landmark_contour_right7_x = FloatField()
	landmark_left_eyebrow_right_corner_x = FloatField()
	landmark_left_eyebrow_right_corner_y = FloatField()
	landmark_nose_contour_right2_x = FloatField()
	landmark_right_eyebrow_left_corner_x = FloatField()
	landmark_right_eyebrow_left_corner_y = FloatField()
	landmark_left_eye_center_x = FloatField()
	landmark_left_eyebrow_left_corner_x = FloatField()
	landmark_left_eyebrow_left_corner_y = FloatField()
	landmark_left_eye_right_corner_y = FloatField()
	landmark_right_eyebrow_upper_middle_x = FloatField()
	landmark_right_eyebrow_upper_middle_y = FloatField()
	landmark_left_eye_pupil_y = FloatField()
	landmark_left_eye_pupil_x = FloatField()
	landmark_right_eye_upper_right_quarter_y = FloatField()
	landmark_right_eye_upper_right_quarter_x = FloatField()
	landmark_mouth_upper_lip_top_x = FloatField()
	landmark_mouth_upper_lip_top_y = FloatField()
	landmark_mouth_upper_lip_bottom_y = FloatField()
	landmark_mouth_upper_lip_bottom_x = FloatField()
	landmark_nose_contour_lower_middle_x = FloatField()
	landmark_nose_contour_lower_middle_y = FloatField()
	landmark_nose_tip_x = FloatField()
	landmark_right_eyebrow_lower_middle_y = FloatField()
	landmark_right_eyebrow_lower_middle_x = FloatField()
	landmark_nose_tip_y = FloatField()
	landmark_mouth_upper_lip_right_contour1_x = FloatField()
	landmark_mouth_upper_lip_right_contour1_y = FloatField()
	landmark_nose_left_y = FloatField()
	landmark_nose_left_x = FloatField()
	landmark_right_eyebrow_lower_left_quarter_x = FloatField()
	landmark_right_eyebrow_lower_left_quarter_y = FloatField()
	landmark_right_eye_bottom_y = FloatField()
	landmark_right_eye_bottom_x = FloatField()
	landmark_mouth_upper_lip_right_contour3_x = FloatField()
	landmark_mouth_upper_lip_right_contour3_y = FloatField()
	landmark_nose_right_y = FloatField()
	landmark_nose_right_x = FloatField()
	landmark_mouth_lower_lip_left_contour2_y = FloatField()
	landmark_left_eye_top_x = FloatField()
	landmark_left_eye_top_y = FloatField()
	landmark_contour_left7_y = FloatField()
	landmark_contour_left7_x = FloatField()
	landmark_mouth_right_corner_y = FloatField()
	landmark_contour_left9_y = FloatField()
	landmark_contour_left9_x = FloatField()
	landmark_nose_contour_left2_y = FloatField()
	landmark_nose_contour_left2_x = FloatField()
	landmark_right_eye_left_corner_y = FloatField()
	landmark_mouth_upper_lip_right_contour2_y = FloatField()
	landmark_mouth_upper_lip_right_contour2_x = FloatField()
	landmark_nose_contour_right3_x = FloatField()
	landmark_left_eyebrow_upper_middle_x = FloatField()
	landmark_left_eyebrow_upper_middle_y = FloatField()
	landmark_contour_right8_x = FloatField()
	landmark_nose_contour_right3_y = FloatField()
	landmark_contour_right8_y = FloatField()
	landmark_mouth_lower_lip_right_contour1_y = FloatField()
	landmark_mouth_lower_lip_right_contour1_x = FloatField()
	landmark_nose_contour_left1_x = FloatField()
	landmark_nose_contour_left1_y = FloatField()
	landmark_mouth_lower_lip_right_contour3_y = FloatField()
	landmark_mouth_lower_lip_right_contour3_x = FloatField()
	landmark_right_eyebrow_right_corner_x = FloatField()
	landmark_right_eyebrow_right_corner_y = FloatField()
	landmark_contour_left8_x = FloatField()
	landmark_right_eye_lower_left_quarter_x = FloatField()
	landmark_right_eye_lower_left_quarter_y = FloatField()
	landmark_left_eye_upper_right_quarter_y = FloatField()
	landmark_left_eye_upper_right_quarter_x = FloatField()
	landmark_right_eyebrow_upper_left_quarter_y = FloatField()
	landmark_right_eyebrow_upper_left_quarter_x = FloatField()
	landmark_right_eye_lower_right_quarter_x = FloatField()
	landmark_right_eye_lower_right_quarter_y = FloatField()
	landmark_left_eye_left_corner_x = FloatField()
	landmark_left_eye_left_corner_y = FloatField()
	landmark_contour_left8_y = FloatField()
	landmark_contour_right4_x = FloatField()
	landmark_contour_right4_y = FloatField()
	landmark_mouth_lower_lip_left_contour2_x = FloatField()
	landmark_contour_right9_x = FloatField()
	landmark_mouth_upper_lip_left_contour3_x = FloatField()
	landmark_mouth_upper_lip_left_contour3_y = FloatField()
	landmark_contour_right2_x = FloatField()
	landmark_contour_right2_y = FloatField()
	meta = {'strict': False}

class User(EmbeddedDocument):
	username = StringField()
	profile_pic_url = StringField()
	liked_image_ids = ListField(IntField())
	id = StringField()
	meta = {'strict': False}

class Comment(EmbeddedDocument):
	text = StringField()
	created_at = FloatField()
	id = StringField()
	user = EmbeddedDocumentField(User)
	meta = {'strict': False}

class FaceInfo(EmbeddedDocument):
	face_id = StringField()
	#landmark_result = EmbeddedDocumentField(LandmarkResult)
	landmark_result_25p = StringField()
	detect_result = EmbeddedDocumentField(DetectResult)
	meta = {'strict': False}

class Image(Document):
	_id = IntField()
	comments = ListField(EmbeddedDocumentField(Comment))
	size_result = StringField()
	size_result_tuple = ListField(IntField())
	face_info = ListField(EmbeddedDocumentField(FaceInfo))
	bytesize_result = IntField()
	tags = ListField(StringField())
	instagram_likes = IntField()
	likes = IntField()
	dislikes = IntField()
	pic_url = StringField()
	pic_type = IntField()
	create_time = IntField()
	update_time = IntField()
	user_posted_time = IntField()
	enlarge_times = IntField()
	smiling_info = ListField(StringField())
	glass_info = ListField(StringField())
	face_ids = ListField(StringField())
	race_info = ListField(StringField())
	gender_info = ListField(StringField())
	age_info = ListField(StringField())
	image_local_path = StringField()
	quality = IntField()
	repeated = IntField()
	is_25p = IntField()
	active = IntField()
	meta = {
		'ordering': ['-user_posted_time'],
		'strict': False,
		'indexes': [
			{
				'fields': ['-user_posted_time'],
			},
			{
				'fields': ['-instagram_likes'],
			},
			{
				'fields': ['-enlarge_times'],
			}
		],
	}

class UserVote(Document):
	username = StringField()
	image_id = IntField()
	vote = IntField()
	date = StringField()

class ImageView(Document):
	image_id = IntField()
	date = StringField()
	times = IntField()