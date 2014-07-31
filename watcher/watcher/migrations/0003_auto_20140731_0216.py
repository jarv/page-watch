# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0002_auto_20140723_2154'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchergithub',
            name='branch',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watchergithub',
            name='file_path',
            field=models.CharField(default=b'', max_length=2048),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watchergithub',
            name='repo',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watchergithub',
            name='user',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='watchergithub',
            name='gh_path',
            field=models.CharField(default=b'', max_length=2048, db_index=True),
        ),
    ]
