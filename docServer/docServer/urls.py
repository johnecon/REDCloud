from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken import views
from docServer import api_views
from django.contrib.auth.decorators import login_required
from docServer.views import ProjectList, ProjectDetail, resource_download, start, import_uploader
from docServer.api_views import project_update, node_delete, edge_delete, project_load, resource_export, csv_config, \
    public_resources, templates

router = routers.DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet)
router.register(r'projects/(?P<project_pk>\d+)/graphs', api_views.GraphViewSet, base_name='graphs')

urlpatterns = patterns('',
                        url(r'^$', 'docServer.views.index', name='home'),
                        url(r'^report_builder/', include('report_builder.urls')),
                        url(r'^api/', include(router.urls)),
                        url(r'^admin/', include(admin.site.urls)),
                        url(r'^account/', include('account.urls')),
                        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                        url(r'^api/token', views.obtain_auth_token),
                        url(r'^api/config', csv_config, name='merge_resources'),
                        url(r'^resources/$', login_required(public_resources), name='resources'),
                        url(r'^resources/(?P<pk>\d+)/download', login_required(resource_download),
                           name='resource_download'),
                        url(r'^projects/$', login_required(ProjectList.as_view()), name='project_list'),
                        url(r'^projects/(?P<pk>\d+)/$', login_required(ProjectDetail.as_view()), name='project_detail'),
                        url(r'^projects/(?P<pk>\d+)/update', project_update,
                           name='project_update'),
                        url(r'^projects/(?P<pk>\d+)/nodes/(?P<node_pk>\d+)/delete', node_delete,
                           name='project_nodes_delete'),
                        url(r'^projects/(?P<pk>\d+)/edges/(?P<src_pk>\d+)/(?P<tgt_pk>\d+)/delete', edge_delete,
                           name='project_edges_delete'),
                        url(r'^projects/(?P<pk>\d+)/load', project_load,
                           name='project_load'),
                        url(r'^projects/(?P<pk>\d+)/resources/export', resource_export,
                           name='export_resources'),
                        url(r'start$', start, name="start"),
                        url(r'^projects/(?P<pk>\d+)/upload', import_uploader, name="project_file_upload"),
                        url(r'session_security/', include('session_security.urls')),
                        url(r'^templates/$', login_required(templates), name='templates'),
                       )

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += patterns('django.views.static',
                            (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}),
                            )
