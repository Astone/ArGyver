# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0003_iteration_archive'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteration',
            name='fix',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
