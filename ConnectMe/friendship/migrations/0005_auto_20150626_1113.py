# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0004_friendshiprequest_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendshiprequest',
            name='to_user',
            field=models.ForeignKey(related_name='friendship_requests_received', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
