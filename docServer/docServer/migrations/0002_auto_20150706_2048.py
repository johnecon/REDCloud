# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docServer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionnode',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='objectnode',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
