# Backend API - Dashboard Equatorial

API FastAPI para conectar ao Snowflake e fornecer dados para os dashboards.

## Configuração

1. Crie o arquivo `.env` baseado no `.env.example`:
```bash
cp .env.example .env
```

2. Edite o `.env` com suas credenciais do Snowflake:
```
SNOWFLAKE_ACCOUNT=abc12345.us-east-1
SNOWFLAKE_USER=seu_usuario
SNOWFLAKE_PASSWORD=sua_senha
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MEU_DATABASE
SNOWFLAKE_SCHEMA=PUBLIC
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a API:
```bash
python main.py
# ou
uvicorn main:app --reload --port 8000
```

## Endpoints

### Saúde
- `GET /` - Status da API
- `GET /health` - Verifica conexão com Snowflake

### Manutenção
- `GET /api/manutencao/dados` - Dados de manutenção (com filtros)
- `GET /api/manutencao/kpis` - KPIs agregados
- `GET /api/manutencao/por-polo` - Agrupado por polo
- `GET /api/manutencao/por-equipe` - Agrupado por equipe
- `GET /api/manutencao/por-data` - Timeline
- `GET /api/manutencao/filtros` - Opções de filtros

### Query Customizada
- `POST /api/query` - Executa SELECT customizado

## Filtros disponíveis

Todos os endpoints de manutenção aceitam:
- `ano` (int): Filtrar por ano
- `mes` (int): Filtrar por mês (1-12)
- `polo` (string): Filtrar por polo
- `equipe` (string): Filtrar por equipe

Exemplo:
```
GET /api/manutencao/dados?ano=2024&mes=12&polo=MARABA
```
