# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-11 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shangmi', '0014_store_boss_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='getmoneylog',
            name='partner_trade_no',
            field=models.CharField(max_length=255, null=True, verbose_name='下单号'),
        ),
    ]
