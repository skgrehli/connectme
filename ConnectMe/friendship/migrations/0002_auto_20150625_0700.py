# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='from_user',
            field=models.ForeignKey(related_name='_unused_friend_relation', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='friend',
            name='to_user',
            field=models.ForeignKey(related_name='friends', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
