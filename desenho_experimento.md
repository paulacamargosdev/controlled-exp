# Desenho do Experimento: GraphQL vs REST

## Laboratório 05 - Sprint 1

**Disciplina:** Laboratório de Experimentação de Software
**Data:** 30/11/2025

---

## 1. Objetivo

Realizar um experimento controlado para avaliar quantitativamente os benefícios da adoção de uma API GraphQL em comparação com uma API REST.

## 2. Perguntas de Pesquisa

**RQ1:** Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?

**RQ2:** Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

---

## A. Hipóteses

### Para RQ1 (Tempo de Resposta):

**H0₁ (Hipótese Nula):** Não há diferença significativa no tempo de resposta entre consultas GraphQL e consultas REST.

- μ_GraphQL = μ_REST

**H1₁ (Hipótese Alternativa):** Consultas GraphQL apresentam tempo de resposta significativamente menor que consultas REST.

- μ_GraphQL < μ_REST

### Para RQ2 (Tamanho da Resposta):

**H0₂ (Hipótese Nula):** Não há diferença significativa no tamanho da resposta entre consultas GraphQL e consultas REST.

- μ_GraphQL = μ_REST

**H1₂ (Hipótese Alternativa):** Consultas GraphQL apresentam tamanho de resposta significativamente menor que consultas REST.

- μ_GraphQL < μ_REST

---

## B. Variáveis Dependentes

As variáveis dependentes são as métricas que serão medidas durante o experimento:

1. **Tempo de Resposta (ms):** Tempo decorrido desde o envio da requisição até o recebimento completo da resposta.

   - Unidade: milissegundos (ms)
   - Método de coleta: Medição programática usando bibliotecas de timing (time.perf_counter())
2. **Tamanho da Resposta (bytes):** Tamanho total do payload de resposta retornado pela API.

   - Unidade: bytes
   - Método de coleta: Medição do tamanho do conteúdo da resposta HTTP (len(response.content))

---

## C. Variáveis Independentes

As variáveis independentes são aquelas que serão manipuladas/controladas durante o experimento:

1. **Tipo de API (Tratamento Principal):**

   - REST
   - GraphQL
2. **Tipo de Consulta (Fator de Bloco):**

   - Consulta simples (1 entidade)
   - Consulta com relacionamentos (múltiplas entidades)
   - Consulta com filtros
   - Consulta com paginação

---

## D. Tratamentos

Os tratamentos são as diferentes combinações das variáveis independentes que serão aplicadas:

**T1 - REST com consultas simples:** Requisições REST para obter dados de uma única entidade

**T2 - GraphQL com consultas simples:** Requisições GraphQL equivalentes para obter os mesmos dados

**T3 - REST com relacionamentos:** Requisições REST que requerem múltiplos endpoints para obter dados relacionados (over-fetching)

**T4 - GraphQL com relacionamentos:** Requisições GraphQL que obtêm dados relacionados em uma única query

**T5 - REST com filtros:** Requisições REST com parâmetros de filtro

**T6 - GraphQL com filtros:** Requisições GraphQL equivalentes com filtros

**T7 - REST com paginação:** Requisições REST com paginação de resultados

**T8 - GraphQL com paginação:** Requisições GraphQL equivalentes com paginação

---

## E. Objetos Experimentais

Para garantir a comparabilidade e permitir a replicação do experimento, utilizaremos APIs públicas que oferecem ambas as interfaces (REST e GraphQL):

### API Selecionada: GitHub API

**Justificativa:**

- Disponibiliza versões REST v3 e GraphQL v4
- Bem documentada
- Alta disponibilidade
- Dados reais e consistentes
- Permite consultas de diferentes complexidades

### Consultas Específicas a Serem Executadas:

1. **Consulta Simples:**

   - REST: GET /users/{username}
   - GraphQL: query { user(login: "{username}") { ... } }
2. **Consulta com Relacionamentos:**

   - REST: GET /users/{username} + GET /users/{username}/repos
   - GraphQL: query { user(login: "{username}") { repositories { ... } } }
3. **Consulta com Filtros:**

   - REST: GET /search/repositories?q=language:python
   - GraphQL: query { search(query: "language:python", type: REPOSITORY) { ... } }
4. **Consulta com Paginação:**

   - REST: GET /users/{username}/repos?per_page=10&page=1
   - GraphQL: query { user(login: "{username}") { repositories(first: 10) { ... } } }

### API Alternativa: SpaceX API

Caso necessário, podemos utilizar a SpaceX API como objeto experimental adicional:

- REST: https://api.spacexdata.com/v4/
- GraphQL: https://api.spacex.land/graphql/

---

## F. Tipo de Projeto Experimental

**Projeto Experimental Selecionado:** Experimento Fatorial Completo 2×4

- **Fator 1:** Tipo de API (2 níveis: REST, GraphQL)
- **Fator 2:** Tipo de Consulta (4 níveis: simples, relacionamentos, filtros, paginação)

**Características:**

- Balanceado: Cada combinação de tratamento receberá o mesmo número de medições
- Randomizado: A ordem de execução dos tratamentos será aleatorizada para evitar efeitos de ordem
- Com repetições: Múltiplas medições para cada combinação de tratamento

