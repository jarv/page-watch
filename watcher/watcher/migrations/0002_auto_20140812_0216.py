# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WatcherGithub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gh_path', models.CharField(default=b'', max_length=2048, db_index=True)),
                ('user', models.CharField(default=b'', max_length=255)),
                ('repo', models.CharField(default=b'', max_length=255)),
                ('branch', models.CharField(default=b'', max_length=255)),
                ('file_path', models.CharField(default=b'', max_length=2048)),
                ('location', models.URLField()),
                ('status', models.CharField(default=b'initialized', max_length=32, choices=[(b'initialized', b'initialized'), (b'processing', b'processing'), (b'processed', b'processed'), (b'errored', b'errored')])),
                ('last_error', models.TextField(default=b'')),
                ('error_count', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('ratelimit_remaining', models.IntegerField(default=0)),
                ('ratelimit', models.IntegerField(default=0)),
            ],
            options={
                'ordering': (b'created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WatcherGithubHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latest_sha', models.CharField(default=None, max_length=255)),
                ('diff', models.URLField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('commits', models.TextField(default=b'')),
                ('watchergithub', models.ForeignKey(to='watcher.WatcherGithub')),
            ],
            options={
                'ordering': (b'created',),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='watchergithubhistory',
            unique_together=set([(b'watchergithub', b'latest_sha')]),
        ),
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
            field=models.ManyToManyField(to='watcher.WatcherGithubNotifications'),
            preserve_default=True,
        ),
    ]
