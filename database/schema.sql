-- Schema do Banco de Dados - Manutenção
-- Compatível com PostgreSQL, MySQL e SQLite

-- Tabela principal de serviços de manutenção
CREATE TABLE IF NOT EXISTS manutencao (
    id SERIAL PRIMARY KEY,
    ordem_servico VARCHAR(20) NOT NULL,
    abrir_am VARCHAR(50),
    medidor_encontrado VARCHAR(50),
    medidor_instalado VARCHAR(50),
    chave_afericao_encontrada VARCHAR(10),
    chave_afericao_instalada VARCHAR(10),
    tcs_encontrado VARCHAR(10),
    tcs_instalados VARCHAR(10),
    troca_caixa VARCHAR(10),
    polo VARCHAR(50) NOT NULL,
    equipe VARCHAR(50) NOT NULL,
    data_servico DATE NOT NULL,
    horario_inicio TIME,
    horario_fim TIME,
    observacao TEXT,
    colaboradora_baixa VARCHAR(100),
    data_baixa DATE,
    nota VARCHAR(50),
    am_remanejo VARCHAR(50),
    anexo VARCHAR(100),
    obs TEXT,
    faixa VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_data_servico ON manutencao(data_servico);
CREATE INDEX IF NOT EXISTS idx_polo ON manutencao(polo);
CREATE INDEX IF NOT EXISTS idx_equipe ON manutencao(equipe);
CREATE INDEX IF NOT EXISTS idx_ordem_servico ON manutencao(ordem_servico);

-- Tabela de histórico diário (para comparações)
CREATE TABLE IF NOT EXISTS historico_diario (
    id SERIAL PRIMARY KEY,
    data_referencia DATE NOT NULL UNIQUE,
    total_servicos INTEGER,
    servicos_maraba INTEGER,
    servicos_tucurui INTEGER,
    servicos_parauapebas INTEGER,
    servicos_redencao INTEGER,
    servicos_com_baixa INTEGER,
    total_equipes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de sincronização
CREATE TABLE IF NOT EXISTS sync_logs (
    id SERIAL PRIMARY KEY,
    sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_inserted INTEGER,
    records_updated INTEGER,
    status VARCHAR(20),
    message TEXT
);
