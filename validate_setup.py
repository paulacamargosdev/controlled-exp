"""
Script de validação do ambiente experimental
Verifica se todas as dependências e configurações estão corretas
"""

import sys
import os
from dotenv import load_dotenv


def check_python_version():
    print("[*] Verificando versao do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [ERRO] Python {version.major}.{version.minor}.{version.micro} (Requer Python 3.9+)")
        return False


def check_dependencies():
    print("\n[*] Verificando dependencias...")
    
    required_packages = [
        "requests",
        "pandas",
        "numpy"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   [OK] {package}")
        except ImportError:
            print(f"   [ERRO] {package} (nao encontrado)")
            missing.append(package)
    
    if missing:
        print(f"\n   Para instalar os pacotes faltantes, execute:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_github_token():
    print("\n[*] Verificando token do GitHub...")
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    
    if token:
        token_preview = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
        print(f"   [OK] Token encontrado: {token_preview}")
        return True
    else:
        print("   [ERRO] Token nao encontrado na variavel de ambiente GITHUB_TOKEN")
        print("\n   Para configurar o token:")
        print("   Windows (PowerShell): $env:GITHUB_TOKEN='seu_token_aqui'")
        print("   Windows (CMD): set GITHUB_TOKEN=seu_token_aqui")
        print("   Ou crie um arquivo .env com: GITHUB_TOKEN=seu_token_aqui")
        return False


def check_network_access():
    print("\n[*] Verificando acesso a API do GitHub...")
    
    try:
        import requests
        response = requests.get("https://api.github.com", timeout=10)
        if response.status_code == 200:
            print("   [OK] Acesso a API REST do GitHub")
            
            rate_limit = response.headers.get("X-RateLimit-Limit", "N/A")
            print(f"   [INFO] Rate limit: {rate_limit} requisicoes/hora")
            return True
        else:
            print(f"   [ERRO] Erro ao acessar API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERRO] Erro de conexao: {e}")
        return False


def check_files():
    print("\n[*] Verificando arquivos do projeto...")
    
    required_files = [
        "rest_client.py",
        "graphql_client.py",
        "experiment.py",
        "requirements.txt",
        "README.md",
        "desenho_experimento.md"
    ]
    
    all_exist = True
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"   [OK] {filename}")
        else:
            print(f"   [ERRO] {filename} (nao encontrado)")
            all_exist = False
    
    return all_exist


def test_clients():
    print("\n[*] Testando clientes de API...")
    
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("   [AVISO] Pulando testes de cliente (token nao configurado)")
        return True
    
    try:
        from rest_client import RESTClient
        client = RESTClient(token)
        print("   [OK] Cliente REST inicializado")
        client.close()
    except Exception as e:
        print(f"   [ERRO] Erro no cliente REST: {e}")
        return False
    
    try:
        from graphql_client import GraphQLClient
        client = GraphQLClient(token)
        print("   [OK] Cliente GraphQL inicializado")
        client.close()
    except Exception as e:
        print(f"   [ERRO] Erro no cliente GraphQL: {e}")
        return False
    
    return True


def create_results_directory():
    print("\n[*] Verificando diretorio de resultados...")
    
    if not os.path.exists("results"):
        os.makedirs("results")
        print("   [OK] Diretorio 'results/' criado")
    else:
        print("   [OK] Diretorio 'results/' ja existe")
    
    return True


def main():
    load_dotenv()
    
    print("=" * 70)
    print("VALIDACAO DO AMBIENTE EXPERIMENTAL")
    print("Laboratorio 05 - GraphQL vs REST")
    print("=" * 70)
    
    checks = [
        ("Versao do Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Token GitHub", check_github_token),
        ("Acesso a rede", check_network_access),
        ("Arquivos do projeto", check_files),
        ("Diretorio de resultados", create_results_directory),
        ("Clientes de API", test_clients)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n   [ERRO] Erro durante verificacao de '{name}': {e}")
            results[name] = False
    
    print("\n" + "=" * 70)
    print("SUMARIO DA VALIDACAO")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, status in results.items():
        symbol = "[OK]" if status else "[ERRO]"
        print(f"  {symbol} {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("[SUCESSO] AMBIENTE PRONTO PARA EXECUCAO DO EXPERIMENTO!")
        print("=" * 70)
        print("\nProximos passos:")
        print("  1. Execute: python experiment.py")
        print("  2. Aguarde a conclusao (aproximadamente 4-5 minutos)")
        print("  3. Verifique os resultados no diretorio 'results/'")
        return 0
    else:
        print(f"[ATENCAO] {total - passed} verificacao(oes) falharam")
        print("=" * 70)
        print("\nCorrecoes necessarias:")
        
        if not results.get("Token GitHub", True):
            print("  - Configure o token do GitHub (veja README.md)")
        
        if not results.get("Dependencias", True):
            print("  - Instale as dependencias: pip install -r requirements.txt")
        
        if not results.get("Versao do Python", True):
            print("  - Atualize para Python 3.9 ou superior")
        
        print("\nConsulte o README.md para instrucoes detalhadas.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

