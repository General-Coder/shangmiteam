# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-07 09:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shangmi', '0007_auto_20181122_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='shangmiuser',
            name='icon',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
