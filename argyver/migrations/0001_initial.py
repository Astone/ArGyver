# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=32)),
                ('remote_host', models.CharField(help_text='For example: 173.194.65.121', max_length=255)),
                ('remote_port', models.SmallIntegerField(default=22, help_text='Default is: 22')),
                ('remote_user', models.CharField(help_text='For example: angus', max_length=64)),
                ('remote_path', models.CharField(help_text='For example: Documents(which is equal to /home/angus/Documents)', max_length=255)),
                ('rsync_arguments', models.CharField(help_text='Only use this if you know what you are doing, it might break the ArGyver. Using -exclude and --include should be fine.', max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Remote Location',
                'verbose_name_plural': 'Remote Locations',
            },
            bases=(models.Model,),
        ),
    ]
