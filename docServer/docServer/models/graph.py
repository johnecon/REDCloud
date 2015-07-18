import itertools

from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum

from docServer.models.abstract import AbsModel, InheritanceCastModel
from docServer.models.project import Project, Resource


class Graph(AbsModel):
    project = models.ForeignKey(Project, related_name='graphs')
    is_template = models.BooleanField(default=False)
    def __str__(self):
        return self.project.name

    @property
    def graph_elements(self):
        return itertools.chain(self.nodes.all(), self.edges.all(), self.areas.all())

    def is_due(self):
        return len([node for node in self.nodes.all() if node.is_due()]) > 0


class Area(InheritanceCastModel):
    graph = models.ForeignKey(Graph, related_name='areas')
    name = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, related_name="areas_created")
    width = models.FloatField(default=300)
    height = models.FloatField(default=800)
    location_x = models.FloatField(default=0)
    location_y = models.FloatField(default=0)
    expanded = models.BooleanField(default=True)

    @property
    def loc(self):
        return str(self.location_x) + " " + str(self.location_y)

    @property
    def is_group(self):
        return True

    def editable_attrs(self):
        return ["width", "height","location_x", "location_y", "expanded"]

    def __str__(self):
        return self.name

    def is_deletable(self):
        return False


class SwimLane(Area):
    user = models.ForeignKey(User, related_name="swimlanes")
    color = models.CharField(max_length=255, default="#ffffff")

    def editable_attrs(self):
        return ["color", "width", "height","location_x", "location_y", "expanded"]

    def save(self, *args, **kwargs):
        self.name = self.user.username
        super(SwimLane, self).save(*args, **kwargs)

    @property
    def is_group(self):
        return True


class Tense(enum.Enum):
    FUTURE = 0
    PRESENT = 1
    PAST = 2

    labels = {
        FUTURE: 'Future',
        PRESENT: 'Present',
        PAST: 'Past'
    }

    # _transitions = {
    #     PRESENT: (FUTURE,),
    #     PAST: (PRESENT,FUTURE,)
    # }


class Node(InheritanceCastModel):
    graph = models.ForeignKey(Graph, related_name='nodes')
    created_by = models.ForeignKey(User, related_name="nodes_created")
    location_x = models.FloatField(default=0)
    location_y = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    assigned_to = models.ForeignKey(Area, null=True, blank=True, related_name="nodes")

    def is_due():
        self.cast().is_due()

    @staticmethod
    def real_category(gojs_category):
        return {
            'Start': 'ControlNode',
            'Fork': 'ControlNode',
            'End': 'ControlNode',
            'Choice': 'ControlNode',
            'Action': 'ActionNode',
            'Object': 'ObjectNode',
            'Comment': 'CommentNode',
            'SwimLane': 'SwimLane',
            'Action-In': 'ActionNode',
            'Action-Im': 'ActionNode',
            'Action-Ex': 'ActionNode',
            'Edge': 'Edge',
            'Sync': 'Edge',
            'Boundary': 'Area',
            'Pool': 'Area',
        }[gojs_category]

    @property
    def loc(self):
        return str(self.location_x) + " " + str(self.location_y)

    @property
    def gojs_category(self):
        if self.__class__.__name__ == 'ControlNode':
            return {
                'S': 'Start',
                'F': 'Fork',
                'E': 'End',
                'C': 'Choice',
            }[self.type]
        elif self.__class__.__name__ == 'ActionNode':
            return "Action-" + self.operation_type
        else:
            return {
                'ControlNode': 'Start',
                'ActionNode': 'Action',
                'ObjectNode': 'Object',
                'CommentNode': 'Comment',
                'SwimLane': 'SwimLane',
                'Comment': 'Comment',
            }[self.__class__.__name__]

    def is_deletable(self):
        return self.cast().tense == Tense.FUTURE


class ObjectNode(Node):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_exported = models.BooleanField(default=False)
    resource = models.ForeignKey(Resource, null=True, blank=True, related_name="object_nodes")
    tense = enum.EnumField(Tense, default=Tense.FUTURE)
    date_realized = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    realized_by = models.ForeignKey(User, null=True, blank=True, related_name="object_nodes_realized")

    def is_due(self):
        return datetime.now() >= due_date

    def editable_attrs(self):
        return ["location_x", "location_y", "name", "description", "is_exported", "assigned_to", "tense",
                "date_realized", "realized_by", "width", "height"]

    def __str__(self):
        return self.name


class CommentNode(Node):
    name = models.CharField(max_length=255, blank=True)

    def is_due(self):
        return False

    def editable_attrs(self):
        return ["location_x", "location_y", "assigned_to", "name", "width", "height"]

    def is_deletable(self):
        return True


class ActionNode(Node):
    name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    tense = enum.EnumField(Tense, default=Tense.FUTURE)
    date_realized = models.DateTimeField(blank=True, null=True)
    realized_by = models.ForeignKey(User, null=True, blank=True, related_name="action_nodes_realized")
    operation_type = models.CharField(max_length=255, default='In')
    due_date = models.DateTimeField(blank=True, null=True)

    def is_due(self):
        return datetime.now() >= due_date

    def editable_attrs(self):
        return ["location_x", "location_y", "name", "description", "assigned_to", "tense", "date_realized",
                "realized_by", "operation_type", "width", "height"]

    def __str__(self):
        return self.name


class ControlNode(Node):
    type = models.CharField(max_length=255)

    def __str__(self):
        return "ControlNode: %s" % self.pk

    def editable_attrs(self):
        return ["location_x", "location_y", "assigned_to", "type"]

    def is_deletable(self):
        return False

    def is_due(self):
        return False


class EdgeType(enum.Enum):
    NORMAL = 0
    SYNC = 1

    labels = {
        NORMAL: 'Normal',
        SYNC: 'Sync'
    }


class Edge(AbsModel):
    graph = models.ForeignKey(Graph, related_name='edges')
    created_by = models.ForeignKey(User, related_name="edges_created")
    src = models.ForeignKey(Node, related_name="outgoing_edges")
    tgt = models.ForeignKey(Node, related_name="incoming_edges")
    fromPort = models.CharField(max_length=32, blank=True, default="B")
    toPort = models.CharField(max_length=32, blank=True, default="T")
    points = models.TextField(blank=True)
    type = enum.EnumField(EdgeType, default=EdgeType.NORMAL)

    def __str__(self):
        return "Edge: {0}, {1}".format(self.src, self.tgt)

    def cast(self):
        return self

    def category_class(self):
        return 'Edge' if self.type == EdgeType.NORMAL else 'Sync'

    def editable_attrs(self):
        return ["src", "tgt", "points", "fromPort", "toPort"]

    def is_deletable(self):
        return self.tgt.is_deletable()
