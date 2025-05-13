from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass

class CodeDocumentation(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    code_example = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class APIDocumentation(models.Model):
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    description = models.TextField()
    parameters = models.JSONField()
    responses = models.JSONField()

class DatabaseSchema(models.Model):
    name = models.CharField(max_length=100)
    schema = models.JSONField()
    description = models.TextField()