import os
import tempfile
import shutil
import stat
import time
import ast
import markdown2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from git import Repo

class UploadRepoUrlView(APIView):
    def post(self, request, format=None):
        repo_url = request.data.get('repo_url')
        if not repo_url:
            return Response({'error': 'No repo_url provided'}, status=status.HTTP_400_BAD_REQUEST)

        temp_dir = tempfile.mkdtemp()
        repo = None
        try:
            # Клонируем репозиторий
            repo = Repo.clone_from(repo_url, temp_dir)
            docs = self.generate_documentation(temp_dir, repo)
        except Exception as e:
            safe_rmtree(temp_dir)
            return Response({'error': str(e)}, status=400)
        
        if repo is not None and hasattr(repo, 'close'):
            repo.close()
        time.sleep(0.5)
        safe_rmtree(temp_dir)
        return Response(docs, status=200)

    def generate_documentation(self, repo_path, repo):
        """Генерирует документацию в заданном формате"""
        return {
            'readme': self.parse_readme(repo_path),
            'commits': self.get_commits(repo),
            'code': self.analyze_code(repo_path)
        }

    def parse_readme(self, path):
        """Парсит README в Markdown формате"""
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().startswith('readme'):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {
                        'filename': file,
                        'content': markdown2.markdown(content),
                        'raw_content': content
                    }
        return None

    def analyze_code(self, path):
        """Анализирует код и возвращает структурированные данные"""
        result = {
            'classes': [],
            'functions': []
        }

        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                methods = []
                                for item in node.body:
                                    if isinstance(item, ast.FunctionDef):
                                        methods.append({
                                            'name': item.name,
                                            'args': self.get_function_args(item),
                                            'docstring': ast.get_docstring(item) or ''
                                        })
                                
                                result['classes'].append({
                                    'name': node.name,
                                    'docstring': ast.get_docstring(node) or '',
                                    'methods': methods,
                                    'file': os.path.relpath(file_path, path)
                                })
                            
                            elif isinstance(node, ast.FunctionDef):
                                result['functions'].append({
                                    'name': node.name,
                                    'args': self.get_function_args(node),
                                    'docstring': ast.get_docstring(node) or '',
                                    'file': os.path.relpath(file_path, path)
                                })
                    except Exception:
                        continue
        
        return result

    def get_function_args(self, node):
        """Извлекает аргументы функции"""
        args = [arg.arg for arg in node.args.args]
        if node.args.vararg:
            args.append(f'*{node.args.vararg.arg}')
        if node.args.kwarg:
            args.append(f'**{node.args.kwarg.arg}')
        return ', '.join(args)

    def get_commits(self, repo, max_count=5):
        """Получает историю коммитов"""
        commits = []
        branch = repo.head.reference.name if repo.head.is_valid() else 'main'
        for commit in repo.iter_commits(branch, max_count=max_count):
            commits.append({
                'message': commit.message.strip(),
                'author': commit.author.name,
                'date': commit.committed_datetime.strftime('%Y-%m-%d')
            })
        return commits

def safe_rmtree(path):
    """Безопасное удаление директории"""
    def remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)