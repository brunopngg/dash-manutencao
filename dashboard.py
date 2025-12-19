import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import base64

# Cores da paleta Equatorial
AZUL_EQUATORIAL = "#1a4d8f"
AZUL_CLARO = "#2d6bb5"
AZUL_ESCURO = "#0d2e5a"
BRANCO = "#ffffff"
CINZA_CLARO = "#f5f7fa"

# Configuração da página
st.set_page_config(
    page_title="Dashboard Manutenção - Equatorial",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Função para carregar logo como base64
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), 'image.png')
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_base64 = get_logo_base64()

# CSS customizado com cores Equatorial
st.markdown(f"""
<style>
    /* Esconder sidebar por padrão */
    [data-testid="stSidebar"] {{
        display: none;
    }}
    
    /* Header principal */
    .header-container {{
        background: linear-gradient(135deg, {AZUL_ESCURO} 0%, {AZUL_EQUATORIAL} 50%, {AZUL_CLARO} 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 4px 15px rgba(26, 77, 143, 0.3);
    }}
    
    .header-content {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .logo-title {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    
    .logo-title img {{
        height: 50px;
        filter: brightness(0) invert(1);
    }}
    
    .main-title {{
        color: {BRANCO};
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .subtitle {{
        color: rgba(255,255,255,0.8);
        font-size: 0.9rem;
        margin: 0;
    }}
    
    /* Cards de métricas */
    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, {AZUL_EQUATORIAL} 0%, {AZUL_CLARO} 100%);
        padding: 1rem;
        color: {BRANCO};
        box-shadow: 0 4px 10px rgba(26, 77, 143, 0.2);
    }}
    
    [data-testid="stMetric"] label {{
        color: rgba(255,255,255,0.9) !important;
    }}
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {BRANCO} !important;
        font-weight: bold;
    }}
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        color: rgba(255,255,255,0.8) !important;
    }}
    
    /* Subtítulos */
    .stSubheader {{
        color: {AZUL_EQUATORIAL} !important;
        border-bottom: 3px solid {AZUL_EQUATORIAL};
        padding-bottom: 0.5rem;
    }}
    
    /* Filtros no header */
    .filter-container {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        align-items: flex-end;
    }}
    
    /* Estilo dos selectbox */
    .stSelectbox > div > div {{
        background-color: rgba(255,255,255,0.95);
        border: 2px solid {AZUL_EQUATORIAL};
    }}
    
    /* Data input */
    .stDateInput > div > div {{
        border: 2px solid {AZUL_EQUATORIAL};
    }}
    
    /* Expander */
    .streamlit-expanderHeader {{
        background-color: {CINZA_CLARO};
        border: 1px solid {AZUL_EQUATORIAL};
    }}
    
    /* Tabelas */
    .stDataFrame {{
        border: 1px solid {AZUL_EQUATORIAL};
    }}
    
    /* Rodapé */
    .footer {{
        text-align: center;
        color: {AZUL_EQUATORIAL};
        padding: 1rem;
        margin-top: 2rem;
        border-top: 2px solid {AZUL_EQUATORIAL};
    }}
</style>
""", unsafe_allow_html=True)

# Header com logo
if logo_base64:
    header_html = f"""
    <div class="header-container">
        <div class="header-content">
            <div class="logo-title">
                <img src="data:image/png;base64,{logo_base64}" alt="Equatorial">
                <div>
                    <p class="main-title">Dashboard de Manutenção</p>
                    <p class="subtitle">Controle de Serviços e Equipes</p>
                </div>
            </div>
        </div>
    </div>
    """
else:
    header_html = f"""
    <div class="header-container">
        <div class="header-content">
            <div class="logo-title">
                <div>
                    <p class="main-title">⚡ Dashboard de Manutenção</p>
                    <p class="subtitle">Grupo Equatorial - Controle de Serviços</p>
                </div>
            </div>
        </div>
    </div>
    """

st.markdown(header_html, unsafe_allow_html=True)


def get_bigquery_client():
    """Conecta ao BigQuery usando secrets ou arquivo local"""
    from google.cloud import bigquery
    from google.oauth2 import service_account
    
    # Tenta usar secrets do Streamlit Cloud primeiro
    if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        project_id = st.secrets.get("bigquery", {}).get("project_id", "meu-projeto-manutencao")
        return bigquery.Client(credentials=credentials, project=project_id)
    
    # Fallback para arquivo local
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        return bigquery.Client(credentials=credentials, project="meu-projeto-manutencao")
    
    return None


