from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.conf import settings
from django.http import FileResponse
import os
import logging
from weasyprint import HTML
from datetime import datetime

logger = logging.getLogger(__name__)

# Создаем папку для загрузок, если её нет
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'uploads'), exist_ok=True)
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'docs'), exist_ok=True)

@api_view(['GET'])
def get_documentation(request):
    """Тестовый endpoint для документации"""
    return Response([
        {
            "title": "Тестовая документация",
            "description": "Это тестовый ответ от Django API",
            "code": "def example():\n    return 'Hello World'"
        }
    ])

class CodeUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        logger.info(f"Получен запрос. Данные: {request.data}, Файлы: {request.FILES}")
        
        if 'file' not in request.FILES:
            logger.error("Файл не найден в request.FILES")
            return Response(
                {'error': 'Файл не найден'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Проверки
        if uploaded_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'Файл слишком большой (макс. 5MB)'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        allowed_extensions = ['.py', '.js', '.ts', '.java'];
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return Response(
                {'error': f'Недопустимое расширение. Разрешены: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1. Сохраняем исходный файл
            source_path = os.path.join(settings.MEDIA_ROOT, 'uploads', uploaded_file.name)
            with open(source_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # 2. Читаем содержимое
            with open(source_path, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # 3. Генерируем PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"doc_{uploaded_file.name}_{timestamp}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, 'docs', pdf_filename)
            
            self.generate_pdf_documentation(
                code=code_content,
                filename=uploaded_file.name,
                output_path=pdf_path
            )

            # 4. Возвращаем ссылки
            pdf_url = request.build_absolute_uri(settings.MEDIA_URL + 'docs/' + pdf_filename)
            original_url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + uploaded_file.name)

            return Response({
                'status': 'success',
                'original_file': original_url,
                'pdf_documentation': pdf_url,
                'filename': uploaded_file.name,
                'pdf_filename': pdf_filename
            })

        except UnicodeDecodeError:
            return Response(
                {'error': 'Ошибка декодирования файла (используйте UTF-8)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Внутренняя ошибка сервера'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_pdf_documentation(self, code: str, filename: str, output_path: str):
        """Генерация PDF с документацией"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Документация для {filename}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2cm; }}
                h1 {{ color: #2c3e50; border-bottom: 1px solid #eee; }}
                pre {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                    overflow-x: auto;
                }}
                .meta {{ 
                    color: #7f8c8d; 
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>Документация к файлу: {filename}</h1>
            <div class="meta">
                Сгенерировано: {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
            <pre>{code}</pre>
        </body>
        </html>
        """
        HTML(string=html_content).write_pdf(output_path)
