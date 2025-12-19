"""
Módulo de conexão com banco de dados
Suporta SQLite, PostgreSQL e BigQuery
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

from config import SQLITE_DB, POSTGRES_CONFIG, BIGQUERY_CONFIG, DB_MODE


class DatabaseManager:
    """Gerenciador de banco de dados multi-plataforma"""
    
    def __init__(self, mode: str = None):
        self.mode = mode or DB_MODE
        self.connection = None
        
    def connect(self):
        """Estabelece conexão com o banco"""
        if self.mode == "sqlite":
            self.connection = sqlite3.connect(str(SQLITE_DB))
            self.connection.row_factory = sqlite3.Row
        elif self.mode == "postgres":
            import psycopg2
            self.connection = psycopg2.connect(**POSTGRES_CONFIG)
        elif self.mode == "bigquery":
            from google.cloud import bigquery
            self.connection = bigquery.Client()
        return self.connection
    
    def close(self):
        """Fecha conexão"""
        if self.connection and self.mode != "bigquery":
            self.connection.close()
            
    def execute(self, query: str, params: tuple = None):
        """Executa query"""
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        """Busca todos os registros"""
        cursor = self.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Busca um registro"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def init_schema(self):
        """Inicializa o schema do banco"""
        schema_path = SQLITE_DB.parent / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        # Adapta para SQLite se necessário
        if self.mode == "sqlite":
            schema = schema.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            schema = schema.replace("IF NOT EXISTS ", "")
        
        # Executa cada statement separadamente
        for statement in schema.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    self.execute(statement)
                except Exception as e:
                    print(f"Aviso ao executar statement: {e}")
        
        print("✅ Schema inicializado com sucesso!")


class MaintenanceRepository:
    """Repositório de dados de manutenção"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        
    def insert_service(self, data: Dict[str, Any]) -> int:
        """Insere um serviço de manutenção"""
        query = """
        INSERT INTO manutencao (
            ordem_servico, abrir_am, medidor_encontrado, medidor_instalado,
            chave_afericao_encontrada, chave_afericao_instalada,
            tcs_encontrado, tcs_instalados, troca_caixa,
            polo, equipe, data_servico, horario_inicio, horario_fim,
            observacao, colaboradora_baixa, data_baixa, nota, am_remanejo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('ordem_servico'),
            data.get('abrir_am'),
            data.get('medidor_encontrado'),
            data.get('medidor_instalado'),
            data.get('chave_afericao_encontrada'),
            data.get('chave_afericao_instalada'),
            data.get('tcs_encontrado'),
            data.get('tcs_instalados'),
            data.get('troca_caixa'),
            data.get('polo'),
            data.get('equipe'),
            data.get('data_servico'),
            data.get('horario_inicio'),
            data.get('horario_fim'),
            data.get('observacao'),
            data.get('colaboradora_baixa'),
            data.get('data_baixa'),
            data.get('nota'),
            data.get('am_remanejo'),
        )
        cursor = self.db.execute(query, params)
        return cursor.lastrowid
    
    def bulk_insert(self, df: pd.DataFrame) -> int:
        """Insere múltiplos registros de um DataFrame"""
        count = 0
        for _, row in df.iterrows():
            try:
                self.insert_service(row.to_dict())
                count += 1
            except Exception as e:
                print(f"Erro ao inserir registro: {e}")
        return count
    
    def get_services_by_date(self, date: str) -> List[Dict]:
        """Busca serviços por data"""
        query = "SELECT * FROM manutencao WHERE data_servico = ?"
        return self.db.fetch_all(query, (date,))
    
    def get_services_by_polo(self, polo: str) -> List[Dict]:
        """Busca serviços por polo"""
        query = "SELECT * FROM manutencao WHERE polo = ?"
        return self.db.fetch_all(query, (polo,))
    
    def get_daily_summary(self, date: str) -> Dict:
        """Retorna resumo diário"""
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN polo = 'MARABA' THEN 1 ELSE 0 END) as maraba,
            SUM(CASE WHEN polo = 'TUCURUI' THEN 1 ELSE 0 END) as tucurui,
            SUM(CASE WHEN polo = 'PARAUAPEBAS' THEN 1 ELSE 0 END) as parauapebas,
            SUM(CASE WHEN polo = 'REDENÇÃO' THEN 1 ELSE 0 END) as redencao,
            SUM(CASE WHEN colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '' THEN 1 ELSE 0 END) as com_baixa,
            COUNT(DISTINCT equipe) as equipes
        FROM manutencao 
        WHERE data_servico = ?
        """
        return self.db.fetch_one(query, (date,))
    
    def get_comparison(self, date1: str, date2: str) -> Dict:
        """Compara dois dias"""
        summary1 = self.get_daily_summary(date1)
        summary2 = self.get_daily_summary(date2)
        
        if not summary1 or not summary2:
            return None
            
        return {
            'data_atual': date1,
            'data_anterior': date2,
            'atual': summary1,
            'anterior': summary2,
            'diferenca': {
                'total': (summary1['total'] or 0) - (summary2['total'] or 0),
                'maraba': (summary1['maraba'] or 0) - (summary2['maraba'] or 0),
                'tucurui': (summary1['tucurui'] or 0) - (summary2['tucurui'] or 0),
                'parauapebas': (summary1['parauapebas'] or 0) - (summary2['parauapebas'] or 0),
                'redencao': (summary1['redencao'] or 0) - (summary2['redencao'] or 0),
            }
        }
    
    def clear_all(self):
        """Limpa todos os registros (use com cuidado)"""
        self.db.execute("DELETE FROM manutencao")
        print("⚠️ Todos os registros foram removidos!")
    
    def check_exists(self, ordem_servico: str, data_servico: str) -> bool:
        """Verifica se registro já existe"""
        query = "SELECT 1 FROM manutencao WHERE ordem_servico = ? AND data_servico = ?"
        result = self.db.fetch_one(query, (ordem_servico, data_servico))
        return result is not None


def get_db() -> DatabaseManager:
    """Factory para obter instância do banco"""
    db = DatabaseManager()
    db.connect()
    return db


def init_database():
    """Inicializa o banco de dados"""
    db = get_db()
    db.init_schema()
    db.close()
    print("✅ Banco de dados inicializado!")


if __name__ == "__main__":
    init_database()
