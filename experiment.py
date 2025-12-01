"""
Script principal para execução do experimento GraphQL vs REST
Coordena a execução dos tratamentos e coleta de dados
"""

import time
import random
import csv
import json
from datetime import datetime
from typing import List, Dict, Tuple
import os
from rest_client import RESTClient
from graphql_client import GraphQLClient
from dotenv import load_dotenv

load_dotenv()

class ExperimentRunner:

    
    def __init__(self, token: str, output_dir: str = "results"):
        self.rest_client = RESTClient(token)
        self.graphql_client = GraphQLClient(token)
        self.output_dir = output_dir
        self.results = []
        
        os.makedirs(output_dir, exist_ok=True)
    
    def _record_measurement(
        self, 
        api_type: str, 
        query_type: str, 
        query_name: str,
        response_time_ms: float, 
        response_size_bytes: int,
        success: bool = True,
        error_msg: str = None
    ):
        """
        Registra uma medição do experimento
        
        Args:
            api_type: Tipo de API (REST ou GraphQL)
            query_type: Tipo de consulta (simples, relacionamentos, filtros, paginação)
            query_name: Nome específico da consulta
            response_time_ms: Tempo de resposta em milissegundos
            response_size_bytes: Tamanho da resposta em bytes
            success: Se a consulta foi bem-sucedida
            error_msg: Mensagem de erro (se houver)
        """
        measurement = {
            "timestamp": datetime.now().isoformat(),
            "api_type": api_type,
            "query_type": query_type,
            "query_name": query_name,
            "response_time_ms": response_time_ms,
            "response_size_bytes": response_size_bytes,
            "success": success,
            "error_msg": error_msg
        }
        self.results.append(measurement)
    
    def run_simple_queries(self, repetitions: int = 30):
        print("\n" + "=" * 60)
        print("EXECUTANDO TRATAMENTOS T1 e T2: Consultas Simples")
        print("=" * 60)
        
        test_users = ["torvalds", "gvanrossum", "mojombo", "defunkt", "pjhyett"]
        
        for i in range(repetitions):
            user = random.choice(test_users)
            
            try:
                print(f"\n[{i+1}/{repetitions}] T1 - REST: Consultando usuário {user}")
                _, time_ms, size_bytes = self.rest_client.get_user_simple(user)
                self._record_measurement("REST", "simples", "get_user", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("REST", "simples", "get_user", 0, 0, False, str(e))
            
            time.sleep(1)
            
            try:
                print(f"[{i+1}/{repetitions}] T2 - GraphQL: Consultando usuário {user}")
                _, time_ms, size_bytes = self.graphql_client.get_user_simple(user)
                self._record_measurement("GraphQL", "simples", "get_user", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("GraphQL", "simples", "get_user", 0, 0, False, str(e))
            
            time.sleep(1)
    
    def run_relationship_queries(self, repetitions: int = 30):
        print("\n" + "=" * 60)
        print("EXECUTANDO TRATAMENTOS T3 e T4: Consultas com Relacionamentos")
        print("=" * 60)
        
        test_users = ["torvalds", "gvanrossum", "mojombo", "defunkt", "pjhyett"]
        
        for i in range(repetitions):
            user = random.choice(test_users)
            
            try:
                print(f"\n[{i+1}/{repetitions}] T3 - REST: Consultando {user} + repositórios")
                _, time_ms, size_bytes = self.rest_client.get_user_with_repos(user)
                self._record_measurement("REST", "relacionamentos", "get_user_with_repos", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("REST", "relacionamentos", "get_user_with_repos", 0, 0, False, str(e))
            
            time.sleep(1)
            
            try:
                print(f"[{i+1}/{repetitions}] T4 - GraphQL: Consultando {user} + repositórios")
                _, time_ms, size_bytes = self.graphql_client.get_user_with_repos(user)
                self._record_measurement("GraphQL", "relacionamentos", "get_user_with_repos", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("GraphQL", "relacionamentos", "get_user_with_repos", 0, 0, False, str(e))
            
            time.sleep(1)
    
    def run_filter_queries(self, repetitions: int = 30):
        print("\n" + "=" * 60)
        print("EXECUTANDO TRATAMENTOS T5 e T6: Consultas com Filtros")
        print("=" * 60)
        
        search_queries = [
            "language:python stars:>10000",
            "language:javascript stars:>5000",
            "language:java stars:>3000",
            "language:go stars:>2000",
            "topic:machine-learning stars:>1000"
        ]
        
        for i in range(repetitions):
            query = random.choice(search_queries)
            
            try:
                print(f"\n[{i+1}/{repetitions}] T5 - REST: Buscando '{query}'")
                _, time_ms, size_bytes = self.rest_client.search_repositories(query)
                self._record_measurement("REST", "filtros", "search_repositories", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("REST", "filtros", "search_repositories", 0, 0, False, str(e))
            
            time.sleep(1)
            
            try:
                print(f"[{i+1}/{repetitions}] T6 - GraphQL: Buscando '{query}'")
                _, time_ms, size_bytes = self.graphql_client.search_repositories(query)
                self._record_measurement("GraphQL", "filtros", "search_repositories", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("GraphQL", "filtros", "search_repositories", 0, 0, False, str(e))
            
            time.sleep(1)
    
    def run_pagination_queries(self, repetitions: int = 30):
        print("\n" + "=" * 60)
        print("EXECUTANDO TRATAMENTOS T7 e T8: Consultas com Paginação")
        print("=" * 60)
        
        test_users = ["torvalds", "gvanrossum", "mojombo", "defunkt", "pjhyett"]
        
        for i in range(repetitions):
            user = random.choice(test_users)
            page = random.randint(1, 3)
            
            try:
                print(f"\n[{i+1}/{repetitions}] T7 - REST: Repos de {user} (página {page})")
                _, time_ms, size_bytes = self.rest_client.get_user_repos_paginated(user, per_page=10, page=page)
                self._record_measurement("REST", "paginacao", "get_repos_paginated", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("REST", "paginacao", "get_repos_paginated", 0, 0, False, str(e))
            
            time.sleep(1)
            
            try:
                print(f"[{i+1}/{repetitions}] T8 - GraphQL: Repos de {user} (primeiros 10)")
                _, time_ms, size_bytes = self.graphql_client.get_user_repos_paginated(user, first=10)
                self._record_measurement("GraphQL", "paginacao", "get_repos_paginated", time_ms, size_bytes)
                print(f"  ✓ Tempo: {time_ms:.2f} ms | Tamanho: {size_bytes} bytes")
            except Exception as e:
                print(f"  ✗ Erro: {e}")
                self._record_measurement("GraphQL", "paginacao", "get_repos_paginated", 0, 0, False, str(e))
            
            time.sleep(1)
    
    def run_full_experiment(self, repetitions: int = 30, randomize: bool = True):
        print("\n" + "=" * 70)
        print("INICIANDO EXPERIMENTO COMPLETO: GraphQL vs REST")
        print("=" * 70)
        print(f"Configuração:")
        print(f"  - Repetições por tratamento: {repetitions}")
        print(f"  - Total de medições esperadas: {8 * repetitions}")
        print(f"  - Ordem randomizada: {randomize}")
        print(f"  - Data/Hora de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        treatments = [
            ("simples", self.run_simple_queries),
            ("relacionamentos", self.run_relationship_queries),
            ("filtros", self.run_filter_queries),
            ("paginacao", self.run_pagination_queries)
        ]
        
        if randomize:
            random.shuffle(treatments)
            print("\n✓ Ordem de execução dos tratamentos foi randomizada")
        
        start_time = time.time()
        
        for treatment_name, treatment_func in treatments:
            try:
                treatment_func(repetitions)
            except Exception as e:
                print(f"\n✗ Erro crítico no tratamento '{treatment_name}': {e}")
                print("Continuando com próximo tratamento...")
        
        end_time = time.time()
        duration_minutes = (end_time - start_time) / 60
        
        print("\n" + "=" * 70)
        print("EXPERIMENTO CONCLUÍDO")
        print("=" * 70)
        print(f"  - Data/Hora de término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - Duração total: {duration_minutes:.2f} minutos")
        print(f"  - Total de medições coletadas: {len(self.results)}")
        print(f"  - Medições bem-sucedidas: {sum(1 for r in self.results if r['success'])}")
        print(f"  - Medições com erro: {sum(1 for r in self.results if not r['success'])}")
        print("=" * 70)
    
    def save_results(self, filename_prefix: str = "experiment"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        csv_filename = os.path.join(self.output_dir, f"{filename_prefix}_{timestamp}.csv")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            if self.results:
                fieldnames = self.results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
        
        print(f"\n✓ Resultados salvos em CSV: {csv_filename}")
        
        json_filename = os.path.join(self.output_dir, f"{filename_prefix}_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.results, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ Resultados salvos em JSON: {json_filename}")
        
        self._save_summary(filename_prefix, timestamp)
    
    def _save_summary(self, filename_prefix: str, timestamp: str):
        summary_filename = os.path.join(self.output_dir, f"{filename_prefix}_{timestamp}_summary.txt")
        
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("SUMÁRIO DO EXPERIMENTO: GraphQL vs REST\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de medições: {len(self.results)}\n\n")
            
            for api_type in ["REST", "GraphQL"]:
                f.write(f"\n{api_type}:\n")
                f.write("-" * 70 + "\n")
                
                for query_type in ["simples", "relacionamentos", "filtros", "paginacao"]:
                    measurements = [
                        r for r in self.results 
                        if r['api_type'] == api_type and r['query_type'] == query_type and r['success']
                    ]
                    
                    if measurements:
                        times = [m['response_time_ms'] for m in measurements]
                        sizes = [m['response_size_bytes'] for m in measurements]
                        
                        f.write(f"\n  {query_type.capitalize()}:\n")
                        f.write(f"    Medições: {len(measurements)}\n")
                        f.write(f"    Tempo médio: {sum(times)/len(times):.2f} ms\n")
                        f.write(f"    Tempo min/max: {min(times):.2f} / {max(times):.2f} ms\n")
                        f.write(f"    Tamanho médio: {sum(sizes)/len(sizes):.2f} bytes\n")
                        f.write(f"    Tamanho min/max: {min(sizes)} / {max(sizes)} bytes\n")
        
        print(f"✓ Sumário salvo em: {summary_filename}")
    
    def close(self):
        self.rest_client.close()
        self.graphql_client.close()


def main():
    print("\n" + "=" * 70)
    print("EXPERIMENTO CONTROLADO: GraphQL vs REST")
    print("Laboratório de Experimentação de Software")
    print("=" * 70)
    
    token = os.getenv("GITHUB_TOKEN")
    
    REPETITIONS = 30
    RANDOMIZE = True
    
    experiment = ExperimentRunner(token)
    
    try:
        experiment.run_full_experiment(repetitions=REPETITIONS, randomize=RANDOMIZE)
        
        experiment.save_results()
        
        print("\n" + "=" * 70)
        print("✓ EXPERIMENTO FINALIZADO COM SUCESSO!")
        print("=" * 70)
        print("\nPróximos passos:")
        print("  1. Revisar os arquivos de resultados no diretório 'results/'")
        print("  2. Executar análise estatística (Sprint 2)")
        print("  3. Criar dashboard de visualização (Sprint 3)")
        
    except KeyboardInterrupt:
        print("\n\n✗ Experimento interrompido pelo usuário")
        print("Salvando resultados parciais...")
        experiment.save_results(filename_prefix="experiment_partial")
    
    except Exception as e:
        print(f"\n✗ Erro durante execução do experimento: {e}")
        print("Salvando resultados parciais...")
        experiment.save_results(filename_prefix="experiment_error")
    
    finally:
        experiment.close()
        print("\n✓ Conexões fechadas. Encerrando...")


if __name__ == "__main__":
    main()

