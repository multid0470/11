import os
import json
import requests
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from weasyprint import HTML
from django.views import View  # Import бары для View class

load_dotenv()

class GitHubDocumentationGenerator:
    """Класс для генерации документации из GitHub репозитория"""
    
    def __init__(self, owner, repo):
        self.owner = owner
        self.repo = repo
        self.headers = {
            "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repo_info(self):
        """Получение информации о репозитории"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_commits(self, limit=20):
        """Получение списка коммитов"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/commits?per_page={limit}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def analyze_code_structure(self):
        """Анализ структуры кода"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        items = response.json()
        return {
            "files": [item["name"] for item in items if item["type"] == "file"],
            "dirs": [item["name"] for item in items if item["type"] == "dir"]
        }

class CodeUploadView(View):  # Добавлен CodeUploadView
    def post(self, request):
        #  логика загрузки кода здесь
        return JsonResponse({"message": "Code uploaded successfully"})

def get_documentation(request):  # Добавлена функция get_documentation
    #  логика получения документации здесь
    return JsonResponse({"message": "Documentation retrieved successfully"})

@csrf_exempt
def generate_from_github(request):
    """Основной view для обработки запросов на генерацию документации"""
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)
    
    try:
        # Проверка и парсинг входных данных
        data = json.loads(request.body)
        github_url = data.get('url', '').strip()
        
        if not github_url or "github.com" not in github_url:
            return JsonResponse({"error": "Invalid GitHub URL"}, status=400)
        
        # Извлечение owner/repo из URL
        parts = [p for p in github_url.split('/') if p]
        if len(parts) < 2:
            return JsonResponse({"error": "Invalid GitHub repository URL"}, status=400)
            
        owner, repo = parts[-2], parts[-1]
        
        # Генерация документации
        generator = GitHubDocumentationGenerator(owner, repo)
        
        repo_info = generator.get_repo_info()
        commits = generator.get_commits()
        code_structure = generator.analyze_code_structure()
        
        # Создание PDF
        html_content = generate_html_content(repo_info, commits, code_structure, github_url)
        pdf = HTML(string=html_content).write_pdf()
        
        # Формирование ответа
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{repo}_documentation_{datetime.now().date()}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except requests.HTTPError as e:
        return JsonResponse({"error": f"GitHub API error: {str(e)}"}, status=502)
    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

def generate_html_content(repo_info, commits, code_structure, github_url):
    """Генерация HTML контента для PDF"""
    commit_items = "".join(
        f'<div class="commit"><strong>{c["commit"]["author"]["name"]}</strong>: {c["commit"]["message"]}</div>'
        for c in commits
    )
    
    return f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <title>{repo_info['name']} Documentation</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 2cm; 
                    line-height: 1.6;
                }}
                h1 {{ 
                    color: #0366d6; 
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
                .section {{ 
                    margin-bottom: 1.5em; 
                }}
                .commit {{ 
                    margin: 0.5em 0; 
                    padding: 0.5em 1em; 
                    border-left: 3px solid #0366d6;
                    background-color: #f8f9fa;
                }}
                .file-list, .dir-list {{
                    padding-left: 20px;
                }}
                .footer {{ 
                    margin-top: 2em; 
                    font-size: 0.8em; 
                    color: #666;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1>{repo_info['name']} Documentation</h1>
            
            <div class="section">
                <h2>Repository Information</h2>
                <p><strong>Description:</strong> {repo_info.get('description', 'No description')}</p>
                <p><strong>URL:</strong> <a href="{github_url}">{github_url}</a></p>
                <p><strong>Last updated:</strong> {repo_info['updated_at']}</p>
                <p><strong>Stars:</strong> {repo_info.get('stargazers_count', 0)}</p>
            </div>
            
            <div class="section">
                <h2>Recent Commits</h2>
                {commit_items}
            </div>
            
            <div class="section">
                <h2>Code Structure</h2>
                <p><strong>Files:</strong></p>
                <ul class="file-list">
                    {''.join(f'<li>{file}</li>' for file in code_structure['files'][:10])}
                    {'<li>...</li>' if len(code_structure['files']) > 10 else ''}
                </ul>
                <p><strong>Directories:</strong></p>
                <ul class="dir-list">
                    {''.join(f'<li>{directory}</li>' for directory in code_structure['dirs'])}
                </ul>
            </div>
            
            <div class="footer">
                Documentation generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
                Source: <a href="{github_url}">{github_url}</a>
            </div>
        </body>
    </html>
    """
