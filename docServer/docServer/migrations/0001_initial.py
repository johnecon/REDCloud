# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import docServer.models.project
import phonenumber_field.modelfields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('width', models.FloatField(default=300)),
                ('height', models.FloatField(default=800)),
                ('location_x', models.FloatField(default=0)),
                ('location_y', models.FloatField(default=0)),
                ('expanded', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('fromPort', models.CharField(default='B', max_length=32, blank=True)),
                ('toPort', models.CharField(default='T', max_length=32, blank=True)),
                ('points', models.TextField(blank=True)),
                ('type', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='edges_created')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('is_template', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('location_x', models.FloatField(default=0)),
                ('location_y', models.FloatField(default=0)),
                ('width', models.FloatField(default=0)),
                ('height', models.FloatField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ControlNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, to='docServer.Node', primary_key=True, parent_link=True, serialize=False)),
                ('type', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.node',),
        ),
        migrations.CreateModel(
            name='CommentNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, to='docServer.Node', primary_key=True, parent_link=True, serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.node',),
        ),
        migrations.CreateModel(
            name='ActionNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, to='docServer.Node', primary_key=True, parent_link=True, serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('tense', models.IntegerField(default=0)),
                ('date_realized', models.DateTimeField(null=True, blank=True)),
                ('operation_type', models.CharField(default='In', max_length=255)),
                ('realized_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='action_nodes_realized')),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.node',),
        ),
        migrations.CreateModel(
            name='ObjectNode',
            fields=[
                ('node_ptr', models.OneToOneField(auto_created=True, to='docServer.Node', primary_key=True, parent_link=True, serialize=False)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('is_exported', models.BooleanField(default=False)),
                ('tense', models.IntegerField(default=0)),
                ('date_realized', models.DateTimeField(null=True, blank=True)),
                ('realized_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='object_nodes_realized')),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.node',),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('contributors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='projects_contributed', blank=True)),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='projects_created')),
                ('leaders', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='projects_leaded', blank=True)),
                ('supervisors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='projects_supervised', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, to='docServer.Resource', primary_key=True, parent_link=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.resource',),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, to='docServer.Resource', primary_key=True, parent_link=True, serialize=False)),
                ('file', models.FileField(upload_to=docServer.models.project.resources_upload_path, null=True, blank=True)),
                ('format', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.resource',),
        ),
        migrations.CreateModel(
            name='SwimLane',
            fields=[
                ('area_ptr', models.OneToOneField(auto_created=True, to='docServer.Area', primary_key=True, parent_link=True, serialize=False)),
                ('color', models.CharField(default='#ffffff', max_length=255)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='swimlanes')),
            ],
            options={
                'abstract': False,
            },
            bases=('docServer.area',),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True)),
                ('skype', models.CharField(max_length=255, blank=True)),
                ('comment', models.TextField(blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resource',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='project',
            field=models.ForeignKey(to='docServer.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='real_type',
            field=models.ForeignKey(to='contenttypes.ContentType', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='objectnode',
            name='resource',
            field=models.ForeignKey(to='docServer.Resource', null=True, blank=True, related_name='object_nodes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='assigned_to',
            field=models.ForeignKey(to='docServer.Area', null=True, blank=True, related_name='nodes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='nodes_created'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='graph',
            field=models.ForeignKey(to='docServer.Graph', related_name='nodes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='node',
            name='real_type',
            field=models.ForeignKey(to='contenttypes.ContentType', editable=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='graph',
            name='project',
            field=models.ForeignKey(to='docServer.Project', related_name='graphs'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='folder',
            name='items',
            field=models.ManyToManyField(to='docServer.Resource', null=True, related_name='parent_folder', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='graph',
            field=models.ForeignKey(to='docServer.Graph', related_name='edges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='src',
            field=models.ForeignKey(to='docServer.Node', related_name='outgoing_edges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edge',
            name='tgt',
            field=models.ForeignKey(to='docServer.Node', related_name='incoming_edges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='created_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='areas_created'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='graph',
            field=models.ForeignKey(to='docServer.Graph', related_name='areas'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='area',
            name='real_type',
            field=models.ForeignKey(to='contenttypes.ContentType', editable=False),
            preserve_default=True,
        ),
    ]
