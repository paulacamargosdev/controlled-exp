"""
Cliente REST para o experimento GraphQL vs REST
Implementa consultas REST para a API do GitHub
"""

import requests
import time
from typing import Dict, Any, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


class RESTClient:

    def __init__(self, token: str = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GraphQL-REST-Experiment"
        }
        
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url: str, params: Dict = None) -> Tuple[Dict[Any, Any], float, int]:
        start_time = time.perf_counter()
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            end_time = time.perf_counter()
            
            response_time_ms = (end_time - start_time) * 1000
            response_size_bytes = len(response.content)
            
            data = response.json()
            
            return data, response_time_ms, response_size_bytes
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição REST: {e}")
            raise
    
    def get_user_simple(self, username: str) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/users/{username}"
        return self._make_request(url)
    
    def get_repository_simple(self, owner: str, repo: str) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/repos/{owner}/{repo}"
        return self._make_request(url)
    
    def get_user_with_repos(self, username: str) -> Tuple[Dict, float, int]:
        start_time = time.perf_counter()
        total_size = 0
        
        user_url = f"{self.base_url}/users/{username}"
        response1 = self.session.get(user_url, timeout=30)
        response1.raise_for_status()
        user_data = response1.json()
        total_size += len(response1.content)
        
        repos_url = f"{self.base_url}/users/{username}/repos"
        response2 = self.session.get(repos_url, params={"per_page": 10}, timeout=30)
        response2.raise_for_status()
        repos_data = response2.json()
        total_size += len(response2.content)
        
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000
        
        combined_data = {
            "user": user_data,
            "repositories": repos_data
        }
        
        return combined_data, total_time_ms, total_size
    
    def get_repo_with_issues(self, owner: str, repo: str) -> Tuple[Dict, float, int]:
        start_time = time.perf_counter()
        total_size = 0
        
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        response1 = self.session.get(repo_url, timeout=30)
        response1.raise_for_status()
        repo_data = response1.json()
        total_size += len(response1.content)
        
        issues_url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        response2 = self.session.get(issues_url, params={"per_page": 10, "state": "all"}, timeout=30)
        response2.raise_for_status()
        issues_data = response2.json()
        total_size += len(response2.content)
        
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000
        
        combined_data = {
            "repository": repo_data,
            "issues": issues_data
        }
        
        return combined_data, total_time_ms, total_size
    
    def search_repositories(self, query: str, per_page: int = 10) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "per_page": per_page,
            "sort": "stars",
            "order": "desc"
        }
        return self._make_request(url, params)
    
    def search_users(self, query: str, per_page: int = 10) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/search/users"
        params = {
            "q": query,
            "per_page": per_page
        }
        return self._make_request(url, params)

    def get_user_repos_paginated(self, username: str, per_page: int = 10, page: int = 1) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "direction": "desc"
        }
        return self._make_request(url, params)
    
    def get_repo_commits_paginated(self, owner: str, repo: str, per_page: int = 10, page: int = 1) -> Tuple[Dict, float, int]:
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            "per_page": per_page,
            "page": page
        }
        return self._make_request(url, params)
    
    def close(self):
        self.session.close()


def get_github_token() -> str:
    return os.getenv("GITHUB_TOKEN")


if __name__ == "__main__":
    token = get_github_token()
    client = RESTClient(token)
    
    try:
        print("=" * 50)
        print("Testando Cliente REST")
        print("=" * 50)
        
        print("\n1. Consulta Simples - Usuário")
        data, time_ms, size_bytes = client.get_user_simple("torvalds")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Nome: {data.get('name')}")
        
        time.sleep(1)
        
        print("\n2. Consulta com Relacionamentos - Usuário + Repos")
        data, time_ms, size_bytes = client.get_user_with_repos("torvalds")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Repositórios: {len(data['repositories'])}")
        
        time.sleep(1)
        
        print("\n3. Consulta com Filtros - Busca de Repositórios")
        data, time_ms, size_bytes = client.search_repositories("language:python stars:>10000")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Total encontrado: {data.get('total_count')}")
        
        time.sleep(1)
        
        print("\n4. Consulta com Paginação - Repositórios do Usuário")
        data, time_ms, size_bytes = client.get_user_repos_paginated("torvalds", per_page=5, page=1)
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Repositórios retornados: {len(data)}")
        
        print("\n" + "=" * 50)
        print("Testes REST concluídos com sucesso!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nErro durante os testes: {e}")
    finally:
        client.close()

