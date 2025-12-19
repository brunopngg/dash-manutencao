"""
Configurações do projeto Dashboard Manutenção
"""
import os
from pathlib import Path

# Diretório base
BASE_DIR = Path(__file__).parent

# Configuração do banco de dados
# Opção 1: SQLite (local, para testes)
SQLITE_DB = BASE_DIR / "database" / "manutencao.db"

# Opção 2: PostgreSQL (para produção)
POSTGRES_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "manutencao_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Opção 3: BigQuery (para Looker Studio - RECOMENDADO)
BIGQUERY_CONFIG = {
    "project_id": "meu-projeto-manutencao",
    "dataset": "manutencao",
    "table": "servicos",
    "credentials_path": str(BASE_DIR / "credentials.json"),
}

# Google Sheets (fonte de dados)
GOOGLE_SHEETS_CONFIG = {
    "spreadsheet_id": "1LChFOFxxBUY4hpQz2K4lZS6oC-NVhIBAqgCVYyKZZHw",
    "sheet_name": "MANUTENÇÃO",
    "credentials_path": os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials.json"),
}

# Configuração WhatsApp (Evolution API ou similar)
WHATSAPP_CONFIG = {
    "api_url": os.getenv("WHATSAPP_API_URL", "http://localhost:8080"),
    "api_key": os.getenv("WHATSAPP_API_KEY", ""),
    "instance": os.getenv("WHATSAPP_INSTANCE", "default"),
    "group_id": os.getenv("WHATSAPP_GROUP_ID", ""),  # ID do grupo para enviar
}

# Horário de execução automática
SCHEDULE_CONFIG = {
    "sync_time": "18:30",  # Sincroniza dados
    "report_time": "19:00",  # Envia relatório WhatsApp
}

# Modo do banco (sqlite, postgres, bigquery)
DB_MODE = os.getenv("DB_MODE", "sqlite")
