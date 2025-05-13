from celery import shared_task
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML
from .models import CodeDocumentation

@shared_task
def generate_pdf(doc_id):
    doc = CodeDocumentation.objects.get(id=doc_id)
    
    # Чтение кода
    with open(doc.original_code.path, 'r') as f:
        code = f.read()

    # Генерация HTML
    html = render_to_string('code_docs/template.html', {
        'code': code,
        'user': doc.user.username,
        'filename': doc.title
    })

    # Конвертация в PDF
    pdf = HTML(string=html).write_pdf()
    
    # Сохранение PDF
    pdf_name = f"documentation_{doc.id}.pdf"
    doc.generated_pdf.save(pdf_name, ContentFile(pdf))
    doc.is_processed = True
    doc.save()