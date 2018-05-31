# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuspiciousUrls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=500)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WatcherUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'queued', max_length=32)),
                ('user', models.CharField(default=b'', max_length=255, blank=True)),
                ('interval', models.CharField(default=b'day', max_length=32)),
                ('url', models.CharField(unique=True, max_length=500)),
                ('last_error', models.TextField(default=b'', blank=True)),
                ('last_output', models.TextField(default=b'', blank=True)),
                ('error_count', models.IntegerField(default=0)),
                ('timeout_count', models.IntegerField(default=0)),
                ('save_output', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('checks', models.IntegerField(default=0)),
                ('changes', models.IntegerField(default=0)),
                ('capture_tool', models.CharField(default=b'wkhtmltoimage', max_length=32)),
                ('screen_grab', models.BooleanField(default=False)),
                ('checks_remaining', models.IntegerField(default=168)),
                ('unlimited', models.BooleanField(default=False)),
                ('sponsor', models.TextField(default=b'')),
            ],
            options={
                'ordering': ('created',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WatcherUrlBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'', max_length=32)),
                ('bucket_name', models.CharField(default=b'', max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('md5', models.CharField(default=b'', max_length=32)),
                ('error', models.TextField(default=b'')),
                ('changed', models.BooleanField(default=False)),
                ('output', models.TextField(default=b'')),
                ('cap_path', models.CharField(default=b'', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WatcherUrlHistoryDay',
            fields=[
                ('watcherurlbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='watcher.WatcherUrlBase')),
            ],
            options={
            },
            bases=('watcher.watcherurlbase',),
        ),
        migrations.CreateModel(
            name='WatcherUrlHistoryHour',
            fields=[
                ('watcherurlbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='watcher.WatcherUrlBase')),
            ],
            options={
            },
            bases=('watcher.watcherurlbase',),
        ),
        migrations.CreateModel(
            name='WatcherUrlHistoryWeek',
            fields=[
                ('watcherurlbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='watcher.WatcherUrlBase')),
            ],
            options={
            },
            bases=('watcher.watcherurlbase',),
        ),
        migrations.CreateModel(
            name='WatcherUrlNotifications',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='watcherurlbase',
            name='watcher_url',
            field=models.ForeignKey(to='watcher.WatcherUrl'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='watcherurl',
            name='notifications',
            field=models.ManyToManyField(to='watcher.WatcherUrlNotifications', blank=True),
            preserve_default=True,
        ),
    ]
