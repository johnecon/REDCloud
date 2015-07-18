from ajaxuploader.backends.local import LocalUploadBackend
from django.conf import settings
from io import FileIO, BufferedWriter

from docServer.models.project import *


class LocalFileBackend(LocalUploadBackend):

    def upload_dir(self, kwargs):
        return os.path.join(getattr(settings, "UPLOAD_DIR", "resources") , "project_"  + str(kwargs['pk']))

    def upload_complete(self, request, filename, *args, **kwargs):
        path = os.path.join(self.upload_dir(kwargs), filename)
        self._dest.close()
        file = File.objects.create(created_by=request.user, file=path, name=request.GET['qqfile'],
                                   project=Project.objects.get(pk=kwargs['pk']))
        return {"path": path, "resource_pk": file.pk}

    def setup(self, filename, *args, **kwargs):
        self._path = os.path.join(
            settings.MEDIA_ROOT, self.upload_dir(kwargs), filename)
        try:
            os.makedirs(os.path.realpath(os.path.dirname(self._path)))
        except:
            pass
        self._dest = BufferedWriter(FileIO(self._path, "w"))

    def update_filename(self, request, filename, *args, **kwargs):
        """
        Returns a new name for the file being uploaded.
        Ensure file with name doesn't exist, and if it does,
        create a unique filename to avoid overwriting
        """
        filename = os.path.basename(filename)
        self._dir = os.path.join(
            settings.MEDIA_ROOT, self.upload_dir(kwargs))
        unique_filename = False
        filename_suffix = 0

        # Check if file at filename exists
        if os.path.isfile(os.path.join(self._dir, filename)):
            while not unique_filename:
                try:
                    if filename_suffix == 0:
                        open(os.path.join(self._dir, filename))
                    else:
                        filename_no_extension, extension = os.path.splitext(filename)
                        open(os.path.join(self._dir, filename_no_extension + str(filename_suffix) + extension))
                    filename_suffix += 1
                except IOError:
                    unique_filename = True

        if filename_suffix == 0:
            return filename
        else:
            return filename_no_extension + str(filename_suffix) + extension