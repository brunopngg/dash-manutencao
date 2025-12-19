# 🔧 Dashboard de Manutenção

Sistema completo para gestão e visualização de dados de manutenção com:
- Dashboard interativo (Streamlit)
- Banco de dados (SQLite/PostgreSQL/BigQuery)
- Sincronização automática com Google Sheets
- Relatórios diários comparativos
- Integração com WhatsApp para envio automático

## 📁 Estrutura do Projeto

```
dash/
├── cli.py                    # CLI principal
├── config.py                 # Configurações
├── dashboard.py              # Dashboard Streamlit
├── scheduler.py              # Agendador de tarefas
├── requirements.txt          # Dependências
├── data/
│   └── manutencao.csv        # Dados CSV
├── database/
│   ├── schema.sql            # Schema do banco
│   ├── db_manager.py         # Gerenciador de banco
│   └── manutencao.db         # Banco SQLite (gerado)
├── sync/
│   └── data_sync.py          # Sincronização de dados
├── reports/
│   ├── daily_report.py       # Gerador de relatórios
│   └── report_*.html/.txt    # Relatórios gerados
└── whatsapp/
    └── sender.py             # Integração WhatsApp
```

## 🚀 Instalação

```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt
```

## 📋 Comandos CLI

```bash
# Inicializar banco de dados
python cli.py init

# Sincronizar dados do CSV
python cli.py sync --source csv

# Sincronizar do Google Sheets
python cli.py sync --source sheets

# Gerar relatório
python cli.py report

# Testar envio WhatsApp (sem enviar)
python cli.py whatsapp --test

# Iniciar dashboard
python cli.py dashboard

# Iniciar agendador automático
python cli.py scheduler --daemon

# Executar tarefa agora
python cli.py scheduler --run-now sync
python cli.py scheduler --run-now report
```

## 🖥️ Dashboard

Para iniciar o dashboard:

```bash
python cli.py dashboard
# ou
streamlit run dashboard.py
```

Acesse: http://localhost:8501

## 📊 Looker Studio (BigQuery)

### Configuração BigQuery:

1. Crie um projeto no Google Cloud
2. Ative a API do BigQuery
3. Crie uma conta de serviço e baixe o JSON de credenciais
4. Configure as variáveis de ambiente:

```bash
export GCP_PROJECT_ID="seu-projeto"
export BQ_DATASET="manutencao"
export BQ_TABLE="servicos"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export DB_MODE="bigquery"
```

5. No Looker Studio, conecte ao BigQuery usando o mesmo projeto

### Via Gemini CLI:

```bash
# Instale o Gemini CLI
npm install -g @anthropic-ai/claude-cli

# Use para automatizar
gemini "Crie uma query no BigQuery para buscar os serviços de manutenção de hoje agrupados por polo"
```

## 📱 WhatsApp (Automação)

### Opção 1: Evolution API (Self-hosted)

```bash
# Instale Evolution API via Docker
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=sua-chave \
  atendai/evolution-api
```

Configure em `config.py`:
```python
WHATSAPP_CONFIG = {
    "api_url": "http://localhost:8080",
    "api_key": "sua-chave",
    "instance": "default",
    "group_id": "5511999999999@g.us",  # ID do grupo
}
```

### Opção 2: Z-API (Pago)

1. Crie conta em https://z-api.io
2. Configure as credenciais no `config.py`

## ⏰ Automação às 19h

### Windows (Task Scheduler):

```powershell
# Criar tarefa agendada
schtasks /create /tn "ManutencaoReport" /tr "python C:\Users\c06569285\Desktop\dash\scheduler.py --run-now report" /sc daily /st 19:00
```

### Linux (Cron):

```bash
# Edite o crontab
crontab -e

# Adicione:
0 19 * * * cd /path/to/dash && python scheduler.py --run-now report
```

### Docker (Recomendado):

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "scheduler.py", "--daemon"]
```

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env`:

```env
# Banco de dados
DB_MODE=sqlite  # sqlite, postgres, bigquery

# PostgreSQL (se usar)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=manutencao_db
DB_USER=postgres
DB_PASSWORD=senha

# BigQuery (se usar)
GCP_PROJECT_ID=seu-projeto
BQ_DATASET=manutencao
GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

# WhatsApp
WHATSAPP_API_URL=http://localhost:8080
WHATSAPP_API_KEY=sua-chave
WHATSAPP_INSTANCE=default
WHATSAPP_GROUP_ID=5511999999999@g.us
```

## 📈 Fluxo de Dados

```
┌─────────────────┐     ┌─────────────┐     ┌──────────────┐
│  Google Sheets  │────▶│  Sync Job   │────▶│   Database   │
└─────────────────┘     └─────────────┘     └──────┬───────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                              ▼                    ▼                    ▼
                     ┌────────────────┐   ┌───────────────┐   ┌────────────────┐
                     │   Dashboard    │   │ Looker Studio │   │    Relatório   │
                     │  (Streamlit)   │   │  (BigQuery)   │   │   (WhatsApp)   │
                     └────────────────┘   └───────────────┘   └────────────────┘
```

## 🛠️ Desenvolvimento

```bash
# Rodar testes
python -m pytest tests/

# Verificar código
python -m flake8 .

# Formatar código
python -m black .
```

## 📝 Licença

MIT License
