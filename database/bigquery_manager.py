"""
Módulo de integração com Google BigQuery
Cria dataset, tabela e sincroniza dados para uso com Looker Studio
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import BIGQUERY_CONFIG, BASE_DIR


class BigQueryManager:
    """Gerenciador de operações no BigQuery"""
    
    def __init__(self):
        self.project_id = BIGQUERY_CONFIG['project_id']
        self.dataset_id = BIGQUERY_CONFIG['dataset']
        self.table_id = BIGQUERY_CONFIG['table']
        self.credentials_path = BIGQUERY_CONFIG['credentials_path']
        self.client = None
        
    def connect(self):
        """Conecta ao BigQuery usando credenciais de serviço"""
        from google.cloud import bigquery
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        
        self.client = bigquery.Client(
            credentials=credentials,
            project=self.project_id
        )
        
        print(f"✅ Conectado ao BigQuery: {self.project_id}")
        return self.client
    
    def create_dataset(self):
        """Cria o dataset se não existir"""
        from google.cloud import bigquery
        
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.client.get_dataset(dataset_ref)
            print(f"📁 Dataset '{self.dataset_id}' já existe")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # ou "southamerica-east1" para São Paulo
            dataset.description = "Dataset de Manutenção - Dashboard"
            
            self.client.create_dataset(dataset, exists_ok=True)
            print(f"✅ Dataset '{self.dataset_id}' criado!")
    
    def create_table(self):
        """Cria a tabela com schema definido"""
        from google.cloud import bigquery
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        schema = [
            bigquery.SchemaField("id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("ordem_servico", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("abrir_am", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("medidor_encontrado", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("medidor_instalado", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("chave_afericao_encontrada", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("chave_afericao_instalada", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tcs_encontrado", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("tcs_instalados", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("troca_caixa", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("polo", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("equipe", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("data_servico", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("horario_inicio", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("horario_fim", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("observacao", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("colaboradora_baixa", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("data_baixa", "DATE", mode="NULLABLE"),
            bigquery.SchemaField("nota", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("am_remanejo", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        ]
        
        try:
            self.client.get_table(table_ref)
            print(f"📋 Tabela '{self.table_id}' já existe")
        except Exception:
            table = bigquery.Table(table_ref, schema=schema)
            table.description = "Serviços de Manutenção"
            
            self.client.create_table(table)
            print(f"✅ Tabela '{self.table_id}' criada!")
    
    def load_from_csv(self, csv_path: str = None) -> pd.DataFrame:
        """Carrega dados do CSV"""
        if csv_path is None:
            csv_path = BASE_DIR / "data" / "manutencao.csv"
        
        df = pd.read_csv(csv_path)
        
        # Renomeia colunas
        column_mapping = {
            'ID': 'ordem_servico',
            'ABRIR_AM': 'abrir_am',
            'MEDIDOR_ENCONTRADO': 'medidor_encontrado',
            'MEDIDOR_INSTALADO': 'medidor_instalado',
            'CHAVE_AFERICAO_ENCONTRADA': 'chave_afericao_encontrada',
            'CHAVE_AFERICAO_INSTALADA': 'chave_afericao_instalada',
            'TCS_ENCONTRADO': 'tcs_encontrado',
            'TCS_INSTALADOS': 'tcs_instalados',
            'TROCA_CAIXA': 'troca_caixa',
            'POLO': 'polo',
            'EQUIPE': 'equipe',
            'DATA_SERVICO': 'data_servico',
            'HORARIO_INICIO': 'horario_inicio',
            'HORARIO_FIM': 'horario_fim',
            'OBSERVACAO': 'observacao',
            'COLABORADORA_BAIXA': 'colaboradora_baixa',
            'DATA_BAIXA': 'data_baixa',
            'NOTA': 'nota',
            'AM_REMANEJO': 'am_remanejo',
        }
        
        df = df.rename(columns=column_mapping)
        
        # Converte datas
        df['data_servico'] = pd.to_datetime(df['data_servico'], format='%d/%m/%Y', errors='coerce')
        df['data_baixa'] = pd.to_datetime(df['data_baixa'], format='%d/%m/%Y', errors='coerce')
        
        # Remove linhas sem data ou polo
        df = df.dropna(subset=['data_servico', 'polo'])
        
        # Adiciona timestamp de criação
        df['created_at'] = datetime.now()
        
        # Adiciona ID sequencial
        df['id'] = range(1, len(df) + 1)
        
        return df
    
    def upload_data(self, df: pd.DataFrame, mode: str = "WRITE_TRUNCATE"):
        """
        Faz upload dos dados para o BigQuery
        
        Args:
            df: DataFrame com os dados
            mode: WRITE_TRUNCATE (substitui), WRITE_APPEND (adiciona), WRITE_EMPTY (só se vazio)
        """
        from google.cloud import bigquery
        
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition=mode,
        )
        
        # Upload
        job = self.client.load_table_from_dataframe(
            df, 
            table_ref, 
            job_config=job_config
        )
        
        job.result()  # Aguarda conclusão
        
        # Verifica resultado
        table = self.client.get_table(table_ref)
        print(f"✅ Upload concluído! {table.num_rows} registros na tabela.")
        
        return table.num_rows
    
    def query(self, sql: str) -> pd.DataFrame:
        """Executa query e retorna DataFrame"""
        return self.client.query(sql).to_dataframe()
    
    def get_daily_summary(self, date: str = None) -> dict:
        """Retorna resumo diário via SQL"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        sql = f"""
        SELECT 
            COUNT(*) as total,
            COUNTIF(polo = 'MARABA') as maraba,
            COUNTIF(polo = 'TUCURUI') as tucurui,
            COUNTIF(polo = 'PARAUAPEBAS') as parauapebas,
            COUNTIF(polo = 'REDENÇÃO') as redencao,
            COUNTIF(colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '') as com_baixa,
            COUNT(DISTINCT equipe) as equipes
        FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
        WHERE data_servico = '{date}'
        """
        
        result = self.query(sql)
        return result.iloc[0].to_dict() if not result.empty else None


def init_bigquery():
    """Inicializa BigQuery: cria dataset e tabela"""
    bq = BigQueryManager()
    bq.connect()
    bq.create_dataset()
    bq.create_table()
    return bq


def sync_to_bigquery(clear: bool = True):
    """Sincroniza dados do CSV para o BigQuery"""
    print("🔄 Iniciando sincronização com BigQuery...")
    
    bq = BigQueryManager()
    bq.connect()
    bq.create_dataset()
    bq.create_table()
    
    # Carrega dados do CSV
    df = bq.load_from_csv()
    print(f"📊 {len(df)} registros carregados do CSV")
    
    # Upload para BigQuery
    mode = "WRITE_TRUNCATE" if clear else "WRITE_APPEND"
    rows = bq.upload_data(df, mode=mode)
    
    print(f"""
