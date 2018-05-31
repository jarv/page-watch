# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0004_auto_20150113_0503'),
    ]

    operations = [
        migrations.AddField(
            model_name='watcherurl',
            name='last_capture',
            field=models.URLField(blank=True),
            preserve_default=True,
        ),
    ]
