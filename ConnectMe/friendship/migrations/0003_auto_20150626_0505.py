# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0002_auto_20150625_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='from_user',
            field=models.ForeignKey(related_name='_unused_friend_relation', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='friend',
            name='to_user',
            field=models.ForeignKey(related_name='friends', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
