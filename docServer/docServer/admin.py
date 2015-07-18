from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf.urls import patterns

from docServer.models.project import *
from docServer.models.graph import *
from docServer.models.abstract import *
from django.contrib.sessions.models import Session


class ActionNodeForm(forms.ModelForm):
    OPERATION_TYPES = (
        ('Im', 'Import'),
        ('Ex', 'Export'),
        ('In', 'Internal'),
    )

    operation_type = forms.ChoiceField(choices=OPERATION_TYPES)


class ActionNodeAdmin(admin.ModelAdmin):
    model = ActionNode
    form = ActionNodeForm

class ControlNodeForm(forms.ModelForm):
    TYPES = (
        ('S', 'Start'),
        ('C', 'Choice'),
        ('F', 'Fork'),
        ('E', 'End'),
    )

    type = forms.ChoiceField(choices=TYPES)


class ControlNodeAdmin(admin.ModelAdmin):
    model = ControlNode
    form = ControlNodeForm


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    change_form_template = 'admin/project/change_form.html'
    change_list_template = 'admin/project/change_list.html'

    @staticmethod
    def export_graph(project, created_by_user):
        graph, created = Graph.objects.get_or_create(project=project)
        Area.objects.get_or_create(graph=graph, created_by=created_by_user, name="Pool")
        contributors = []
        [contributors.append(contributor) for contributor in project.team_members(supervisors=False).all()]
        [SwimLane.objects.get_or_create(graph=graph, created_by=created_by_user, user=contributor)
         for contributor in contributors]

    def get_urls(self):
        urls = super(ProjectAdmin, self).get_urls()
        my_urls = patterns(
            '',
            (r'^export_all_graphs/$', self.export_all_graphs)
        )
        return my_urls + urls

    def export_all_graphs(self, request):
        for project in Project.objects.all():
            ProjectAdmin.export_graph(project, request.user)
        return HttpResponseRedirect(reverse('admin:docServer_project_changelist'))
        # """Generates an xls file
        # """
        #
        # response = HttpResponse(mimetype='application/ms-excel')
        # response['Content-Disposition'] = \
        # 'attachment; filename=Report.xls'
        # # do something
        # return response

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if '_exportgraph' in request.POST:
            ProjectAdmin.export_graph(Project.objects.get(id=object_id), request.user)
            return HttpResponseRedirect(reverse('admin:docServer_project_changelist'))
        else:
            return super(ProjectAdmin, self).changeform_view(request, object_id, form_url, extra_context)


admin.site.register(Session)
admin.site.register(UserProfile)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Graph)
admin.site.register(ControlNode, ControlNodeAdmin)
admin.site.register(SwimLane)
admin.site.register(ObjectNode)
admin.site.register(ActionNode, ActionNodeAdmin)
admin.site.register(CommentNode)
admin.site.register(Edge)
admin.site.register(File)
admin.site.register(Area)
admin.site.register(Folder)
