import json
from io import TextIOWrapper
import csv

from rest_framework import viewsets
from rest_framework import authentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django.db import transaction
from docServer.admin import ProjectAdmin
from docServer.serializers import *
from docServer.models.graph import *
from docServer.models.project import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

@api_view(['POST'])
@authentication_classes((authentication.BasicAuthentication, authentication.TokenAuthentication))
@transaction.atomic
def csv_config(request):
    headers = None
    content = {}
    f = TextIOWrapper(request.FILES['config'].file, encoding='utf-8')
    reader = csv.reader(f.read().splitlines())
    # credits goes to http://www.eurion.net/python-snippets/snippet/CSV%20to%20Dictionary.html
    for row in reader:
        if reader.line_num == 1:
            headers = row[1:]
        else:
            content[row[0]] = dict(zip(headers, row[1:]))
    special_users = []
    projects = set()
    for username in content:
        user, created = User.objects.get_or_create(username=username)
        user.email = content[username]['Email']
        user.first_name = content[username]['First Name']
        user.last_name = content[username]['Last Name']
        user.profile.phone = content[username]['Phone']
        user.profile.skype = content[username]['Skype']
        user.profile.comment = content[username]['Comment']
        user.save()
        project = content[username]['Project']
        sub_project = content[username]['SubProject']
        if project != "*" and sub_project != "*":
            project, created = Project.objects.get_or_create(name=project + "-" + sub_project)
            project.created_by = request.user
            project.add_user(user, content[username]["Role"])
            project.save()
            projects.add(project)
        else:
            special_users.append(
                {"user": user, "role": content[username]["Role"], "project": project, "subproject": sub_project})
    for special_user in special_users:
        for project in projects:
            if (special_user['project'] == "*" and special_user['subproject'] == "*") \
                    or (special_user['project'] == "*" and project.name.endswith(special_user['subproject'])) \
                    or (special_user['subproject'] == "*" and project.name.startswith(special_user['project'])):
                project.add_user(special_user['user'], special_user['role'])
    for project in projects:
        ProjectAdmin.export_graph(project, request.user)
    return Response({"success": True})


def filter_by_pk(gen, pk, class_name):
    for entry in gen:
        if (entry.pk == pk) and (entry.cast().__class__.__name__ == class_name):
            yield entry
        continue


@api_view(['POST'])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
@transaction.atomic
def project_update(request, pk):
    cache.delete('project_{pk}'.format(pk=pk))
    project = Project.objects.get(pk=pk)
    graph = project.graphs.first()
    gojs_manager = GojsManager(json.loads(request.data))

    gojs_elements_to_delete = gojs_manager.get_list_of_elements_to_delete()
    for element in gojs_elements_to_delete:
        try:
            db_element = eval(element['class']).objects.get(pk=element['pk'])
            if db_element.is_deletable():
                db_element.delete()
        except ObjectDoesNotExist:
            pass

    for gojsElement in gojs_manager.get_list_of_elements_not_to_delete():
        # if gojsElement.category_class is "Edge" or gojsElement.is_modified:
        if gojsElement.pk is not None:
            if gojsElement.category_class is "SyncEdge":
                graph_element = next(
                    filter_by_pk(graph.graph_elements, gojsElement.pk, 'Edge')).cast()
            else:
                graph_element = next(
                    filter_by_pk(graph.graph_elements, gojsElement.pk, gojsElement.category_class)).cast()
            if gojsElement.category_class is "ObjectNode":
                resource = gojs_manager.get_resource_for(gojsElement)
                if resource is not None:
                    graph_element.resource = resource
        else:
            if gojsElement.category_class is "ObjectNode":
                resource = gojs_manager.get_resource_for(gojsElement)
                graph_element = eval(gojsElement.category_class). \
                    objects.create(graph=graph, created_by=request.user, resource=resource)
            elif gojsElement.category_class is "Edge":
                graph_element = eval(gojsElement.category_class). \
                    objects.create(graph=graph, created_by=request.user, src=gojsElement.src, tgt=gojsElement.tgt,
                                   type=EdgeType.NORMAL)
            elif gojsElement.category_class is "SyncEdge":
                graph_element = Edge. \
                    objects.create(graph=graph, created_by=request.user, src=gojsElement.src, tgt=gojsElement.tgt,
                                   type=EdgeType.SYNC)
            else:
                graph_element = eval(gojsElement.category_class).objects.create(graph=graph, created_by=request.user)
            gojsElement.pk = graph_element.pk
        [setattr(graph_element, editable_attr, getattr(gojsElement, editable_attr, '')) for editable_attr in
         graph_element.editable_attrs()]
        graph_element.save()
    return Response({"message": "Project " + project.name + " successfully updated"})


@api_view(['GET', ])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
def project_load(request, pk):
    json = cache.get('project_{pk}'.format(pk=pk))
    if not json:
        project = Project.objects.get(pk=pk)
        serializer = ProjectSerializer(project)
        json = serializer.data
    cache.set('project_{pk}'.format(pk=pk), json, 60)
    return Response({"data": json})


@api_view(['GET', ])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
def public_resources(request):
    serializer = ObjectResourceSerializer(ObjectNode.objects.filter(is_exported=1), many=True)
    return Response({"data": serializer.data})

