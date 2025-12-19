"""
Gerador de Dashboard Looker Studio via Linking API
Cria relatórios automaticamente usando URLs parametrizadas
"""
import urllib.parse
import webbrowser
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import BIGQUERY_CONFIG


def generate_looker_url(
    report_name: str = "Dashboard Manutenção",
    project_id: str = None,
    dataset_id: str = None,
    table_id: str = None,
    use_template: bool = False,
    template_id: str = None
) -> str:
    """
    Gera URL para criar relatório no Looker Studio automaticamente
    
    A Linking API do Looker Studio permite criar relatórios via URL
    com a fonte de dados já configurada.
    """
    
    # Usa configurações do BigQuery se não especificadas
    project_id = project_id or BIGQUERY_CONFIG['project_id']
    dataset_id = dataset_id or BIGQUERY_CONFIG['dataset']
    table_id = table_id or BIGQUERY_CONFIG['table']
    
    # URL base do Looker Studio
    base_url = "https://lookerstudio.google.com/reporting/create"
    
    # Parâmetros para criar relatório com BigQuery
    params = {
        # Nome do relatório
        "r.reportName": report_name,
        
        # Configuração do Data Source (BigQuery)
        "ds.connector": "bigQuery",
        "ds.datasourceName": f"Dados Manutenção - {table_id}",
        "ds.type": "TABLE",
        "ds.projectId": project_id,
        "ds.datasetId": dataset_id,
        "ds.tableId": table_id,
        
        # Modo de edição
        "c.mode": "edit",
    }
    
    # Se usar template existente
    if use_template and template_id:
        params["c.reportId"] = template_id
    
    # Constrói a URL
    query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"
    
    return full_url


def generate_custom_query_url(
    report_name: str = "Dashboard Manutenção - Custom",
    sql_query: str = None
) -> str:
    """
    Gera URL com query SQL customizada
    """
    
    project_id = BIGQUERY_CONFIG['project_id']
    dataset_id = BIGQUERY_CONFIG['dataset']
    table_id = BIGQUERY_CONFIG['table']
    
    # Query SQL padrão se não especificada
    if sql_query is None:
        sql_query = f"""
SELECT 
    ordem_servico,
    abrir_am AS tipo_servico,
    polo,
    equipe,
    data_servico,
    horario_inicio,
    horario_fim,
    observacao,
    colaboradora_baixa,
    CASE 
        WHEN colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '' 
        THEN 'Com Baixa' 
        ELSE 'Sem Baixa' 
    END AS status_baixa,
    EXTRACT(DAYOFWEEK FROM data_servico) AS dia_semana,
    FORMAT_DATE('%B', data_servico) AS mes
FROM `{project_id}.{dataset_id}.{table_id}`
WHERE data_servico IS NOT NULL
ORDER BY data_servico DESC
        """.strip()
    
    base_url = "https://lookerstudio.google.com/reporting/create"
    
    params = {
        "r.reportName": report_name,
        "ds.connector": "bigQuery",
        "ds.datasourceName": "Manutenção - Query Customizada",
        "ds.type": "CUSTOM_QUERY",
        "ds.sql": sql_query,
        "ds.billingProjectId": project_id,
        "c.mode": "edit",
    }
    
    query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    full_url = f"{base_url}?{query_string}"
    
    return full_url


def create_looker_dashboard():
    """
    Cria o dashboard no Looker Studio abrindo o navegador
    """
    
    print("""
╔═══════════════════════════════════════════════════════╗
║      🚀 CRIANDO DASHBOARD NO LOOKER STUDIO           ║
╠═══════════════════════════════════════════════════════╣
║                                                       ║
║  📊 Projeto: {project}            
║  📁 Dataset: {dataset}                       
║  📋 Tabela: {table}                          
║                                                       ║
║  O navegador será aberto automaticamente...          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """.format(
        project=BIGQUERY_CONFIG['project_id'],
        dataset=BIGQUERY_CONFIG['dataset'],
        table=BIGQUERY_CONFIG['table']
    ))
    
    # Gera URL
    url = generate_looker_url(
        report_name="Dashboard Manutenção - Serviços",
    )
    
    print(f"\n🔗 URL gerada:\n{url}\n")
    
    # Abre no navegador
    print("🌐 Abrindo navegador...")
    webbrowser.open(url)
    
    print("""
✅ Navegador aberto!

📋 PRÓXIMOS PASSOS NO LOOKER STUDIO:

1. Faça login com sua conta Google (se solicitado)
2. Clique em "AUTORIZAR" para conectar ao BigQuery
3. O relatório será criado com a fonte de dados configurada
4. Adicione os gráficos:
   
   📊 GRÁFICOS SUGERIDOS:
   ┌────────────────────────────────────────────┐
   │  • Scorecard: Total de Serviços           │
   │  • Gráfico de Barras: Serviços por Polo   │
   │  • Gráfico de Pizza: Distribuição %       │
   │  • Gráfico de Linha: Timeline por Data    │
   │  • Tabela: Detalhes por Equipe            │
   └────────────────────────────────────────────┘

5. Adicione filtros:
   • Controle de Data (data_servico)
   • Filtro de Polo
   • Filtro de Equipe

6. Clique em "Salvar" para guardar o relatório!
    """)
    
    return url


def print_all_urls():
    """
    Exibe todas as URLs disponíveis
    """
    
    print("\n" + "="*60)
    print("📊 URLS DO LOOKER STUDIO - DASHBOARD MANUTENÇÃO")
    print("="*60)
    
    # URL básica (tabela)
    url_basic = generate_looker_url("Dashboard Manutenção - Básico")
    print(f"\n1️⃣ Dashboard Básico (Tabela direta):\n{url_basic}")
    
    # URL com query customizada
    url_custom = generate_custom_query_url("Dashboard Manutenção - Avançado")
    print(f"\n2️⃣ Dashboard Avançado (Query SQL):\n{url_custom}")
    
    # URL apenas com resumo por polo
    sql_polo = f"""
SELECT 
    polo,
    COUNT(*) as total_servicos,
    COUNT(DISTINCT equipe) as equipes,
    COUNTIF(colaboradora_baixa IS NOT NULL) as com_baixa
FROM `{BIGQUERY_CONFIG['project_id']}.{BIGQUERY_CONFIG['dataset']}.{BIGQUERY_CONFIG['table']}`
GROUP BY polo
ORDER BY total_servicos DESC
    """.strip()
    
    url_polo = generate_custom_query_url("Dashboard Manutenção - Por Polo")
    print(f"\n3️⃣ Dashboard Resumo por Polo:\n{url_polo}")
    
    print("\n" + "="*60)
    print("💡 Copie qualquer URL acima e cole no navegador!")
    print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Criar Dashboard no Looker Studio')
    parser.add_argument('--create', action='store_true', help='Cria e abre o dashboard')
    parser.add_argument('--urls', action='store_true', help='Mostra todas as URLs disponíveis')
    parser.add_argument('--url-only', action='store_true', help='Apenas mostra a URL (não abre)')
    
    args = parser.parse_args()
    
    if args.create:
        create_looker_dashboard()
    elif args.urls:
        print_all_urls()
    elif args.url_only:
        url = generate_looker_url()
        print(url)
    else:
        # Padrão: cria o dashboard
        create_looker_dashboard()