╔═══════════════════════════════════════════════════════╗
║           ✅ SINCRONIZAÇÃO CONCLUÍDA!                 ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  📊 Registros sincronizados: {rows:<24}║
║  🗄️  Projeto: {bq.project_id:<32}║
║  📁 Dataset: {bq.dataset_id:<33}║
║  📋 Tabela: {bq.table_id:<34}║
║                                                       ║
║  🔗 Acesse no Looker Studio:                         ║
║     https://lookerstudio.google.com                   ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    return rows


def test_connection():
    """Testa conexão com BigQuery"""
    print("🔍 Testando conexão com BigQuery...")
    
    try:
        bq = BigQueryManager()
        bq.connect()
        
        # Testa query simples
        sql = f"SELECT 1 as test"
        result = bq.query(sql)
        
        if not result.empty:
            print("✅ Conexão com BigQuery OK!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciador BigQuery')
    parser.add_argument('--test', action='store_true', help='Testa conexão')
    parser.add_argument('--init', action='store_true', help='Inicializa dataset e tabela')
    parser.add_argument('--sync', action='store_true', help='Sincroniza dados do CSV')
    parser.add_argument('--query', type=str, help='Executa query SQL')
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.init:
        init_bigquery()
    elif args.sync:
        sync_to_bigquery()
    elif args.query:
        bq = BigQueryManager()
        bq.connect()
        result = bq.query(args.query)
        print(result)
    else:
        parser.print_help()
