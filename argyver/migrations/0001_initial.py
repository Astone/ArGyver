# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(unique=True, max_length=32, db_index=True)),
                ('size', models.IntegerField()),
            ],
            options={
                'verbose_name': 'file in repository',
                'verbose_name_plural': 'file in repository',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField(unique=True, max_length=32)),
                ('remote_host', models.CharField(help_text='For example: 173.194.65.121', max_length=255)),
                ('remote_port', models.SmallIntegerField(default=22, help_text='Default is: 22')),
                ('remote_user', models.CharField(help_text='For example: angus', max_length=64)),
                ('remote_path', models.CharField(help_text='For example: Documents/ (which is equal to /home/angus/Documents/)', max_length=255)),
                ('rsync_arguments', models.CharField(help_text='Only use this if you know what you are doing, it might break the ArGyver. Using -exclude and --include should be fine.', max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'remote location',
                'verbose_name_plural': 'remote locations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('parent', models.ForeignKey(blank=True, to='argyver.Node', null=True)),
            ],
            options={
                'verbose_name': 'file system node',
                'verbose_name_plural': 'file system nodes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('created', models.DateTimeField(db_index=True)),
                ('deleted', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('data', models.ForeignKey(blank=True, to='argyver.Data', null=True)),
                ('node', models.ForeignKey(to='argyver.Node')),
            ],
            options={
                'verbose_name': 'version',
                'verbose_name_plural': 'versions',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='location',
            name='root_node',
            field=models.ForeignKey(editable=False, to='argyver.Node', unique=True),
            preserve_default=True,
        ),
    ]
