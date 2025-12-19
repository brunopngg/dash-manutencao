from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import snowflake.connector
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Dashboard API",
    description="API para conectar ao Snowflake e fornecer dados para dashboards",
    version="1.0.0"
)

# CORS - permitir frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração Snowflake via variáveis de ambiente
SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
}


def get_snowflake_connection():
    """Cria conexão com Snowflake"""
    try:
        conn = snowflake.connector.connect(
            account=SNOWFLAKE_CONFIG["account"],
            user=SNOWFLAKE_CONFIG["user"],
            password=SNOWFLAKE_CONFIG["password"],
            warehouse=SNOWFLAKE_CONFIG["warehouse"],
            database=SNOWFLAKE_CONFIG["database"],
            schema=SNOWFLAKE_CONFIG["schema"],
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao Snowflake: {str(e)}")


def execute_query(query: str, params: dict = None) -> List[Dict[str, Any]]:
    """Executa query no Snowflake e retorna resultados"""
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    finally:
        conn.close()


# ============ ENDPOINTS ============

@app.get("/")
def root():
    return {"message": "Dashboard API", "status": "online"}


@app.get("/health")
def health_check():
    """Verifica saúde da API e conexão com Snowflake"""
    try:
        conn = get_snowflake_connection()
        conn.close()
        return {"status": "healthy", "snowflake": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "snowflake": "disconnected", "error": str(e)}


# ============ ENDPOINTS MANUTENÇÃO ============

@app.get("/api/manutencao/dados")
def get_manutencao_dados(
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    polo: Optional[str] = None,
    equipe: Optional[str] = None,
    limit: int = 1000
):
    """Busca dados de manutenção com filtros"""
    
    query = """
    SELECT 
        ORDEM_SERVICO,
        POLO,
        EQUIPE,
        DATA_SERVICO,
        HORARIO_INICIO,
        HORARIO_FIM,
        OBSERVACAO,
        COLABORADORA_BAIXA,
        DATA_BAIXA
    FROM MANUTENCAO
    WHERE 1=1
    """
    
    if ano:
        query += f" AND YEAR(DATA_SERVICO) = {ano}"
    if mes:
        query += f" AND MONTH(DATA_SERVICO) = {mes}"
    if polo:
        query += f" AND POLO = '{polo}'"
    if equipe:
        query += f" AND EQUIPE = '{equipe}'"
    
    query += f" ORDER BY DATA_SERVICO DESC LIMIT {limit}"
    
    return execute_query(query)


@app.get("/api/manutencao/kpis")
def get_manutencao_kpis(
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    polo: Optional[str] = None,
    equipe: Optional[str] = None
):
    """Retorna KPIs de manutenção"""
    
    where_clause = "WHERE 1=1"
    if ano:
        where_clause += f" AND YEAR(DATA_SERVICO) = {ano}"
    if mes:
        where_clause += f" AND MONTH(DATA_SERVICO) = {mes}"
    if polo:
        where_clause += f" AND POLO = '{polo}'"
    if equipe:
        where_clause += f" AND EQUIPE = '{equipe}'"
    
    query = f"""
    SELECT 
        COUNT(*) as total_servicos,
        COUNT(DISTINCT POLO) as polos_ativos,
        COUNT(DISTINCT EQUIPE) as equipes_ativas,
        COUNT(CASE WHEN COLABORADORA_BAIXA IS NOT NULL THEN 1 END) as com_baixa
    FROM MANUTENCAO
    {where_clause}
    """
    
    result = execute_query(query)
    return result[0] if result else {}


@app.get("/api/manutencao/por-polo")
def get_manutencao_por_polo(
    ano: Optional[int] = None,
    mes: Optional[int] = None
):
    """Retorna quantidade de serviços por polo"""
    
    where_clause = "WHERE 1=1"
    if ano:
        where_clause += f" AND YEAR(DATA_SERVICO) = {ano}"
    if mes:
        where_clause += f" AND MONTH(DATA_SERVICO) = {mes}"
    
    query = f"""
    SELECT 
        POLO as name,
        COUNT(*) as value
    FROM MANUTENCAO
    {where_clause}
    GROUP BY POLO
    ORDER BY value DESC
    """
    
    return execute_query(query)


@app.get("/api/manutencao/por-equipe")
def get_manutencao_por_equipe(
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    limit: int = 15
):
    """Retorna quantidade de serviços por equipe"""
    
    where_clause = "WHERE 1=1"
    if ano:
        where_clause += f" AND YEAR(DATA_SERVICO) = {ano}"
    if mes:
        where_clause += f" AND MONTH(DATA_SERVICO) = {mes}"
    
    query = f"""
    SELECT 
        EQUIPE as name,
        COUNT(*) as value
    FROM MANUTENCAO
    {where_clause}
    GROUP BY EQUIPE
    ORDER BY value DESC
    LIMIT {limit}
    """
    
    return execute_query(query)


@app.get("/api/manutencao/por-data")
def get_manutencao_por_data(
    ano: Optional[int] = None,
    mes: Optional[int] = None
):
    """Retorna quantidade de serviços por data (timeline)"""
    
    where_clause = "WHERE DATA_SERVICO IS NOT NULL"
    if ano:
        where_clause += f" AND YEAR(DATA_SERVICO) = {ano}"
    if mes:
        where_clause += f" AND MONTH(DATA_SERVICO) = {mes}"
    
    query = f"""
    SELECT 
        TO_CHAR(DATA_SERVICO, 'YYYY-MM-DD') as date,
        COUNT(*) as value
    FROM MANUTENCAO
    {where_clause}
    GROUP BY DATA_SERVICO
    ORDER BY DATA_SERVICO
    """
    
    return execute_query(query)


@app.get("/api/manutencao/filtros")
def get_manutencao_filtros():
    """Retorna opções de filtros disponíveis"""
    
    anos_query = """
    SELECT DISTINCT YEAR(DATA_SERVICO) as ano 
    FROM MANUTENCAO 
    WHERE DATA_SERVICO IS NOT NULL 
    ORDER BY ano
    """
    
    polos_query = """
    SELECT DISTINCT POLO 
    FROM MANUTENCAO 
    WHERE POLO IS NOT NULL 
    ORDER BY POLO
    """
    
    equipes_query = """
    SELECT DISTINCT EQUIPE 
    FROM MANUTENCAO 
    WHERE EQUIPE IS NOT NULL 
    ORDER BY EQUIPE
    """
    
    anos = [r["ANO"] for r in execute_query(anos_query)]
    polos = [r["POLO"] for r in execute_query(polos_query)]
    equipes = [r["EQUIPE"] for r in execute_query(equipes_query)]
    
    return {
        "anos": anos,
        "polos": polos,
        "equipes": equipes
    }


# ============ QUERY CUSTOMIZADA ============

class QueryRequest(BaseModel):
    query: str
    

@app.post("/api/query")
def execute_custom_query(request: QueryRequest):
    """Executa query customizada (apenas SELECT)"""
    query = request.query.strip()
    
    # Segurança básica - apenas SELECT
    if not query.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Apenas queries SELECT são permitidas")
    
    # Bloquear comandos perigosos
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "CREATE"]
    for keyword in dangerous_keywords:
        if keyword in query.upper():
            raise HTTPException(status_code=400, detail=f"Comando {keyword} não permitido")
    
    return execute_query(query)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