**Design:**

- 2 tipos de API × 4 tipos de consulta = 8 combinações de tratamento
- Cada combinação será executada N vezes (ver próxima seção)
- Total de medições: 8 × N

---

## G. Quantidade de Medições

**Medições por Tratamento:** 30 repetições

**Justificativa:**

- n ≥ 30 permite o uso do Teorema do Limite Central
- Permite aplicação de testes paramétricos (t-test, ANOVA)
- Fornece poder estatístico adequado para detectar diferenças significativas
- É prático em termos de tempo de execução (evita limitações de rate limit)

**Total de Medições no Experimento:**

- 8 tratamentos × 30 repetições = 240 medições totais

**Estratégia de Coleta:**

- Intervalo entre requisições: 1 segundo (para evitar rate limiting)
- Randomização da ordem de execução
- Coleta em condições de rede estáveis
- Múltiplas sessões de coleta para validação

---

## H. Ameaças à Validade

### Validade Interna

**Ameaças Identificadas:**

1. **Variabilidade da Rede:**

   - Latência de rede pode variar entre medições
   - **Mitigação:** Realizar múltiplas medições (n=30), executar em horários consistentes, usar conexão estável
2. **Cache do Servidor/Cliente:**

   - Respostas podem ser servidas de cache, distorcendo os resultados
   - **Mitigação:** Alternar consultas, usar headers no-cache, esperar intervalo entre requisições
3. **Rate Limiting:**

   - APIs podem limitar taxa de requisições
   - **Mitigação:** Intervalo de 1s entre requisições, usar autenticação (aumenta limite)
4. **Carga do Servidor:**

   - Variação na carga dos servidores da API ao longo do tempo
   - **Mitigação:** Randomizar ordem de execução, distribuir coleta ao longo do tempo
5. **Ambiente de Execução:**

   - Outros processos na máquina podem afetar medições
   - **Mitigação:** Executar em ambiente controlado, minimizar processos concorrentes

### Validade Externa

**Ameaças Identificadas:**

1. **Generalização para Outras APIs:**

   - Resultados podem ser específicos para a API do GitHub
   - **Mitigação:** Documentar características específicas, considerar usar API adicional (SpaceX)
2. **Tipos de Consulta Limitados:**

   - Não cobre todos os padrões possíveis de uso
   - **Mitigação:** Selecionar consultas representativas dos casos mais comuns
3. **Contexto de Uso:**

   - Experimento não considera fatores como facilidade de desenvolvimento, manutenibilidade
   - **Mitigação:** Documentar escopo limitado às métricas de desempenho e tamanho

### Validade de Construto

**Ameaças Identificadas:**

1. **Métricas Incompletas:**

   - Tempo e tamanho não capturam toda a complexidade da comparação
   - **Mitigação:** Reconhecer limitações no relatório
2. **Equivalência de Consultas:**

   - Garantir que consultas REST e GraphQL retornam dados equivalentes
   - **Mitigação:** Validar estrutura e conteúdo das respostas antes do experimento

### Validade de Conclusão

**Ameaças Identificadas:**

1. **Poder Estatístico Insuficiente:**

   - Número de medições pode não ser suficiente para detectar pequenas diferenças
   - **Mitigação:** n=30 fornece poder adequado para efeitos de tamanho médio
2. **Violação de Premissas Estatísticas:**

   - Dados podem não seguir distribuição normal ou ter variâncias desiguais
   - **Mitigação:** Verificar premissas, usar testes não-paramétricos se necessário (Mann-Whitney U, Kruskal-Wallis)

---

## 3. Análise Estatística Planejada

### Testes Estatísticos:

**Para RQ1 e RQ2 (comparação entre REST e GraphQL):**

- Teste t de Student independente (se premissas atendidas)
- Teste de Mann-Whitney U (alternativa não-paramétrica)
- Nível de significância: α = 0.05

**Análise Adicional:**

- ANOVA bidirecional (tipo de API × tipo de consulta)
- Testes post-hoc (Tukey HSD) se ANOVA significativa
- Cálculo de tamanho de efeito (Cohen's d)
- Intervalos de confiança (95%)

### Visualizações Planejadas:

- Box plots para comparação de distribuições
- Gráficos de barras com intervalos de confiança
- Gráficos de dispersão para análise de correlação
- Histogramas para verificação de normalidade

---

## 4. Cronograma de Execução

**Sprint 1 (Atual):**

- ✓ Desenho do experimento
- ✓ Preparação de scripts de coleta
- ✓ Validação das consultas

**Sprint 2:**

- Execução do experimento (coleta de dados)
- Análise estatística dos resultados
- Elaboração do relatório final

**Sprint 3:**

- Criação do dashboard de visualização
- Refinamento das análises

---

## Referências

- GitHub REST API Documentation: https://docs.github.com/en/rest
- GitHub GraphQL API Documentation: https://docs.github.com/en/graphql
- SpaceX REST API: https://github.com/r-spacex/SpaceX-API
- SpaceX GraphQL API: https://github.com/spacexland/api