# Carregar dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carrega dados do CSV completo na raiz do projeto"""
    
    # Caminho do CSV completo na raiz
    csv_completo = os.path.join(os.path.dirname(__file__), 'CONTROLE MANUTENÇÃO  -  MANUTENÇÃO .csv')
    
    if os.path.exists(csv_completo):
        try:
            df = pd.read_csv(csv_completo, encoding='utf-8')
        except:
            df = pd.read_csv(csv_completo, encoding='latin-1')
        
        # A primeira coluna é a ordem de serviço (sem nome claro no CSV)
        # Renomear colunas baseado no cabeçalho real
        colunas_originais = df.columns.tolist()
        
        # Mapear colunas
        df = df.rename(columns={
            colunas_originais[0]: 'ORDEM_SERVICO',
            'ABRIR AM ': 'ABRIR_AM',
            'ABRIR AM': 'ABRIR_AM',
            'POLO': 'POLO',
            'EQUIPE': 'EQUIPE',
            'DATA DO SERVIÇO': 'DATA_SERVICO',
            'HORÁRIO INÍCIO': 'HORARIO_INICIO',
            'HORÁRIO FIM': 'HORARIO_FIM',
            'OBSERVAÇÃO': 'OBSERVACAO',
            'COLABORADORA (BAIXA)': 'COLABORADORA_BAIXA',
            'DATA DA BAIXA': 'DATA_BAIXA',
            'MEDIDOR - ENCONTRADO': 'MEDIDOR_ENCONTRADO',
            'MEDIDOR - INSTALADO': 'MEDIDOR_INSTALADO',
            'CHAVE DE AFERIÇÃO ENCONTRADA': 'CHAVE_ENCONTRADA',
            'CHAVE DE AFERIÇÃO INSTALADA': 'CHAVE_INSTALADA',
            'TC´S ENCONTRADO': 'TCS_ENCONTRADO',
            'TC´S INSTALADOS': 'TCS_INSTALADO',
            'TROCA DA CAIXA ': 'TROCA_CAIXA',
            'TROCA DA CAIXA': 'TROCA_CAIXA',
            'NOTA': 'NOTA',
            'AM/REMANEJO': 'AM_REMANEJO',
            'ANEXO': 'ANEXO',
            'OBS': 'OBS_EXTRA',
            'FAIXA': 'FAIXA'
        })
        
        # ========== TRATAMENTO DE DADOS ==========
        # Normalizar POLO - remover acentos, espaços extras e padronizar nomes
        mapeamento_polo = {
            'MARABA': 'MARABÁ',
            'MARABÃ\x81': 'MARABÁ',
            'MARABA ': 'MARABÁ',
            'CANAA': 'CANAÃ',
            'CANAÃ\x83': 'CANAÃ',
            'CANAA ': 'CANAÃ',
            'JACUNDA': 'JACUNDÁ',
            'JACUNDÃ\x81': 'JACUNDÁ',
            'JACUNDA ': 'JACUNDÁ',
            'TUCURUI': 'TUCURUÍ',
            'TUCURUI ': 'TUCURUÍ',
            'TUCURUÃ\x8d': 'TUCURUÍ',
            'REDENÃ\x87Ã\x83O': 'REDENÇÃO',
            'REDENÃ\x87Ã\x83O ': 'REDENÇÃO',
            'REDEÃ\x87Ã\x83O': 'REDENÇÃO',
            'REDENCAO': 'REDENÇÃO',
            'REDENCAO ': 'REDENÇÃO',
            'PARAUAPEBAS ': 'PARAUAPEBAS',
            'XINGUARA ': 'XINGUARA',
        }
        
        # Aplicar tratamento no POLO
        if 'POLO' in df.columns:
            # Primeiro remover espaços extras
            df['POLO'] = df['POLO'].astype(str).str.strip()
            # Aplicar mapeamento
            df['POLO'] = df['POLO'].replace(mapeamento_polo)
            # Para qualquer valor não mapeado, tentar normalizar
            df['POLO'] = df['POLO'].str.upper()
        
        # Normalizar EQUIPE - remover espaços extras
        if 'EQUIPE' in df.columns:
            df['EQUIPE'] = df['EQUIPE'].astype(str).str.strip().str.upper()
            # Padronizar MAB 707 -> MAB707
            df['EQUIPE'] = df['EQUIPE'].str.replace(' ', '', regex=False)
        
        # Normalizar COLABORADORA_BAIXA
        if 'COLABORADORA_BAIXA' in df.columns:
            df['COLABORADORA_BAIXA'] = df['COLABORADORA_BAIXA'].astype(str).str.strip().str.upper()
            df.loc[df['COLABORADORA_BAIXA'] == 'NAN', 'COLABORADORA_BAIXA'] = None
        
        # Converter data
        df['DATA_SERVICO'] = pd.to_datetime(df['DATA_SERVICO'], format='%d/%m/%Y', errors='coerce')
        df['DATA_BAIXA'] = pd.to_datetime(df['DATA_BAIXA'], format='%d/%m/%Y', errors='coerce')
        
        # Limpar dados vazios
        df = df.dropna(subset=['DATA_SERVICO', 'POLO'])
        
        return df
    
    # Fallback para data/manutencao.csv
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'manutencao.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['DATA_SERVICO'] = pd.to_datetime(df['DATA_SERVICO'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['DATA_SERVICO', 'POLO'])
        return df
    
    st.error("Nenhuma fonte de dados disponível!")
    return pd.DataFrame()


