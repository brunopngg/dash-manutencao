"""
📊 Página: Nova Planilha
Template para adicionar novas fontes de dados
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Nova Planilha",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Adicionar Nova Planilha")
st.markdown("Faça upload de uma nova planilha para análise")

# Upload de arquivo
uploaded_file = st.file_uploader(
    "Escolha um arquivo CSV ou Excel",
    type=['csv', 'xlsx', 'xls'],
    help="Arraste ou clique para fazer upload"
)

if uploaded_file is not None:
    # Detectar tipo de arquivo
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'csv':
            # Tentar diferentes encodings
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado com sucesso! {len(df)} linhas x {len(df.columns)} colunas")
        
        # Preview dos dados
        st.subheader("📋 Preview dos Dados")
        st.dataframe(df.head(20), use_container_width=True)
        
        # Informações sobre as colunas
        st.subheader("📊 Colunas Disponíveis")
        
        col_info = pd.DataFrame({
            'Coluna': df.columns,
            'Tipo': df.dtypes.astype(str),
            'Valores Únicos': [df[col].nunique() for col in df.columns],
            'Valores Nulos': df.isnull().sum(),
            'Exemplo': [str(df[col].iloc[0]) if len(df) > 0 else '-' for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Gerador de gráfico rápido
        st.subheader("📈 Criar Gráfico Rápido")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_grafico = st.selectbox(
                "Tipo de Gráfico",
                ['Barras', 'Pizza', 'Linha', 'Dispersão', 'Histograma']
            )
        
        with col2:
            coluna_principal = st.selectbox(
                "Coluna Principal (Dimensão)",
                options=df.columns.tolist()
            )
        
        # Gerar gráfico baseado no tipo
        if st.button("🎨 Gerar Gráfico"):
            if tipo_grafico == 'Barras':
                df_chart = df[coluna_principal].value_counts().reset_index()
                df_chart.columns = [coluna_principal, 'Contagem']
                fig = px.bar(df_chart, x=coluna_principal, y='Contagem', color='Contagem')
                
            elif tipo_grafico == 'Pizza':
                df_chart = df[coluna_principal].value_counts().reset_index()
                df_chart.columns = [coluna_principal, 'Contagem']
                fig = px.pie(df_chart, names=coluna_principal, values='Contagem')
                
            elif tipo_grafico == 'Histograma':
                fig = px.histogram(df, x=coluna_principal)
                
            elif tipo_grafico == 'Linha':
                df_chart = df[coluna_principal].value_counts().sort_index().reset_index()
                df_chart.columns = [coluna_principal, 'Contagem']
                fig = px.line(df_chart, x=coluna_principal, y='Contagem', markers=True)
                
            else:  # Dispersão
                col_y = st.selectbox("Coluna Y", options=[c for c in df.columns if c != coluna_principal])
                fig = px.scatter(df, x=coluna_principal, y=col_y)
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Estatísticas
        st.subheader("📊 Estatísticas Básicas")
        
        # Apenas colunas numéricas
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("Nenhuma coluna numérica encontrada")
        
        # Opção de salvar
        st.markdown("---")
        st.subheader("💾 Salvar Dados")
        
        nome_arquivo = st.text_input("Nome do arquivo (sem extensão)", value="nova_planilha")
        
        if st.button("💾 Salvar no Projeto"):
            save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', f'{nome_arquivo}.csv')
            df.to_csv(save_path, index=False, encoding='utf-8')
            st.success(f"✅ Arquivo salvo em: data/{nome_arquivo}.csv")
            st.info("Agora você pode criar uma nova página para analisar esses dados!")
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

else:
    st.info("👆 Faça upload de um arquivo para começar")
    
    st.markdown("""
    ### 📝 Formatos suportados:
    - **CSV** (.csv)
    - **Excel** (.xlsx, .xls)
    
    ### 💡 Dicas:
    1. Certifique-se que a primeira linha contém os nomes das colunas
    2. Evite caracteres especiais nos nomes das colunas
    3. Datas devem estar em formato consistente
    """)
