# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0002_auto_20150110_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watcherurl',
            name='checks_remaining',
            field=models.IntegerField(default=30),
            preserve_default=True,
        ),
    ]
