import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Manutenção",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<p class="main-header">🔧 Dashboard de Manutenção</p>', unsafe_allow_html=True)


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
    """Carrega dados do BigQuery ou CSV local"""
    
    # Tenta carregar do BigQuery primeiro
    try:
        client = get_bigquery_client()
        if client:
            query = """
            SELECT 
                ordem_servico AS ORDEM_SERVICO,
                abrir_am AS ABRIR_AM,
                polo AS POLO,
                equipe AS EQUIPE,
                data_servico AS DATA_SERVICO,
                horario_inicio AS HORARIO_INICIO,
                horario_fim AS HORARIO_FIM,
                observacao AS OBSERVACAO,
                colaboradora_baixa AS COLABORADORA_BAIXA,
                data_baixa AS DATA_BAIXA
            FROM `meu-projeto-manutencao.manutencao.servicos`
            """
            df = client.query(query).to_dataframe()
            df['DATA_SERVICO'] = pd.to_datetime(df['DATA_SERVICO'])
            return df
    except Exception as e:
        st.sidebar.warning(f"BigQuery indisponível, usando CSV local")
    
    # Fallback para CSV local
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

# Sidebar - Filtros
st.sidebar.header("🎯 Filtros")

# Filtro de data
min_date = df['DATA_SERVICO'].min()
max_date = df['DATA_SERVICO'].max()
date_range = st.sidebar.date_input(
    "Período",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtro de Polo
polos = ['Todos'] + sorted(df['POLO'].unique().tolist())
polo_selecionado = st.sidebar.selectbox("Polo", polos)

# Filtro de Equipe
equipes = ['Todas'] + sorted(df['EQUIPE'].unique().tolist())
equipe_selecionada = st.sidebar.selectbox("Equipe", equipes)

# Filtro de Tipo de Serviço
tipos = ['Todos'] + [t for t in df['ABRIR_AM'].dropna().unique().tolist()]
tipo_selecionado = st.sidebar.selectbox("Tipo de Serviço", tipos)

# Aplicar filtros
df_filtered = df.copy()

if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered['DATA_SERVICO'] >= pd.Timestamp(date_range[0])) & 
        (df_filtered['DATA_SERVICO'] <= pd.Timestamp(date_range[1]))
    ]

if polo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['POLO'] == polo_selecionado]

if equipe_selecionada != 'Todas':
    df_filtered = df_filtered[df_filtered['EQUIPE'] == equipe_selecionada]

if tipo_selecionado != 'Todos':
    df_filtered = df_filtered[df_filtered['ABRIR_AM'] == tipo_selecionado]

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
        color_continuous_scale='Blues',
        text='Quantidade'
    )
    fig_polo.update_traces(textposition='outside')
    fig_polo.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="",
        xaxis_title="Quantidade de Serviços"
    )
    st.plotly_chart(fig_polo, use_container_width=True)

with col_right:
    # Gráfico de Pizza - Distribuição por Polo
    st.subheader("🥧 Distribuição por Polo")
    fig_pizza = px.pie(
        df_polo, 
        values='Quantidade', 
        names='POLO',
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.4
    )
    fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
    fig_pizza.update_layout(height=400)
    st.plotly_chart(fig_pizza, use_container_width=True)

# Linha do tempo
st.subheader("📅 Serviços por Data")
df_timeline = df_filtered.groupby('DATA_SERVICO').size().reset_index(name='Quantidade')
df_timeline = df_timeline.sort_values('DATA_SERVICO')

fig_timeline = px.line(
    df_timeline, 
    x='DATA_SERVICO', 
    y='Quantidade',
    markers=True,
    line_shape='spline'
)
fig_timeline.update_traces(
    line_color='#1f77b4',
    marker_size=10,
    fill='tozeroy',
    fillcolor='rgba(31, 119, 180, 0.2)'
)
fig_timeline.update_layout(
    xaxis_title="Data",
    yaxis_title="Quantidade de Serviços",
    height=350
)
st.plotly_chart(fig_timeline, use_container_width=True)

# Segunda linha de gráficos
col_left2, col_right2 = st.columns(2)

with col_left2:
    # Gráfico de Serviços por Equipe
    st.subheader("👥 Serviços por Equipe")
    df_equipe = df_filtered.groupby('EQUIPE').size().reset_index(name='Quantidade')
    df_equipe = df_equipe.sort_values('Quantidade', ascending=False)
    
    fig_equipe = px.bar(
        df_equipe, 
        x='EQUIPE', 
        y='Quantidade',
        color='Quantidade',
        color_continuous_scale='Viridis',
        text='Quantidade'
    )
    fig_equipe.update_traces(textposition='outside')
    fig_equipe.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Equipe",
        yaxis_title="Quantidade"
    )
    st.plotly_chart(fig_equipe, use_container_width=True)

with col_right2:
    # Gráfico de Tipo de Serviço
    st.subheader("🔧 Tipos de Serviço")
    df_tipo = df_filtered[df_filtered['ABRIR_AM'].notna()].groupby('ABRIR_AM').size().reset_index(name='Quantidade')
    df_tipo = df_tipo.sort_values('Quantidade', ascending=False).head(10)
    
    if not df_tipo.empty:
        fig_tipo = px.bar(
            df_tipo, 
            x='ABRIR_AM', 
            y='Quantidade',
            color='ABRIR_AM',
            text='Quantidade'
        )
        fig_tipo.update_traces(textposition='outside')
        fig_tipo.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Tipo de Serviço",
            yaxis_title="Quantidade"
        )
        st.plotly_chart(fig_tipo, use_container_width=True)
    else:
        st.info("Nenhum tipo de serviço informado nos registros filtrados")

# Heatmap - Serviços por Polo e Data
st.subheader("🗓️ Mapa de Calor: Serviços por Polo e Data")
df_heatmap = df_filtered.groupby(['POLO', df_filtered['DATA_SERVICO'].dt.strftime('%d/%m')]).size().reset_index(name='Quantidade')
df_heatmap_pivot = df_heatmap.pivot(index='POLO', columns='DATA_SERVICO', values='Quantidade').fillna(0)

fig_heatmap = px.imshow(
    df_heatmap_pivot,
    labels=dict(x="Data", y="Polo", color="Serviços"),
    color_continuous_scale='YlOrRd',
    aspect='auto'
)
fig_heatmap.update_layout(height=350)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Tabela de dados
st.subheader("📋 Dados Detalhados")
with st.expander("Clique para ver a tabela completa"):
    # Formatar as colunas para exibição
    df_display = df_filtered.copy()
    df_display['DATA_SERVICO'] = df_display['DATA_SERVICO'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        df_display[[
            'ID', 'ABRIR_AM', 'POLO', 'EQUIPE', 'DATA_SERVICO', 
            'HORARIO_INICIO', 'HORARIO_FIM', 'OBSERVACAO', 'COLABORADORA_BAIXA'
        ]].fillna('-'),
        use_container_width=True,
        height=400
    )

# Estatísticas adicionais
st.markdown("---")
st.subheader("📊 Estatísticas por Polo")

df_stats = df_filtered.groupby('POLO').agg({
    'ID': 'count',
    'EQUIPE': 'nunique',
    'COLABORADORA_BAIXA': lambda x: x.notna().sum()
}).rename(columns={
    'ID': 'Total Serviços',
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
    """
    <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        Dashboard de Manutenção | Atualizado em tempo real
    </div>
    """, 
    unsafe_allow_html=True
)
