import requests
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

# URL do Google Sheets (exportar como CSV)
GOOGLE_SHEETS_URL = 'https://docs.google.com/spreadsheets/d/1LChFOFxxBUY4hpQz2K4lZS6oC-NVhIBAqgCVYyKZZHw/export?format=csv&gid=0'

# Mapeamento para normalizar POLO
MAPEAMENTO_POLO = {
    'MARABA': 'MARABÁ',
    'MARABÃ': 'MARABÁ',
    'CANAA': 'CANAÃ',
    'JACUNDA': 'JACUNDÁ',
    'JACUNDÃ': 'JACUNDÁ',
    'TUCURUI': 'TUCURUÍ',
    'TUCURUÃ': 'TUCURUÍ',
    'REDENÃÃO': 'REDENÇÃO',
    'REDENCAO': 'REDENÇÃO',
    'REDEÃÃO': 'REDENÇÃO',
}


def baixar_dados():
    """Baixa os dados do Google Sheets"""
    print("📥 Baixando dados do Google Sheets...")
    response = requests.get(GOOGLE_SHEETS_URL)
    response.raise_for_status()
    
    df = pd.read_csv(StringIO(response.text), encoding='utf-8')
    
    # Normalizar nomes das colunas (remover caracteres especiais)
    df.columns = df.columns.str.strip()
    
    print(f"✅ {len(df)} registros baixados")
    return df


def encontrar_coluna(df, possiveis_nomes):
    """Encontra uma coluna mesmo com encoding diferente"""
    for col in df.columns:
        # Normaliza removendo caracteres estranhos
        col_limpo = col.encode('ascii', 'ignore').decode('ascii').upper().strip()
        for nome in possiveis_nomes:
            nome_limpo = nome.upper().strip()
            if nome_limpo in col_limpo or col_limpo in nome_limpo:
                return col
            # Também verifica se contém a palavra principal
            palavras_nome = nome_limpo.split()
            if len(palavras_nome) > 0 and palavras_nome[0] in col_limpo:
                return col
    return None


def processar_dados(df):
    """Processa e normaliza os dados"""
    # Encontrar colunas com nomes que podem ter encoding diferente
    col_polo = encontrar_coluna(df, ['POLO'])
    col_equipe = encontrar_coluna(df, ['EQUIPE'])
    col_data = encontrar_coluna(df, ['DATA DO SERVICO', 'DATA DO SERVIÇO', 'DATA SERVICO'])
    col_baixa = encontrar_coluna(df, ['COLABORADORA', 'BAIXA'])
    
    print(f"📊 Colunas encontradas: POLO={col_polo}, EQUIPE={col_equipe}, DATA={col_data}")
    
    # Normalizar POLO
    if col_polo:
        df['POLO'] = df[col_polo].astype(str).str.strip().str.upper()
        df['POLO'] = df['POLO'].replace(MAPEAMENTO_POLO)
    
    # Normalizar EQUIPE
    if col_equipe:
        df['EQUIPE'] = df[col_equipe].astype(str).str.strip().str.upper().str.replace(r'\s+', '', regex=True)
    
    # Processar data
    if col_data:
        df['DATA_SERVICO'] = pd.to_datetime(df[col_data], format='%d/%m/%Y', errors='coerce')
        df['ANO'] = df['DATA_SERVICO'].dt.year
        df['MES'] = df['DATA_SERVICO'].dt.month
    
    # Guardar referência para coluna de baixa
    if col_baixa:
        df['TEM_BAIXA'] = df[col_baixa].notna() & (df[col_baixa].astype(str).str.strip() != '')
    
    # Filtrar dados válidos
    df = df[df['DATA_SERVICO'].notna() & df['POLO'].notna() & (df['ANO'] <= 2026)]
    
    return df


def gerar_relatorio():
    """Gera o mini relatório para WhatsApp"""
    df = baixar_dados()
    df = processar_dados(df)
    
    hoje = datetime.now()
    
    # Meses em português
    MESES_PT = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
        5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
        9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    nome_mes = MESES_PT[hoje.month]
    
    # Dados do mês atual
    mes_atual = df[(df['ANO'] == hoje.year) & (df['MES'] == hoje.month)]
    
    # Dados de hoje
    dados_hoje = df[df['DATA_SERVICO'].dt.date == hoje.date()]
    
    # Dados de ontem
    ontem = hoje - timedelta(days=1)
    dados_ontem = df[df['DATA_SERVICO'].dt.date == ontem.date()]
    
    # KPIs
    total_geral = len(df)
    total_mes = len(mes_atual)
    total_hoje = len(dados_hoje)
    total_ontem = len(dados_ontem)
    
    # Top 3 polos do mês
    top_polos = mes_atual['POLO'].value_counts().head(3)
    
    # Top 3 equipes do mês
    top_equipes = mes_atual['EQUIPE'].value_counts().head(3)
    
    # Variação hoje vs ontem
    if total_ontem > 0:
        variacao = ((total_hoje - total_ontem) / total_ontem) * 100
        emoji_var = "📈" if variacao >= 0 else "📉"
        texto_var = f"{emoji_var} {variacao:+.1f}% vs ontem"
    else:
        texto_var = "📊 Sem dados de ontem"
    
    # Montar mensagem
    msg = f"""🔧 *MANUTENÇÃO - RELATÓRIO DIÁRIO*
📅 {hoje.strftime('%d/%m/%Y')} às {hoje.strftime('%H:%M')}

━━━━━━━━━━━━━━━━━━━━
📊 *RESUMO DO DIA*
━━━━━━━━━━━━━━━━━━━━
• Serviços hoje: *{total_hoje}*
• Serviços ontem: *{total_ontem}*
• {texto_var}

━━━━━━━━━━━━━━━━━━━━
📈 *ACUMULADO {nome_mes}*
━━━━━━━━━━━━━━━━━━━━
• Total do mês: *{total_mes}*
• Total geral: *{total_geral}*

━━━━━━━━━━━━━━━━━━━━
🏆 *TOP 3 POLOS (MÊS)*
━━━━━━━━━━━━━━━━━━━━"""
    
    for i, (polo, qtd) in enumerate(top_polos.items(), 1):
        medalha = ["🥇", "🥈", "🥉"][i-1]
        msg += f"\n{medalha} {polo}: *{qtd}*"
    
    msg += """

━━━━━━━━━━━━━━━━━━━━
👥 *TOP 3 EQUIPES (MÊS)*
━━━━━━━━━━━━━━━━━━━━"""
    
    for i, (equipe, qtd) in enumerate(top_equipes.items(), 1):
        medalha = ["🥇", "🥈", "🥉"][i-1]
        msg += f"\n{medalha} {equipe}: *{qtd}*"
    
    msg += """

━━━━━━━━━━━━━━━━━━━━
🔗 *Dashboard completo:*
https://dash-manutencao.vercel.app/manutencao
━━━━━━━━━━━━━━━━━━━━"""
    
    return msg


if __name__ == "__main__":
    relatorio = gerar_relatorio()
    print(relatorio)