@api_view(['GET', ])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
def templates(request):
    serializer = GraphSerializer(Graph.objects.filter(is_template=1), many=True)
    return Response({"data": serializer.data})


@api_view(['POST', ])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
def resource_export(request, pk):
    if len(request.data['pks']) > 1:
        folder = Folder.objects.create(name=request.data['name'], project=Project.objects.get(pk=pk),
                                       created_by=request.user)
        [folder.items.add(Resource.objects.get(pk=resource_pk).clone(folder)) for resource_pk in request.data['pks'] if resource_pk is not None and resource_pk is not '' ]
        if folder.items.count() > 0:
            return Response({"error": False, "resourcePk": folder.pk, "resourceName": "folder: " + request.data['name']})
        else:
            return Response({"error": False, "resourcePk": None, "resourceName": None})
    elif len(request.data['pks']) == 1 and request.data['pks'][0] is not None and request.data['pks'][0] is not '':
        Resource.objects.get(pk=request.data['pks'][0]).clone()
        return Response(
            {"error": False, "resourcePk": request.data['pks'][0], "resourceName": "folder: " + request.data['name']})
    else:
        return Response({"error": False, "resourcePk": None, "resourceName": None})


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class GraphViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows graphs to be viewed.
    """
    serializer_class = GraphSerializer

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs['project_pk'])

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        project_pk = self.kwargs['project_pk']
        return Graph.objects.filter(project=project_pk)


class GojsNode:
    def __init__(self, manager, data):
        self.loc = None
        self.public = None
        self.category = ''
        self.pk = None
        self.group = None
        self.name = ''
        self.description = ''
        self.tense = Tense.FUTURE
        self.manager = manager
        self.realized_by = None
        self._realized_by = None
        self.date_realized = None
        self.type = None
        self.delete = False
        self.width = 0
        self.height = 0
        self.is_modified = False
        self.operation_type = None
        self._type = None
        for attr in data:
            setattr(self, attr, data[attr])

    @property
    def type(self):
        if self._type is None:
            return {
                'Start': 'S',
                'Choice': 'C',
                'Fork': 'F',
                'End': 'E',
            }[self.category]
        else:
            return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def realized_by(self):
        return self._realized_by

    @realized_by.setter
    def realized_by(self, value):
        self._realized_by = User.objects.get(username=value) if value is not None else None

    @property
    def location_x(self):
        return self.loc.split()[0]

    @property
    def location_y(self):
        return self.loc.split()[1]

    @property
    def assigned_to(self):
        return SwimLane.objects.get(pk=[node.pk for node in self.manager.nodes
                                        if node.key == self.group and node.category == "SwimLane"][0])

    @property
    def category_class(self):
        return {
            'Start': 'ControlNode',
            'End': 'ControlNode',
            'Fork': 'ControlNode',
            'Choice': 'ControlNode',
            'Action-In': 'ActionNode',
            'Action-Im': 'ActionNode',
            'Action-Ex': 'ActionNode',
            'Comment': 'CommentNode',
            'Object': 'ObjectNode',
            'SwimLane': 'SwimLane',
            'Pool': 'Area',
        }[self.category]

    @property
    def is_exported(self):
        return self.public == "YES"


class GojsEdge:
    def __init__(self, manager, data):
        self.pk = None
        self.to = None
        self.manager = manager
        self.category = ''
        self.delete = False
        self.is_modified = False
        for attr in data:
            setattr(self, attr, data[attr])

    @property
    def category_class(self):
        return 'SyncEdge' if self.category == 'Sync' else 'Edge'

    @property
    def tgt(self):
        return Node.objects.get(pk=[node.pk for node in self.manager.nodes
                                    if node.key == self.to][0])

    @property
    def src(self):
        return Node.objects.get(pk=[node.pk for node in self.manager.nodes
                                    if node.key == getattr(self, 'from')][0])


class GojsManager:
    def __init__(self, data):
        self.nodes = []
        self.edges = []
        self.elements = []
        for node in data['nodeDataArray']:
            self.nodes.append(GojsNode(self, node))
        for edge in data['linkDataArray']:
            self.edges.append(GojsEdge(self, edge))
        self.elements = self.nodes + self.edges

    def get_list_of_elements_to_delete(self):
        return [{"pk": element.pk, "class": Node.real_category(element.category)} for element in self.elements if
                element.delete]

    def get_list_of_elements_not_to_delete(self):
        return [element for element in self.elements if not element.delete]

    @staticmethod
    def get_resource_for(gojs_node):
        return Resource.objects.get(pk=gojs_node.resourcePk) if getattr(gojs_node, "resourcePk",
                                                                        None) != '' and getattr(
            gojs_node, "resourcePk", None) is not None else None


@api_view(['POST'])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
@transaction.atomic
def node_delete(request, pk, node_pk):
    node = Node.objects.get(pk=node_pk)
    if node is not None:
        node.delete()
    return Response({"message": "Node successfully deleted"})


@api_view(['POST'])
@authentication_classes(
    (authentication.SessionAuthentication, authentication.BasicAuthentication, authentication.TokenAuthentication))
@transaction.atomic
def edge_delete(request, pk, src_pk, tgt_pk):
    edge = Edge.objects.get(src=src_pk, tgt=tgt_pk)
    if edge is not None:
        edge.delete()
    return Response({"message": "Edge successfully deleted"})
