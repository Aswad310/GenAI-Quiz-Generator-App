import uuid
import datetime
import os
from django.db import models
from django.conf import settings


def file_upload_path(instance, filename):
    current_date = datetime.datetime.now().timestamp()
    folders_for_upload_files = 'documents'

    # Split filename and extension
    name, ext = os.path.splitext(filename)

    # Truncate filename part to 100 chars to avoid exceeding total path length
    if len(name) > 100:
        name = name[:100]

    filename = f'{current_date}_{name}{ext}'

    file_2_be_saved_path = os.path.join(folders_for_upload_files, str(instance.user.id), filename)
    return file_2_be_saved_path


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=file_upload_path, max_length=500)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
