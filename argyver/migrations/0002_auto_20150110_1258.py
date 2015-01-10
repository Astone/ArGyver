# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='data',
            name='size',
            field=models.BigIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
