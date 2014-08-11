# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0003_auto_20140731_0216'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatcherGithubNotifications',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='watchergithub',
            name='notifications',
            field=models.ManyToManyField(to=b'watcher.WatcherGithubNotifications'),
            preserve_default=True,
        ),
    ]
