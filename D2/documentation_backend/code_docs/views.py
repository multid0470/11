from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .models import CodeDocumentation
import magic

@login_required
@require_POST
def upload_code(request):
    if 'code_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    file = request.FILES['code_file']
    
    # Проверка типа файла (разрешаем только текстовые)
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if not mime.startswith('text/'):
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    # Сохраняем файл
    doc = CodeDocumentation.objects.create(
        user=request.user,
        title=file.name,
        original_code=file
    )

    # Запускаем генерацию PDF (через Celery)
    from .tasks import generate_pdf
    generate_pdf.delay(doc.id)

    return JsonResponse({'doc_id': doc.id})

@login_required
def download_pdf(request, doc_id):
    doc = CodeDocumentation.objects.get(id=doc_id, user=request.user)
    return FileResponse(doc.generated_pdf.open(), as_attachment=True)