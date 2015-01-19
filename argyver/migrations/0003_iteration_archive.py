# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0002_auto_20150110_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteration',
            name='archive',
            field=models.ForeignKey(blank=True, to='argyver.Archive', null=True),
            preserve_default=True,
        ),
    ]
