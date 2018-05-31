# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0006_auto_20150115_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='watcherurl',
            name='last_capture_no_img',
            field=models.URLField(blank=True),
            preserve_default=True,
        ),
    ]
