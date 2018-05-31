# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0003_auto_20150112_2330'),
    ]

    operations = [
        migrations.AddField(
            model_name='watcherurl',
            name='last_change',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watcherurl',
            name='last_check',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
