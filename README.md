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

## Análise do Dashboard: GraphQL vs REST

### Visão Geral

Este dashboard apresenta os resultados do experimento controlado comparando as APIs **GraphQL** e **REST** da GitHub, com foco em duas métricas principais: **tempo de resposta** (RQ1) e **tamanho do payload** (RQ2).

---

🔗 [Acessar Dashboard no Power BI](https://app.powerbi.com/groups/me/reports/561994c6-4e70-4e75-9198-237e00e56bc6/dcf38ea6cbc2a1c3d836?experience=power-bi)

### KPIs Principais (Cartões Superiores)

#### 1. Total de Requisições: **240**
- Representa o total de medições realizadas no experimento
- Distribuídas igualmente entre REST e GraphQL (120 cada)
- 30 repetições para cada um dos 8 tratamentos (2 APIs × 4 tipos de consulta)

#### 2. Taxa de Sucesso: **1,00** (100%)
- Todas as 240 requisições foram executadas com sucesso
- Não houve falhas ou erros durante a execução do experimento
- Indica alta confiabilidade dos dados coletados

#### 3. Redução Média de Tamanho: **0,93** (93%)
- **Resultado mais significativo do experimento**
- GraphQL reduz em média **93% do tamanho das respostas** em comparação com REST
- Demonstra a eficiência do GraphQL em eliminar over-fetching
- Impacto direto na economia de banda e tráfego de rede

#### 4. Diferença Média de Tempo: **-72,35 ms**
- O valor **negativo** indica que GraphQL é, em média, **72,35 ms mais lento** que REST
- Nota importante: "GraphQL mais lento" destacado no canto superior direito
- Trade-off: GraphQL sacrifica um pouco de velocidade para reduzir drasticamente o tamanho

---

### Gráfico 1: Tempo Médio de Resposta REST vs GraphQL (RQ1)

**Tipo:** Gráfico de linhas  
**Cores:** Azul (REST), Laranja (GraphQL)

#### Análise por Tipo de Consulta:

- **Simples:** Tempos muito próximos entre REST e GraphQL (linhas quase sobrepostas)
- **Relacionamentos:** Comportamento similar, pequena diferença
- **Paginação:** **Maior divergência** - GraphQL apresenta pico significativo, sendo muito mais lento que REST
- **Filtros:** GraphQL apresenta queda acentuada, aproximando-se do desempenho REST

#### Conclusão RQ1:
- GraphQL **não é consistentemente mais rápido** que REST
- Para **paginação**, GraphQL tem desempenho significativamente **inferior**
- Para consultas simples e filtros, as diferenças são menores

---

### Gráfico 2: Redução de Tamanho de Resposta (RQ2)

**Tipo:** Gráfico de linhas com eixo invertido  
**Cores:** Azul (REST - linha superior), Laranja (GraphQL - linha inferior)

#### Análise por Tipo de Consulta:

- **Filtros:** Maior diferença entre as linhas - REST retorna payloads muito maiores
- **Relacionamentos:** Grande separação entre as linhas - GraphQL muito mais eficiente
- **Paginação:** Diferença substancial mantida
- **Simples:** Menor diferença, mas GraphQL ainda é significativamente menor

#### Conclusão RQ2:
- GraphQL apresenta **redução consistente e dramática** no tamanho das respostas
- A linha laranja (GraphQL) permanece **constantemente abaixo** da linha azul (REST)
- Benefício mais evidente em consultas com **filtros** e **relacionamentos**

---

### Gráfico 3: Evolução no Tempo

**Tipo:** Gráfico de linhas temporal  
**Eixo X:** timestamp  
**Cores:** Azul (GraphQL), Laranja (REST)

#### Observações:

- **Padrão de execução em blocos:** Visível pelos picos e vales alternados
- **REST (laranja):** Apresenta picos muito altos (~60 mil) em determinados momentos
- **GraphQL (azul):** Mantém-se consistentemente baixo (~0-5 mil) durante todo o experimento
- **Randomização:** Os blocos alternados indicam a randomização dos tratamentos
- **Estabilidade:** GraphQL mostra comportamento mais estável e previsível

#### Interpretação:
- A diferença visual dramática confirma a **redução de 93% no tamanho** das respostas
- REST apresenta alta variabilidade dependendo do tipo de consulta
- GraphQL mantém payloads consistentemente pequenos

---

### Gráfico 4: Gráfico de Interação - ANOVA

**Tipo:** Gráfico de barras  
**Eixo Y:** Média de sum_sq (soma dos quadrados)

#### Fatores Analisados:

1. **Residual:** Maior barra (~4E+16) - variância não explicada pelos fatores
2. **C(query_type):** Segunda maior barra - tipo de consulta tem impacto significativo
3. **C(api_type):C(query_type):** Interação entre API e tipo de consulta
4. **C(api_type):** Menor barra - tipo de API isoladamente

#### Conclusão Estatística:
- O **tipo de consulta** é o fator que mais contribui para a variância
- Existe **interação significativa** entre tipo de API e tipo de consulta
- Confirma que o desempenho relativo de REST vs GraphQL **depende do cenário**

---

### Tabela: Estatísticas Descritivas por API e Tipo de Consulta

#### Destaques da Tabela:

**GraphQL:**
- **Filtros:** mean_size = 3.635,23 bytes
- **Paginação:** mean_size = 2.813,63 bytes
- **Relacionamentos:** mean_size = 2.893,67 bytes
- **Simples:** mean_size = 414,10 bytes (menor de todos)

**REST:**
- **Filtros:** mean_size = 55.825,77 bytes (**15x maior** que GraphQL)
- **Paginação:** mean_size = 34.868,37 bytes (**12x maior** que GraphQL)
- **Relacionamentos:** mean_size = 50.251,50 bytes (**17x maior** que GraphQL)
- **Simples:** mean_size = 1.246,87 bytes (**3x maior** que GraphQL)

#### Observações Importantes:

- **Consistência:** Todas as consultas têm `count_time = 30` (30 repetições cada)
- **Variabilidade (std_size):** REST apresenta desvio padrão muito maior, indicando maior inconsistência
- **Min/Max:** REST tem ranges muito mais amplos (ex: paginação de 2 a 51.682 bytes)

---

## Principais Conclusões do Dashboard

### Pontos Fortes do GraphQL

1. **Redução massiva de tamanho (93%)** - Benefício consistente em todos os cenários
2. **Previsibilidade** - Menor variabilidade nos tamanhos de resposta
3. **Eficiência de banda** - Ideal para aplicações móveis ou com restrições de rede
4. **Eliminação de over-fetching** - Retorna apenas os dados solicitados

### Trade-offs do GraphQL

1. **Tempo de resposta maior** - Em média 72ms mais lento que REST
2. **Paginação problemática** - Desempenho significativamente inferior em cenários de paginação
3. **Overhead de processamento** - Queries complexas podem ter custo computacional maior

### Recomendações

**Use GraphQL quando:**
- Largura de banda é limitada (mobile, IoT)
- Precisa de flexibilidade nas consultas
- Quer evitar múltiplas requisições REST
- Tamanho do payload é crítico

**Use REST quando:**
- Latência é prioridade absoluta
- Implementa paginação pesada
- Precisa de cache HTTP tradicional
- Simplicidade de implementação é importante

### Validação das Hipóteses

**RQ1 (Tempo de Resposta):**
- **Hipótese rejeitada** - GraphQL não é consistentemente mais rápido
- GraphQL é mais lento, especialmente em paginação

**RQ2 (Tamanho da Resposta):**
- **Hipótese confirmada** - GraphQL tem tamanho significativamente menor
- Redução de 93% é estatisticamente e praticamente significativa

---

## Qualidade do Dashboard

### Pontos Positivos

**Design limpo e profissional** com fundo escuro  
**KPIs bem destacados** no topo para insights rápidos  
**Cores consistentes** (azul para REST, laranja para GraphQL)  
**Múltiplas perspectivas** (tempo, tamanho, evolução temporal, ANOVA)  
**Tabela detalhada** com estatísticas descritivas completas  
**Visualização temporal** mostra a execução do experimento  

### Sugestões de Melhoria

- Adicionar boxplots para visualizar distribuição e outliers
- Incluir testes de significância estatística (p-values) nos gráficos
- Adicionar slicers para filtrar por tipo de consulta
- Criar página separada para cada RQ (RQ1 e RQ2)
- Incluir gráfico de barras para comparação direta de redução percentual por tipo de consulta

<img width="863" height="476" alt="dashboard" src="https://github.com/user-attachments/assets/b4980cb5-06b1-47d6-9b39-7ae9b34955f8" />

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
