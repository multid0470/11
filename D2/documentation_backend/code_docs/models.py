from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CodeDocumentation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    original_code = models.FileField(upload_to='user_codes/')
    generated_pdf = models.FileField(upload_to='generated_pdfs/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)