df = load_data()

if df.empty:
    st.stop()

# ========== FILTROS NO CABEÇALHO ==========
st.markdown("### 🎯 Filtros")
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

# Extrair anos e meses disponíveis
df['ANO'] = df['DATA_SERVICO'].dt.year
df['MES'] = df['DATA_SERVICO'].dt.month

# Filtro de Ano
anos_disponiveis = sorted([a for a in df['ANO'].dropna().unique().astype(int).tolist() if a <= 2026])
with col_f1:
    ano_selecionado = st.selectbox("📅 Ano", ['Todos'] + anos_disponiveis)

# Filtro de Mês
meses_nome = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
with col_f2:
    mes_selecionado = st.selectbox("🗓️ Mês", ['Todos'] + list(meses_nome.values()))

# Filtro de Polo
polos = ['Todos'] + sorted(df['POLO'].unique().tolist())
with col_f3:
    polo_selecionado = st.selectbox("🏢 Polo", polos)

# Filtro de Equipe  
equipes = ['Todas'] + sorted(df['EQUIPE'].unique().tolist())
with col_f4:
    equipe_selecionada = st.selectbox("👥 Equipe", equipes)

# Aplicar filtros
df_filtered = df.copy()

# Filtro de ano
if ano_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['ANO'] == ano_selecionado]

# Filtro de mês
if mes_selecionado != 'Todos':
    # Converter nome do mês para número
    mes_numero = [k for k, v in meses_nome.items() if v == mes_selecionado][0]
    df_filtered = df_filtered[df_filtered['MES'] == mes_numero]

if polo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['POLO'] == polo_selecionado]

if equipe_selecionada != 'Todas':
    df_filtered = df_filtered[df_filtered['EQUIPE'] == equipe_selecionada]

# KPIs principais
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="📋 Total de Serviços",
        value=len(df_filtered),
        delta=f"{len(df_filtered) - len(df)} vs total" if polo_selecionado != 'Todos' or equipe_selecionada != 'Todas' else None
    )

with col2:
    st.metric(
        label="🏢 Polos Ativos",
        value=df_filtered['POLO'].nunique()
    )

with col3:
    st.metric(
        label="👥 Equipes",
        value=df_filtered['EQUIPE'].nunique()
    )

with col4:
    # Serviços com baixa
    servicos_baixa = df_filtered['COLABORADORA_BAIXA'].notna().sum()
    st.metric(
        label="✅ Com Baixa",
        value=servicos_baixa
    )

with col5:
    # Média por dia
    dias = df_filtered['DATA_SERVICO'].nunique()
    media_dia = len(df_filtered) / dias if dias > 0 else 0
    st.metric(
        label="📊 Média/Dia",
        value=f"{media_dia:.1f}"
    )

st.markdown("---")

# Paleta de cores Equatorial para gráficos
cores_equatorial = ['#1a4d8f', '#2d6bb5', '#4a90d9', '#7ab3eb', '#a8d1f5', '#0d2e5a']

# Gráficos
col_left, col_right = st.columns(2)

with col_left:
    # Gráfico de Serviços por Polo
    st.subheader("📍 Serviços por Polo")
    df_polo = df_filtered.groupby('POLO').size().reset_index(name='Quantidade')
    df_polo = df_polo.sort_values('Quantidade', ascending=True)
    
    fig_polo = px.bar(
        df_polo, 
        x='Quantidade', 
        y='POLO',
        orientation='h',
        color='Quantidade',
        color_continuous_scale=[[0, '#a8d1f5'], [0.5, '#2d6bb5'], [1, '#0d2e5a']],
        text='Quantidade'
    )
    fig_polo.update_traces(textposition='outside', textfont=dict(color=AZUL_EQUATORIAL, size=14, family="Arial Black"))
    fig_polo.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="",
        xaxis_title="Quantidade de Serviços",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=AZUL_EQUATORIAL)
    )
    st.plotly_chart(fig_polo, use_container_width=True)

