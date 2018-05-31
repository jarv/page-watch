# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0007_watcherurl_last_capture_no_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='watcherurl',
            name='img',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watcherurl',
            name='url',
            field=models.CharField(max_length=500),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='watcherurl',
            unique_together=set([('url', 'img')]),
        ),
        migrations.RemoveField(
            model_name='watcherurl',
            name='last_capture_no_img',
        ),
    ]
