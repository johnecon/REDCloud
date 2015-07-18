from io import BytesIO
import zipfile
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from docServer.forms import *
import mimetypes

from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext

from ajaxuploader.views import AjaxFileUploader
from docServer.ajaxuploader_backends import LocalFileBackend


def start(request):
    return render_to_response('import.html',
                              {'csrf_token': get_token(request)}, context_instance=RequestContext(request))


import_uploader = AjaxFileUploader(backend=LocalFileBackend)


def index(request):
    params = {'current': 'home'}
    return render(request, 'index.html', params)


def respond_as_attachment(request, file_path, original_filename):
    fp = open(file_path, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    file_type, encoding = mimetypes.guess_type(original_filename)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = str(os.stat(file_path).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding
    filename_header = 'filename=%s' % original_filename
    response['Content-Disposition'] = 'attachment; ' + filename_header
    response.set_cookie('fileDownload', 'true', path='/')
    return response


class ResourceFormMixin(object):
    model = Resource
    form_class = ResourceForm
    template_name = 'resource/_form.html'


class EditResourceModal(ResourceFormMixin, UpdateView):
    model = Resource
    template_name = 'resource/modal_form.html'


class ProjectList(ListView):
    model = Project
    template_name = 'project/list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ProjectList, self).get_context_data(**kwargs)
        context['object_name'] = 'Project'
        return context

    def get_queryset(self):
        return Project.objects.filter(
            Q(id__in=self.request.user.projects_created.all()) | Q(id__in=self.request.user.projects_contributed.all()))


class ProjectDetail(DetailView):
    model = Project
    template_name = 'project/view.html'

    def dispatch(self, *args, **kwargs):
        if not (Project.objects.get(pk=kwargs.get('pk')).is_editable_by_user(self.request.user)):
            return HttpResponse('Unauthorized', status=403)
        return super(ProjectDetail, self).dispatch(*args, **kwargs)


def get_dir(f_dir, name):
    f_dir, f_name = os.path.split(f_dir)
    directory = ""
    while f_name != name:
        directory = f_name + "/" + directory
        f_dir, f_name = os.path.split(f_dir)
    return directory


def flatten(l):
    basestring = (str, bytes)
    import collections

    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def resource_download(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if resource.instance_of("File"):
        return respond_as_attachment(request, resource.cast().file.path, resource.cast().file_name())
    else:
        file_names = flatten(resource.file_path())
        zip_subdir = resource.name
        zip_filename = "%s.zip" % zip_subdir
        s = BytesIO()
        zf = zipfile.ZipFile(s, "w")

        for f_path in file_names:
            f_dir, f_name = os.path.split(f_path)
            zip_path = os.path.join(zip_subdir, get_dir(f_dir, resource.cast().slug), f_name)
            zf.write(f_path, zip_path)
        zf.close()
        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class ResourceList(ListView):
    model = Resource
    template_name = 'resource/list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(ResourceList, self).get_context_data(**kwargs)
        context['object_name'] = 'Resource'
        return context


class ResourceDetail(DetailView):
    model = Resource
    template_name = 'resource/view.html'


class NewResource(ResourceFormMixin, CreateView):
    pass


class EditResource(ResourceFormMixin, UpdateView):
    model = Resource
    template_name = 'resource/update.html'


class DeleteResource(DeleteView):
    model = Resource
    template_name = 'resource/delete.html'

    def get_success_url(self):
        return reverse('Resource_list')
