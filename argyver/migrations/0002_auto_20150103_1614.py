# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(unique=True, max_length=32, db_index=True)),
                ('timestamp', models.DateTimeField()),
                ('size', models.IntegerField()),
            ],
            options={
                'verbose_name': 'file in repository',
                'verbose_name_plural': 'file in repository',
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
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
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
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['name'], 'verbose_name': 'remote location', 'verbose_name_plural': 'remote locations'},
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='remote_path',
            field=models.CharField(help_text='For example: Documents/ (which is equal to /home/angus/Documents/)', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='slug',
            field=models.SlugField(unique=True, max_length=32),
            preserve_default=True,
        ),
    ]
