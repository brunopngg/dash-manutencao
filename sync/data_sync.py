"""
Sincronizador de dados - Google Sheets para Banco de Dados
"""
import pandas as pd
from datetime import datetime
from pathlib import Path

# Importações locais
import sys
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import get_db, MaintenanceRepository
from config import GOOGLE_SHEETS_CONFIG, BASE_DIR


def load_from_csv(csv_path: str = None) -> pd.DataFrame:
    """Carrega dados do CSV local"""
    if csv_path is None:
        csv_path = BASE_DIR / "data" / "manutencao.csv"
    
    df = pd.read_csv(csv_path)
    
    # Renomeia colunas para o padrão do banco
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
    
    # Converte data
    df['data_servico'] = pd.to_datetime(df['data_servico'], format='%d/%m/%Y', errors='coerce')
    df['data_servico'] = df['data_servico'].dt.strftime('%Y-%m-%d')
    
    # Remove linhas sem data ou polo
    df = df.dropna(subset=['data_servico', 'polo'])
    
    return df


def load_from_google_sheets() -> pd.DataFrame:
    """Carrega dados diretamente do Google Sheets"""
    try:
        from google.oauth2.service_account import Credentials
        import gspread
        
        # Autenticação
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CONFIG['credentials_path'],
            scopes=scopes
        )
        
        client = gspread.authorize(creds)
        
        # Abre a planilha
        spreadsheet = client.open_by_key(GOOGLE_SHEETS_CONFIG['spreadsheet_id'])
        worksheet = spreadsheet.worksheet(GOOGLE_SHEETS_CONFIG['sheet_name'])
        
        # Obtém todos os dados
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        print(f"✅ Carregados {len(df)} registros do Google Sheets")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao carregar do Google Sheets: {e}")
        print("💡 Usando CSV local como fallback...")
        return load_from_csv()


def sync_to_database(df: pd.DataFrame, clear_existing: bool = False) -> dict:
    """Sincroniza DataFrame com o banco de dados"""
    db = get_db()
    repo = MaintenanceRepository(db)
    
    # Inicializa schema se necessário
    db.init_schema()
    
    if clear_existing:
        repo.clear_all()
    
    inserted = 0
    skipped = 0
    errors = 0
    
    for _, row in df.iterrows():
        try:
            # Verifica se já existe
            if not clear_existing and repo.check_exists(
                str(row.get('ordem_servico', '')), 
                str(row.get('data_servico', ''))
            ):
                skipped += 1
                continue
            
            repo.insert_service(row.to_dict())
            inserted += 1
            
        except Exception as e:
            errors += 1
            print(f"Erro ao inserir: {e}")
    
    db.close()
    
    result = {
        'inserted': inserted,
        'skipped': skipped,
        'errors': errors,
        'total': len(df),
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n📊 Resultado da sincronização:")
    print(f"   ✅ Inseridos: {inserted}")
    print(f"   ⏭️ Ignorados (duplicados): {skipped}")
    print(f"   ❌ Erros: {errors}")
    
    return result


def sync_from_csv():
    """Sincroniza dados do CSV local"""
    print("🔄 Iniciando sincronização do CSV...")
    df = load_from_csv()
    return sync_to_database(df, clear_existing=True)


def sync_from_sheets():
    """Sincroniza dados do Google Sheets"""
    print("🔄 Iniciando sincronização do Google Sheets...")
    df = load_from_google_sheets()
    return sync_to_database(df, clear_existing=False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sincroniza dados de manutenção')
    parser.add_argument('--source', choices=['csv', 'sheets'], default='csv',
                       help='Fonte dos dados (csv ou sheets)')
    parser.add_argument('--clear', action='store_true',
                       help='Limpa dados existentes antes de inserir')
    
    args = parser.parse_args()
    
    if args.source == 'csv':
        df = load_from_csv()
    else:
        df = load_from_google_sheets()
    
    sync_to_database(df, clear_existing=args.clear)
