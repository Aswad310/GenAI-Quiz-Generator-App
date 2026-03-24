import uuid
import datetime
import os
from django.db import models
from django.conf import settings


def file_upload_path(instance, filename):
    current_date = datetime.datetime.now().timestamp()
    folders_for_upload_files = 'documents'
    filename = f'{current_date}_{filename}'
    file_2_be_saved_path = os.path.join(folders_for_upload_files, str(instance.user.id), filename)
    return file_2_be_saved_path


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=file_upload_path)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
