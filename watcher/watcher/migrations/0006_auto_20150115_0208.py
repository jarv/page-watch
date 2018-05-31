# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0005_watcherurl_last_capture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watcherurl',
            name='sponsor',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