with col_right:
    # Gráfico de Pizza - Distribuição por Polo
    st.subheader("🥧 Distribuição por Polo")
    fig_pizza = px.pie(
        df_polo, 
        values='Quantidade', 
        names='POLO',
        color_discrete_sequence=cores_equatorial,
        hole=0.4
    )
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='white'))
    fig_pizza.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=AZUL_EQUATORIAL)
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

# Linha do tempo
st.subheader("📅 Serviços por Data")
df_timeline = df_filtered.groupby('DATA_SERVICO').size().reset_index(name='Quantidade')
df_timeline = df_timeline.sort_values('DATA_SERVICO')
# Filtrar apenas até 2026
df_timeline = df_timeline[df_timeline['DATA_SERVICO'] < '2027-01-01']

fig_timeline = px.line(
    df_timeline, 
    x='DATA_SERVICO', 
    y='Quantidade',
    markers=True,
    line_shape='spline'
)
fig_timeline.update_traces(
    line_color=AZUL_EQUATORIAL,
    marker_size=5,
    fill='tozeroy',
    fillcolor='rgba(26, 77, 143, 0.2)'
)
fig_timeline.update_layout(
    xaxis_title="Data",
    yaxis_title="Quantidade de Serviços",
    height=350,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color=AZUL_EQUATORIAL)
)
st.plotly_chart(fig_timeline, use_container_width=True)

# Gráfico de Serviços por Equipe
st.subheader("👥 Serviços por Equipe")
df_equipe = df_filtered.groupby('EQUIPE').size().reset_index(name='Quantidade')
df_equipe = df_equipe.sort_values('Quantidade', ascending=False).head(15)

fig_equipe = px.bar(
    df_equipe, 
    x='EQUIPE', 
    y='Quantidade',
    color='Quantidade',
    color_continuous_scale=[[0, '#a8d1f5'], [0.5, '#2d6bb5'], [1, '#0d2e5a']],
    text='Quantidade'
)
fig_equipe.update_traces(textposition='outside', textfont=dict(color=AZUL_EQUATORIAL, size=12))
fig_equipe.update_layout(
    showlegend=False,
    height=400,
    xaxis_title="Equipe",
    yaxis_title="Quantidade",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color=AZUL_EQUATORIAL)
)
st.plotly_chart(fig_equipe, use_container_width=True)

# Tabela de dados
st.subheader("📋 Dados Detalhados")
with st.expander("Clique para ver a tabela completa"):
    # Formatar as colunas para exibição
    df_display = df_filtered.copy()
    df_display['DATA_SERVICO'] = df_display['DATA_SERVICO'].dt.strftime('%d/%m/%Y')
    
    # Colunas disponíveis para exibir
    colunas_exibir = ['ORDEM_SERVICO', 'ABRIR_AM', 'POLO', 'EQUIPE', 'DATA_SERVICO', 
                      'HORARIO_INICIO', 'HORARIO_FIM', 'OBSERVACAO', 'COLABORADORA_BAIXA']
    colunas_disponiveis = [c for c in colunas_exibir if c in df_display.columns]
    
    st.dataframe(
        df_display[colunas_disponiveis].fillna('-'),
        use_container_width=True,
        height=400
    )

# Estatísticas adicionais
st.markdown("---")
st.subheader("📊 Estatísticas por Polo")

df_stats = df_filtered.groupby('POLO').agg({
    'ORDEM_SERVICO': 'count',
    'EQUIPE': 'nunique',
    'COLABORADORA_BAIXA': lambda x: x.notna().sum()
}).rename(columns={
    'ORDEM_SERVICO': 'Total Serviços',
    'EQUIPE': 'Qtd Equipes',
    'COLABORADORA_BAIXA': 'Com Baixa'
}).reset_index()

df_stats['Total Serviços'] = pd.to_numeric(df_stats['Total Serviços'], errors='coerce')
df_stats['Com Baixa'] = pd.to_numeric(df_stats['Com Baixa'], errors='coerce')
df_stats['% Baixa'] = (df_stats['Com Baixa'] / df_stats['Total Serviços'] * 100).round(1)

st.dataframe(df_stats, use_container_width=True, hide_index=True)

# Rodapé
st.markdown("---")
st.markdown(
    f"""
    <div class="footer">
        <p style="margin: 0; font-weight: bold; color: {AZUL_EQUATORIAL};">⚡ Grupo Equatorial</p>
        <p style="margin: 0; font-size: 0.8rem; color: {AZUL_CLARO};">Dashboard de Manutenção | Atualizado em tempo real</p>
        <p style="margin: 0; font-size: 0.7rem; color: gray;">📊 {len(df_filtered)} registros exibidos de {len(df)} total</p>
    </div>
    """, 
    unsafe_allow_html=True
)
