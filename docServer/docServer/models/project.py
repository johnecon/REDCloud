import os

from django.db import models
from django.contrib.auth.models import User

from docServer.models.abstract import AbsModel, InheritanceCastModel


class Project(AbsModel):
    name = models.CharField(max_length=255)
    contributors = models.ManyToManyField(User, blank=True, related_name="projects_contributed")
    leaders = models.ManyToManyField(User, blank=True, related_name="projects_leaded")
    supervisors = models.ManyToManyField(User, blank=True, related_name="projects_supervised")
    created_by = models.ForeignKey(User, null=True, related_name="projects_created")

    def __str__(self):
        return self.name

    def is_editable_by_user(self, user):
        return self.created_by == user or user in self.team_members(supervisors=True)

    def get_roles_of(self, user):
        roles = []
        if user in self.contributors.all():
            roles.append("Contributor")
        if user in self.leaders.all():
            roles.append("Leader")
        if user in self.supervisors.all():
            roles.append("Supervisor")
        return ",".join(roles)

    def team_members(self, supervisors=False):
        team_members = self.contributors.all() | self.leaders.all()
        return team_members | self.supervisors.all() if supervisors else team_members

    def add_user(self, user, role):
        if role == "Supervisor":
            self.supervisors.add(user)
        elif role == "Leader":
            self.leaders.add(user)
        else:
            self.contributors.add(user)

    @models.permalink
    def get_absolute_url(self):
        return 'project_detail', [self.pk]


class Resource(InheritanceCastModel):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project)
    created_by = models.ForeignKey(User)

    def clone(self, folder=None):
        return self.cast().clone(folder)

    def file_path(self):
        return self.cast().file_path()

    def __str__(self):
        return self.name


class Folder(Resource):
    items = models.ManyToManyField('Resource', related_name="parent_folder", symmetrical=False, blank=True, null=True)

    def file_path(self):
        return [item.file_path() for item in self.items.all()]

    def clone(self, folder=None):
        folder_name = (folder.slug + "/" if folder else "") + self.name
        new_folder = Folder.objects.create(name=folder_name, project=self.project, created_by=self.created_by)
        [new_folder.items.add(item.clone(new_folder)) for item in self.items.all()]
        new_folder.save()
        return new_folder

    @property
    def slug(self):
        return '%(name)s_%(id)d' % {'name': self.name, 'id': self.id}


def resources_upload_path(instance, filename):
    parent_folder = instance.parent_folder.first()
    folder_path_name = parent_folder.slug \
        if parent_folder else ''
    return os.path.join(
        "resources", "project_" + str(instance.project_id), folder_path_name, filename)


class File(Resource):
    file = models.FileField(upload_to=resources_upload_path, blank=True, null=True)
    format = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{0} {1}".format(self.file_name(), self.pk)

    def clone(self, folder=None):
        from django.core.files.base import ContentFile

        file = File.objects.create(created_by=self.created_by, name=self.name,
                                   project=self.project)
        file.file = ContentFile(self.file.read())
        file.file.name = (folder.slug + "/" if folder is not None else "") + self.file_name()
        file.save()
        return file

    def file_name(self):
        return os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(File, self).delete(*args, **kwargs)

    def file_extension(self):
        file_name, file_type = os.path.splitext(self.file.name)
        return file_type

    def file_path(self):
        return self.file.path
