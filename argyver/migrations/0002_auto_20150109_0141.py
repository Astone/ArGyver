# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Iteration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField()),
                ('finished', models.DateTimeField(null=True, blank=True)),
                ('errors', models.TextField()),
            ],
            options={
                'ordering': ['started'],
                'verbose_name': 'iteration',
                'verbose_name_plural': 'iterations',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='version',
            options={'ordering': ['created'], 'verbose_name': 'version', 'verbose_name_plural': 'versions'},
        ),
    ]
