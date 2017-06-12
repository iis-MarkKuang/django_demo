# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-24 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstaGlassesPicsInfo',
            fields=[
                ('username', models.CharField(max_length=255)),
                ('pic_id', models.AutoField(primary_key=True, serialize=False)),
                ('pic_url', models.CharField(blank=True, max_length=255, null=True)),
                ('pic_type', models.IntegerField()),
                ('likes', models.IntegerField()),
                ('is_active', models.IntegerField(blank=True, null=True)),
                ('tags', models.TextField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('create_time', models.DateTimeField()),
                ('update_time', models.DateTimeField()),
                ('facepp_info', models.TextField(blank=True, null=True)),
                ('image_local_path', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'db_table': 'insta_glasses_pics_info',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='Image',
        ),
    ]