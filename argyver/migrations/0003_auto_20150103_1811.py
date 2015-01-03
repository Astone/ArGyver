# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('argyver', '0002_auto_20150103_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='root_node',
            field=models.ForeignKey(default=1, editable=False, to='argyver.Node'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='version',
            name='created',
            field=models.DateTimeField(db_index=True),
            preserve_default=True,
        ),
    ]
