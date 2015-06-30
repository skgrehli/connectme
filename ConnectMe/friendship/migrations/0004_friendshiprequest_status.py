# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0003_auto_20150626_0505'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendshiprequest',
            name='status',
            field=models.CharField(default=b'P', max_length=1, choices=[(b'A', b'accepted'), (b'R', b'rejected'), (b'P', b'pending')]),
            preserve_default=True,
        ),
    ]
