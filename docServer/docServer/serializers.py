from rest_framework import serializers

from docServer.models.graph import *

from django.contrib.sessions.models import Session
from django.utils import timezone

def get_color(color):
    return {
        'grey_yellow': '#4f4b29',
        'grey_blue': '#2e3e42',
    }[color]

def get_all_logged_in_users():
    # Query all non-expired sessions
    # use timezone.now() instead of datetime.now() in latest versions of Django
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    # Build a list of user ids from that query
    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))

    # Query all logged in users based on id list
    return User.objects.filter(id__in=uid_list)

class GraphElementSerializer(serializers.HyperlinkedModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_category(self, obj):
        if (obj.__class__.__name__ is not 'Edge'):
            return obj.__class__.__name__
        else:
            return obj.category_class()


class NodeSerializer(GraphElementSerializer):
    assigned_to = serializers.StringRelatedField(read_only=True)
    category = serializers.ReadOnlyField(source='gojs_category')
    group = serializers.StringRelatedField(read_only=True, source='assigned_to')
    key = serializers.ReadOnlyField(source='pk')
    createdBy = serializers.SlugRelatedField(source='created_by', slug_field='username', read_only=True)
    date = serializers.SerializerMethodField('get_date_created')

    def get_date_created(self, obj):
        # times 1000 for javascript.
        return obj.date_created.strftime("%Y-%m-%d %H:%M")

    def get_fromLinkable(self, obj):
        return {
            0: True,
            1: True,
            2: False,
        }[obj.tense]

    def get_editable(self, obj):
        return {
            0: True,
            1: True,
            2: False,
        }[obj.tense]

    def get_toLinkable(self, obj):
        return {
            0: True,
            1: False,
            2: False,
        }[obj.tense]

    class Meta:
        abstract = True


class AreaSerializer(GraphElementSerializer):
    isGroup = serializers.ReadOnlyField(source='is_group')
    category = serializers.ReadOnlyField(source='name')
    key = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Area
        fields = ('key', 'category', 'pk', 'isGroup', 'width', 'height', 'loc', 'expanded')


class SwimLaneSerializer(GraphElementSerializer):
    isGroup = serializers.ReadOnlyField(source='is_group')
    key = serializers.ReadOnlyField(source='name')
    name = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = SwimLane
        fields = ('key', 'category', 'pk', 'name', 'color', 'isGroup', 'group', 'width', 'height', 'loc', 'expanded')

    def get_name(self, obj):
        return obj.user.first_name + " (" + obj.graph.project.get_roles_of(obj.user) + ") "  + ('*' if obj.user in get_all_logged_in_users() else '')

    def get_group(self, obj):
        return Area.objects.filter(graph=obj.graph,name='Pool')[0].pk

class ObjectNodeSerializer(NodeSerializer):
    resourcePk = serializers.PrimaryKeyRelatedField(read_only=True, source='resource')
    resourceName = serializers.SlugRelatedField(read_only=True, source='resource', slug_field='name')
    public = serializers.SerializerMethodField()
    strokeDashArray = serializers.SerializerMethodField()
    fill = serializers.SerializerMethodField()
    realized_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    date_realized = serializers.SerializerMethodField()
    fromLinkable = serializers.SerializerMethodField()
    toLinkable = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()

    class Meta:
        model = ObjectNode
        fields = ('category', 'key', 'pk', 'name','description', 'loc', 'group', 'createdBy', 'realized_by',
                  'date_realized', 'public', 'date', 'resourcePk', 'resourceName', 'tense', 'strokeDashArray', 'fill',
                  'width', 'height', 'fromLinkable', 'toLinkable', 'textColor', 'editable')

    def get_textColor(self, obj):
        return 'white' if obj.tense == Tense.PAST else 'black'

    def get_date_realized(self, obj):
        return obj.date_realized.strftime("%Y-%m-%d") if obj.date_realized is not None else None

    def get_public(self, obj):
        return "YES" if obj.is_exported else "NO"

    def get_strokeDashArray(self, obj):
        return [5,10] if obj.tense == Tense.FUTURE else None

    def get_fill(self, obj):
        return {
            0: 'white',
            1: 'lightblue',
            2: get_color('grey_blue'),
        }[obj.tense]


class ActionNodeSerializer(NodeSerializer):
    strokeDashArray = serializers.SerializerMethodField()
    fill = serializers.SerializerMethodField()
    realized_by = serializers.SlugRelatedField(slug_field='username', read_only=True)
    date_realized = serializers.SerializerMethodField()
    fromLinkable = serializers.SerializerMethodField()
    toLinkable = serializers.SerializerMethodField()
    textColor = serializers.SerializerMethodField()
    editable = serializers.SerializerMethodField()

    class Meta:
        model = ActionNode
        fields = ('category', 'key', 'pk', 'name', 'description', 'loc', 'group', 'createdBy', 'realized_by',
                  'date_realized', 'date', 'tense', 'fill', 'strokeDashArray', 'operation_type', 'width', 'height',
                  'fromLinkable', 'toLinkable', 'textColor', 'editable')

    def get_strokeDashArray(self, obj):
        return [5,10] if obj.tense == Tense.FUTURE else None

    def get_date_realized(self, obj):
        return obj.date_realized.strftime("%Y-%m-%d") if obj.date_realized is not None else None

    def get_fill(self, obj):
        return {
            0: 'white',
            1: 'lightyellow',
            2: get_color('grey_yellow'),
        }[obj.tense]

    def get_textColor(self, obj):
        return 'white' if obj.tense == Tense.PAST else 'black'

class CommentNodeSerializer(NodeSerializer):
    class Meta:
        model = CommentNode
        fields = ('category', 'key', 'pk', 'name', 'loc', 'group', 'createdBy', 'date' , 'width', 'height')


class ControlNodeSerializer(NodeSerializer):
    class Meta:
        model = ControlNode
        fields = ('category', 'key', 'pk', 'loc', 'group', 'type', 'createdBy', 'date')

        def get_category(self, obj):
            return obj.category


class EdgeSerializer(GraphElementSerializer):
    src = serializers.PrimaryKeyRelatedField(read_only=True)
    tgt = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Edge
        fields = ('category', 'pk', 'src', 'tgt', 'points', 'fromPort', 'toPort')




class GraphElementRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `graph_element` generic relationship.
    """

    def to_representation(self, graph_element):
        """
        Serialize graph elements to a simple textual representation.
        """
        graph_element = graph_element.cast()
        serializer = None
        if isinstance(graph_element, SwimLane):
            serializer = SwimLaneSerializer(graph_element)
        elif isinstance(graph_element, ObjectNode):
            serializer = ObjectNodeSerializer(graph_element)
        elif isinstance(graph_element, ActionNode):
            serializer = ActionNodeSerializer(graph_element)
        elif isinstance(graph_element, ControlNode):
            serializer = ControlNodeSerializer(graph_element)
        elif isinstance(graph_element, CommentNode):
            serializer = CommentNodeSerializer(graph_element)
        elif isinstance(graph_element, Edge):
            serializer = EdgeSerializer(graph_element)
        elif isinstance(graph_element, Area):
            serializer = AreaSerializer(graph_element)
        if (serializer is None):
            raise Exception('Unexpected type of graph element')
        else:
            return serializer.data


class UserSerializer(serializers.ModelSerializer):
    is_logged_in = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'is_logged_in',)

    def get_is_logged_in(self, object):
        return object in get_all_logged_in_users()


class GraphSerializer(serializers.HyperlinkedModelSerializer):
    graph_elements = GraphElementRelatedField(many=True, read_only=True)

    class Meta:
        model = Graph
        fields = ('pk', '__str__', 'graph_elements',)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    contributors = UserSerializer(many=True, read_only=True)
    supervisors = UserSerializer(many=True, read_only=True)
    leaders = UserSerializer(many=True, read_only=True)
    graphs = GraphSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('pk', 'name', 'contributors', 'supervisors', 'leaders', 'graphs', 'created_by')


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resource
        fields = ('pk', 'name', )


class ObjectResourceSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    pk = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = ('pk', 'name', 'type', 'items',)

    def get_items(self, obj):
        if obj.resource is not None and obj.resource.cast().__class__.__name__ == "Folder":
            return FileSerializer(obj.resource.cast().items, many=True).data
        else:
            return []

    def get_type(self, obj):
        return obj.resource.cast().__class__.__name__ if obj.resource is not None else None

    def get_pk(self, obj):
        return obj.resource.cast().pk if obj.resource is not None else None