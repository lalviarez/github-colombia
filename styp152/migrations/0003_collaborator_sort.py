# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-07 03:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('styp152', '0002_auto_20170407_0342'),
    ]

    operations = [
        migrations.AddField(
            model_name='collaborator',
            name='sort',
            field=models.IntegerField(default=0),
        ),
    ]
