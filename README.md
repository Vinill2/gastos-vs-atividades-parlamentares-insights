# Câmara Legislativo ETL

Pipeline de engenharia de dados que extrai, transforma e carrega dados públicos da Câmara dos Deputados Brasileira para o Google BigQuery.

## 📋 Problema e Objetivo

A Câmara dos Deputados disponibiliza dados abertos sobre proposições, autores, temas, gastos parlamentares e deputados. Este projeto automatiza a ingestão, transformação e armazenamento desses dados em um data warehouse, criando uma base consolidada para análises sobre o comportamento legislativo.

**Perguntas que esse projeto responde:**
- Qual é o perfil de gastos de cada deputado?
- Quais são os temas mais debatidos no legislativo?
- Qual é a distribuição de proposições por partido e estado?
- Qual é o padrão de tramitação das proposições?

## 🏗️ Arquitetura

```
┌─────────────────────────┐
│  API Dados Abertos      │
│  Câmara dos Deputados   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Download (CSV/ZIP)     │
│  requests + zipfile     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Transform              │
│  pandas + validações    │
│  (tipos, nulos, IDs)    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  BigQuery               │
│  5 tabelas              │
│  (schemas validados)    │
└─────────────────────────┘
```

## 🛠️ Stack Técnico

| Componente | Ferramenta |
|-----------|-----------|
| **Orquestração** | Prefect 2.x |
| **Processamento** | pandas, pandas-gbq |
| **Cloud** | Google BigQuery, Google Cloud Storage |
| **Linguagem** | Python 3.10+ |
| **Controle de versão** | Git + GitHub |

## 📊 Dados

O pipeline processa **5 datasets** da Câmara:

| Dataset | Descrição | Frequência |
|---------|-----------|-----------|
| **proposicoes** | Proposições legislativas com status e tramitação | Anual |
| **proposicoes_autores** | Autores das proposições (deputados/blocos) | Anual |
| **proposicoes_temas** | Temas associados às proposições com relevância | Anual |
| **gastos_parlamentares** | Despesas com cota parlamentar | Anual |
| **deputados** | Dados cadastrais dos deputados | Sem versionamento (atualizado) |

## 🚀 Como Rodar

### Pré-requisitos

- Python 3.10+
- Conta no Google Cloud com BigQuery habilitado
- Service Account com credenciais JSON

### 1. Configuração inicial

Clone o repositório:
```bash
git clone <seu-repo>
cd legislativo_etl
```

Crie um ambiente virtual:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

Preencha com seus valores:
```bash
# .env
GOOGLE_APPLICATION_CREDENTIALS=./gcp/credenciais.json
BQ_PROJECT=seu-projeto-gcp
BQ_DATASET=desafio_legislativo_2026
DADOS_DIR=./data/camara_leg_csv
URL_BASE=https://dadosabertos.camara.leg.br/arquivos
```

Coloque o JSON das credenciais do Google Cloud em `gcp/credenciais.json`.

### 3. Executar o pipeline

**Localmente (sem Prefect UI):**
```bash
cd tasks
python main_prefect.py
```

**Com Prefect (recomendado para desenvolvimento):**
```bash
cd tasks
prefect server start  # em outro terminal
python main_prefect.py
# Acesse http://localhost:4200 para ver a UI
```

**Especificar ano:**
```bash
# Por padrão, roda para 2026
# Para mudar, edite o ano em main_prefect.py ou use variáveis de ambiente
```

### 4. Rodar testes

```bash
pytest tests/ -v
```

Com cobertura:
```bash
pytest tests/ --cov=scripts --cov-report=html
```

## 📁 Estrutura do Projeto

