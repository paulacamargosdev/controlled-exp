# Experimento Controlado: GraphQL vs REST

**Disciplina:** Laboratório de Experimentação de Software
**Instituição:** PUC Minas
**Laboratório:** 05 - GraphQL vs REST - Um experimento controlado

## Descrição

Este projeto implementa um experimento controlado para avaliar quantitativamente os benefícios da adoção de uma API GraphQL em comparação com uma API REST, respondendo às seguintes perguntas de pesquisa:

- **RQ1:** Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?
- **RQ2:** Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

## Objetivo

Realizar medições sistemáticas de tempo de resposta e tamanho de payload em diferentes cenários de consulta (simples, com relacionamentos, com filtros e com paginação) para comparar as duas abordagens de API.

## Estrutura do Projeto

```
controlled-exp/
│
├── desenho_experimento.md      # Documentação completa do desenho experimental
├── rest_client.py               # Cliente para consultas REST (GitHub API v3)
├── graphql_client.py            # Cliente para consultas GraphQL (GitHub API v4)
├── experiment.py                # Script principal de execução do experimento
├── requirements.txt             # Dependências do projeto
├── README.md                    # Este arquivo
│
└── results/                     # Diretório para armazenar resultados
    ├── experiment_YYYYMMDD_HHMMSS.csv
    ├── experiment_YYYYMMDD_HHMMSS.json
    └── experiment_YYYYMMDD_HHMMSS_summary.txt
```

## Configuração do Ambiente

### 1. Pré-requisitos

- Python 3.9 ou superior
- Conta no GitHub
- Token de acesso pessoal do GitHub

### 2. Instalação

Clone o repositório e instale as dependências:

```bash
# Navegue até o diretório do projeto
cd controlled-exp

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Token GitHub

Para executar o experimento, você precisa de um token de acesso pessoal do GitHub:

#### Criando o Token:

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome descritivo (ex: "Experimento Lab05")
4. Selecione as seguintes permissões:
   - ✓ `public_repo` (acesso a repositórios públicos)
   - ✓ `read:user` (leitura de perfil de usuário)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN** (você não poderá vê-lo novamente!)

#### Configurando o Token:

**Crie um arquivo `.env`:**

```
GITHUB_TOKEN=seu_token_aqui
```

## Execução

### Teste dos Clientes

Antes de executar o experimento completo, você pode testar os clientes individualmente:

**Teste do Cliente REST:**

```bash
python rest_client.py
```

**Teste do Cliente GraphQL:**

```bash
python graphql_client.py
```

### Execução do Experimento Completo

```bash
python experiment.py
```

O experimento irá:

1. Executar 8 tratamentos diferentes (4 tipos de consulta × 2 tipos de API)
2. Realizar 30 repetições de cada tratamento (total de 240 medições)
3. Randomizar a ordem de execução para evitar viés
4. Salvar os resultados em formato CSV, JSON e sumário em texto

**Tempo estimado:** Aproximadamente 4-5 minutos (com intervalo de 1s entre requisições para evitar rate limiting)

## Desenho Experimental

### Variáveis

**Variáveis Dependentes (métricas medidas):**

- Tempo de resposta (ms)
- Tamanho da resposta (bytes)

**Variáveis Independentes:**

- Tipo de API: REST vs GraphQL
- Tipo de consulta: simples, relacionamentos, filtros, paginação

### Tratamentos

- **T1/T2:** Consultas simples (REST vs GraphQL)
- **T3/T4:** Consultas com relacionamentos (REST vs GraphQL)
- **T5/T6:** Consultas com filtros (REST vs GraphQL)
- **T7/T8:** Consultas com paginação (REST vs GraphQL)

### Objetos Experimentais

**API Principal:** GitHub API

- REST: GitHub REST API v3 (https://api.github.com)
- GraphQL: GitHub GraphQL API v4 (https://api.github.com/graphql)

### Tipo de Projeto

Experimento Fatorial Completo 2×4:

- 2 níveis de API (REST, GraphQL)
- 4 níveis de tipo de consulta
- 30 repetições por combinação
- Total: 240 medições

### Análise Estatística Planejada

- Teste t de Student (comparação entre REST e GraphQL)
- ANOVA bidirecional (interação tipo de API × tipo de consulta)
- Testes não-paramétricos alternativos (Mann-Whitney U, Kruskal-Wallis)
- Cálculo de tamanho de efeito (Cohen's d)
- Nível de significância: α = 0.05

Consulte `desenho_experimento.md` para detalhes completos do desenho experimental.

## Resultados

Os resultados são salvos automaticamente no diretório `results/` com timestamp:

- **CSV:** Dados brutos para análise estatística
- **JSON:** Dados estruturados para processamento programático
- **TXT:** Sumário com estatísticas descritivas

### Estrutura dos Dados

Cada medição contém:

```json
{
  "timestamp": "2025-11-30T10:30:45.123456",
  "api_type": "REST",
  "query_type": "simples",
  "query_name": "get_user",
  "response_time_ms": 245.67,
  "response_size_bytes": 1234,
  "success": true,
  "error_msg": null
}
```

## Tecnologias Utilizadas

- **Python 3.9+**
- **requests:** Cliente HTTP para REST e GraphQL
- **pandas:** Manipulação de dados (Sprint 2)
- **scipy/statsmodels:** Análise estatística (Sprint 2)
- **matplotlib/seaborn:** Visualização de dados (Sprint 3)

## Referências

- GitHub REST API Documentation: https://docs.github.com/en/rest
- GitHub GraphQL API Documentation: https://docs.github.com/en/graphql
- GraphQL Official: https://graphql.org/
- REST API Design: https://restfulapi.net/
