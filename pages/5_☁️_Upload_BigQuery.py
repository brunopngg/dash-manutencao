"""
📊 Página: Upload para BigQuery
Faz upload de novas planilhas para o BigQuery
"""
import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Upload BigQuery",
    page_icon="☁️",
    layout="wide"
)

st.title("☁️ Upload para BigQuery")
st.markdown("Envie novas planilhas para o Google BigQuery")

# Verificar conexão com BigQuery
try:
    from dashboard import get_bigquery_client
    client = get_bigquery_client()
    if client:
        st.success("✅ Conectado ao BigQuery")
    else:
        st.warning("⚠️ BigQuery não configurado. Os dados serão salvos apenas localmente.")
        client = None
except Exception as e:
    st.warning(f"⚠️ BigQuery não disponível: {e}")
    client = None

# Upload de arquivo
uploaded_file = st.file_uploader(
    "Escolha um arquivo CSV ou Excel",
    type=['csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_extension == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Arquivo carregado: {len(df)} linhas x {len(df.columns)} colunas")
        
        # Preview
        st.subheader("📋 Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Configurações de upload
        st.subheader("⚙️ Configurações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_tabela = st.text_input(
                "Nome da tabela no BigQuery",
                value=uploaded_file.name.split('.')[0].lower().replace(' ', '_').replace('-', '_')
            )
        
        with col2:
            modo_escrita = st.selectbox(
                "Modo de escrita",
                ['WRITE_TRUNCATE (Substituir)', 'WRITE_APPEND (Adicionar)', 'WRITE_EMPTY (Apenas se vazia)']
            )
        
        # Mapeamento de colunas
        st.subheader("📝 Colunas")
        
        col_info = pd.DataFrame({
            'Coluna Original': df.columns,
            'Tipo Detectado': df.dtypes.astype(str),
            'Valores Únicos': [df[col].nunique() for col in df.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)
        
        # Botão de upload
        if st.button("🚀 Enviar para BigQuery", type="primary"):
            if client:
                try:
                    from google.cloud import bigquery
                    
                    # Limpar nomes das colunas
                    df.columns = [c.lower().replace(' ', '_').replace('-', '_') for c in df.columns]
                    
                    # Configurar tabela
                    table_id = f"meu-projeto-manutencao.manutencao.{nome_tabela}"
                    
                    # Configurar job
                    job_config = bigquery.LoadJobConfig(
                        write_disposition=modo_escrita.split(' ')[0],
                        autodetect=True
                    )
                    
                    # Upload
                    with st.spinner("Enviando dados..."):
                        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
                        job.result()
                    
                    st.success(f"✅ Dados enviados para `{table_id}`!")
                    st.balloons()
                    
                    # Mostrar info da tabela
                    table = client.get_table(table_id)
                    st.info(f"📊 Tabela agora tem {table.num_rows} linhas")
                    
                except Exception as e:
                    st.error(f"❌ Erro no upload: {str(e)}")
            else:
                # Salvar localmente como fallback
                save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', f'{nome_tabela}.csv')
                df.to_csv(save_path, index=False, encoding='utf-8')
                st.warning(f"⚠️ BigQuery não disponível. Salvo localmente em: data/{nome_tabela}.csv")
                
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

else:
    st.info("👆 Faça upload de um arquivo para começar")

# Listar tabelas existentes
if client:
    st.markdown("---")
    st.subheader("📁 Tabelas Existentes no BigQuery")
    
    try:
        tables = list(client.list_tables("meu-projeto-manutencao.manutencao"))
        
        if tables:
            table_info = []
            for table in tables:
                full_table = client.get_table(table)
                table_info.append({
                    'Tabela': table.table_id,
                    'Linhas': full_table.num_rows,
                    'Colunas': len(full_table.schema),
                    'Criada': full_table.created.strftime('%d/%m/%Y') if full_table.created else '-'
                })
            
            st.dataframe(pd.DataFrame(table_info), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma tabela encontrada")
            
    except Exception as e:
        st.warning(f"Não foi possível listar tabelas: {e}")
