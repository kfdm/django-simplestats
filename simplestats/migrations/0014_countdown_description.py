# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-05-04 08:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplestats', '0013_auto_20160321_0326'),
    ]

    operations = [
        migrations.AddField(
            model_name='countdown',
            name='description',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]