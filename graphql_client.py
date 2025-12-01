"""
Cliente GraphQL para o experimento GraphQL vs REST
Implementa consultas GraphQL para a API do GitHub
"""

import requests
import time
from typing import Dict, Any, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


class GraphQLClient:
    """Cliente para realizar consultas GraphQL na API do GitHub"""
    
    def __init__(self, token: str = None):
        self.url = "https://api.github.com/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "GraphQL-REST-Experiment"
        }
        
        if token:
            self.headers["Authorization"] = f"bearer {token}"
        else:
            raise ValueError("Token do GitHub é obrigatório para usar a API GraphQL")
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _execute_query(self, query: str, variables: Dict = None) -> Tuple[Dict[Any, Any], float, int]:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        start_time = time.perf_counter()
        
        try:
            response = self.session.post(self.url, json=payload, timeout=30)
            response.raise_for_status()
            
            end_time = time.perf_counter()
            
            response_time_ms = (end_time - start_time) * 1000
            response_size_bytes = len(response.content)
            
            data = response.json()
            
            if "errors" in data:
                print(f"Erros GraphQL: {data['errors']}")
                raise Exception(f"GraphQL errors: {data['errors']}")
            
            return data["data"], response_time_ms, response_size_bytes
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição GraphQL: {e}")
            raise
    
    def get_user_simple(self, username: str) -> Tuple[Dict, float, int]:
        query = """
        query($login: String!) {
            user(login: $login) {
                login
                name
                bio
                company
                location
                websiteUrl
                avatarUrl
                createdAt
                updatedAt
                followers {
                    totalCount
                }
                following {
                    totalCount
                }
                repositories {
                    totalCount
                }
            }
        }
        """
        variables = {"login": username}
        return self._execute_query(query, variables)
    
    def get_repository_simple(self, owner: str, repo: str) -> Tuple[Dict, float, int]:
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                name
                description
                url
                createdAt
                updatedAt
                stargazerCount
                forkCount
                watchers {
                    totalCount
                }
                primaryLanguage {
                    name
                }
                isPrivate
                isFork
                licenseInfo {
                    name
                }
            }
        }
        """
        variables = {"owner": owner, "name": repo}
        return self._execute_query(query, variables)
    
    def get_user_with_repos(self, username: str) -> Tuple[Dict, float, int]:
        query = """
        query($login: String!) {
            user(login: $login) {
                login
                name
                bio
                company
                location
                followers {
                    totalCount
                }
                following {
                    totalCount
                }
                repositories(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
                    totalCount
                    nodes {
                        name
                        description
                        url
                        stargazerCount
                        forkCount
                        primaryLanguage {
                            name
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        variables = {"login": username}
        return self._execute_query(query, variables)
    
    def get_repo_with_issues(self, owner: str, repo: str) -> Tuple[Dict, float, int]:
        query = """
        query($owner: String!, $name: String!) {
            repository(owner: $owner, name: $name) {
                name
                description
                url
                stargazerCount
                forkCount
                createdAt
                updatedAt
                issues(first: 10, states: [OPEN, CLOSED], orderBy: {field: CREATED_AT, direction: DESC}) {
                    totalCount
                    nodes {
                        title
                        state
                        number
                        createdAt
                        updatedAt
                        author {
                            login
                        }
                        comments {
                            totalCount
                        }
                    }
                }
            }
        }
        """
        variables = {"owner": owner, "name": repo}
        return self._execute_query(query, variables)
    
    def search_repositories(self, query_string: str, first: int = 10) -> Tuple[Dict, float, int]:
        query = """
        query($queryString: String!, $first: Int!) {
            search(query: $queryString, type: REPOSITORY, first: $first) {
                repositoryCount
                nodes {
                    ... on Repository {
                        name
                        description
                        url
                        stargazerCount
                        forkCount
                        primaryLanguage {
                            name
                        }
                        owner {
                            login
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        variables = {"queryString": query_string, "first": first}
        return self._execute_query(query, variables)
    
    def search_users(self, query_string: str, first: int = 10) -> Tuple[Dict, float, int]:
        query = """
        query($queryString: String!, $first: Int!) {
            search(query: $queryString, type: USER, first: $first) {
                userCount
                nodes {
                    ... on User {
                        login
                        name
                        bio
                        location
                        company
                        avatarUrl
                        followers {
                            totalCount
                        }
                        repositories {
                            totalCount
                        }
                    }
                }
            }
        }
        """
        variables = {"queryString": query_string, "first": first}
        return self._execute_query(query, variables)
    
    def get_user_repos_paginated(self, username: str, first: int = 10, after: str = None) -> Tuple[Dict, float, int]:
        query = """
        query($login: String!, $first: Int!, $after: String) {
            user(login: $login) {
                repositories(first: $first, after: $after, orderBy: {field: UPDATED_AT, direction: DESC}) {
                    totalCount
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes {
                        name
                        description
                        url
                        stargazerCount
                        forkCount
                        primaryLanguage {
                            name
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """
        variables = {"login": username, "first": first}
        if after:
            variables["after"] = after
        
        return self._execute_query(query, variables)
    
    def get_repo_commits_paginated(self, owner: str, repo: str, first: int = 10, after: str = None) -> Tuple[Dict, float, int]:
        query = """
        query($owner: String!, $name: String!, $first: Int!, $after: String) {
            repository(owner: $owner, name: $name) {
                defaultBranchRef {
                    target {
                        ... on Commit {
                            history(first: $first, after: $after) {
                                totalCount
                                pageInfo {
                                    hasNextPage
                                    endCursor
                                }
                                nodes {
                                    message
                                    committedDate
                                    author {
                                        name
                                    }
                                    additions
                                    deletions
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"owner": owner, "name": repo, "first": first}
        if after:
            variables["after"] = after
        
        return self._execute_query(query, variables)
    
    def close(self):
        self.session.close()


def get_github_token() -> str:
    return os.getenv("GITHUB_TOKEN")


if __name__ == "__main__":
    token = get_github_token()
    
    if not token:
        print("ERRO: Token do GitHub não encontrado!")
        print("Por favor, defina a variável de ambiente GITHUB_TOKEN")
        print("Exemplo: set GITHUB_TOKEN=seu_token_aqui (Windows)")
        exit(1)
    
    client = GraphQLClient(token)
    
    try:
        print("=" * 50)
        print("Testando Cliente GraphQL")
        print("=" * 50)
        
        print("\n1. Consulta Simples - Usuário")
        data, time_ms, size_bytes = client.get_user_simple("torvalds")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Nome: {data['user'].get('name')}")
        
        time.sleep(1)
        
        print("\n2. Consulta com Relacionamentos - Usuário + Repos")
        data, time_ms, size_bytes = client.get_user_with_repos("torvalds")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Repositórios: {len(data['user']['repositories']['nodes'])}")
        
        time.sleep(1)
        
        print("\n3. Consulta com Filtros - Busca de Repositórios")
        data, time_ms, size_bytes = client.search_repositories("language:python stars:>10000")
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Total encontrado: {data['search'].get('repositoryCount')}")
        
        time.sleep(1)
        
        print("\n4. Consulta com Paginação - Repositórios do Usuário")
        data, time_ms, size_bytes = client.get_user_repos_paginated("torvalds", first=5)
        print(f"   Tempo: {time_ms:.2f} ms")
        print(f"   Tamanho: {size_bytes} bytes")
        print(f"   Repositórios retornados: {len(data['user']['repositories']['nodes'])}")
        
        print("\n" + "=" * 50)
        print("Testes GraphQL concluídos com sucesso!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nErro durante os testes: {e}")
    finally:
        client.close()