```
legislativo_etl/
├── tasks/
│   ├── main_prefect.py              # Flow principal (orquestração)
│   └── scripts/
│       ├── __init__.py
│       ├── config.py                # Configuração dos datasets
│       ├── download.py              # Download de arquivos
│       ├── pipeline.py              # Funções de extract e load
│       ├── schemas.py               # Esquemas BigQuery
│       ├── steps_transform.py       # Definição das etapas
│       └── transform.py             # Funções de transformação
├── tests/
│   ├── __init__.py
│   └── test_transform.py            # Testes das transformações
├── gcp/
│   └── credenciais.json             # (gitignored)
├── data/                            # CSVs baixados (gitignored)
├── .env                             # Variáveis locais (gitignored)
├── .env.example                     # Modelo de variáveis
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔄 Fluxo de Dados

### Etapas do Pipeline

1. **Download** (`download.py`)
   - Baixa CSVs da API ou descompacta ZIPs
   - Valida se arquivo foi criado e não está vazio

2. **Extract** (`pipeline.py::extrair`)
   - Lê CSV com pandas (separador `;`)
   - Valida se dataframe não está vazio

3. **Transform** (`transform.py`)
   - **Seleção**: escolhe colunas relevantes
   - **Conversão de tipos**: datas, datetimes, números, decimais
   - **Normalização**: trata nulos, extrai IDs de URIs
   - Cada dataset tem suas transformações específicas (em `steps_transform.py`)

4. **Load** (`pipeline.py::carregar_bigquery`)
   - Carrega no BigQuery com schema validado
   - Modo `replace` (sobrescreve tabela inteira)

### Exemplo de Transformação

```python
# Entrada: proposicoes_temas (com URI como string)
uriProposicao,tema,relevancia
http://...camara.leg.br/proposicoes/123,Saúde,0.95
http://...camara.leg.br/proposicoes/456,Educação,0.87

# Saída (após transform)
uriProposicao,tema,relevancia,id
http://...camara.leg.br/proposicoes/123,Saúde,0.95,123
http://...camara.leg.br/proposicoes/456,Educação,0.87,456
```

## 🎯 Decisões Técnicas

### 1. Configuração Declarativa
Os datasets são configurados em `config.py` com URLs, caminhos, schemas e transformações. Isso permite adicionar novos datasets sem alterar a lógica do flow.

### 2. Modo `replace` no BigQuery
Cada execução sobrescreve a tabela inteira. **Alternativas futuras:**
- Append com coluna `ano` para manter histórico
- Particionamento por data
- Merge incremental (upsert)

### 3. Transformações Reutilizáveis
Funções genéricas (`converter_data`, `normalizar_nulos`, etc.) são compostas em pipelines por dataset. Facilita testes e manutenção.

### 4. Logs no Prefect
Usa `get_run_logger()` para exibir progresso na UI do Prefect, essencial para monitoramento em produção.

### 5. Validações em Camadas
- **Download**: verifica se arquivo existe e não está vazio
- **Extract**: valida se dataframe não está vazio
- **Transform**: converte tipos com `errors="coerce"` (NaN em caso de erro)
- **Load**: schema do BigQuery força tipos

## 📈 Próximos Passos

### Curto prazo (Diferencial no portfolio)
- [ ] **Testes expandidos** (Parte 4)
  - Cobertura > 80% com pytest
  - CI/CD no GitHub Actions
- [ ] **Dashboard Looker Studio** (Parte 6)
  - Análises dos dados
  - Gastos por deputado, temas mais frequentes

### Médio prazo
- [ ] **Agendamento** (Parte 7)
  - Cron diário no Prefect
- [ ] **Containerização** (Parte 8)
  - Dockerfile para reprodutibilidade
- [ ] **Modelo de dados** com dbt
  - Camada de staging e marts
  - Documentação automática

### Longo prazo
- [ ] Incremental loading (não sobrescrever tudo)
- [ ] Data quality checks com Great Expectations
- [ ] Alertas de falha (Slack, email)
- [ ] Versionamento de dados

## 🐛 Troubleshooting

### Erro: `FileNotFoundError` ao baixar
- Verifique se a URL em `config.py` ainda é válida
- A API da Câmara pode ter mudado o endpoint

### Erro: `PermissionError` no BigQuery
- Confirme que a service account tem role `BigQuery Data Editor`
- Verifique se `GOOGLE_APPLICATION_CREDENTIALS` aponta pro JSON correto

### Erro: `MissingContextError` nos testes
- O `get_run_logger()` só funciona dentro de um Prefect flow/task
- Use o try/except sugerido em `transform.py` para rodar testes

### CSV vazio após download
- Confirme a URL em `config.py`
- Teste manualmente: `requests.get(url).status_code`

## 📚 Referências

- [Dados Abertos Câmara](https://dadosabertos.camara.leg.br/)
- [Prefect Docs](https://docs.prefect.io/)
- [pandas-gbq](https://pandas-gbq.readthedocs.io/)
- [Google BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/)

## 📝 Licença

MIT License - veja `LICENSE` (se aplicável)

---

**Autor:** [Seu Nome]  
**Última atualização:** Setembro 2026