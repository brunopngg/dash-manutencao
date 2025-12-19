-- ================================================================
-- 📊 QUERIES SQL AVANÇADAS PARA LOOKER STUDIO
-- ================================================================
-- Projeto: meu-projeto-manutencao
-- Dataset: manutencao
-- Tabela: servicos
-- Atualizado: 19/12/2025
-- ================================================================


-- ================================================================
-- 🔷 QUERY 1: DASHBOARD PRINCIPAL (USE ESTA COMO FONTE DE DADOS)
-- ================================================================
-- Campos calculados para todos os gráficos
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
    data_baixa,
    
    -- Status da baixa
    CASE 
        WHEN colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '' 
        THEN 'Com Baixa' 
        ELSE 'Sem Baixa' 
    END AS status_baixa,
    
    -- Campos de tempo
    EXTRACT(YEAR FROM data_servico) AS ano,
    EXTRACT(MONTH FROM data_servico) AS mes_num,
    FORMAT_DATE('%B', data_servico) AS mes_nome,
    FORMAT_DATE('%Y-%m', data_servico) AS ano_mes,
    EXTRACT(WEEK FROM data_servico) AS semana,
    EXTRACT(DAYOFWEEK FROM data_servico) AS dia_semana_num,
    FORMAT_DATE('%A', data_servico) AS dia_semana_nome,
    FORMAT_DATE('%d/%m/%Y', data_servico) AS data_formatada,
    
    -- Indicador se é fim de semana
    CASE 
        WHEN EXTRACT(DAYOFWEEK FROM data_servico) IN (1, 7) 
        THEN 'Fim de Semana' 
        ELSE 'Dia Útil' 
    END AS tipo_dia,
    
    -- Período do mês
    CASE 
        WHEN EXTRACT(DAY FROM data_servico) <= 10 THEN 'Início (1-10)'
        WHEN EXTRACT(DAY FROM data_servico) <= 20 THEN 'Meio (11-20)'
        ELSE 'Final (21-31)'
    END AS periodo_mes,
    
    -- Polo simplificado para gráficos
    CASE polo
        WHEN 'MARABA' THEN '🔵 MARABÁ'
        WHEN 'TUCURUI' THEN '🟢 TUCURUÍ'
        WHEN 'PARAUAPEBAS' THEN '🟡 PARAUAPEBAS'
        WHEN 'REDENÇÃO' THEN '🟠 REDENÇÃO'
        ELSE polo
    END AS polo_emoji

FROM `meu-projeto-manutencao.manutencao.servicos`
WHERE data_servico IS NOT NULL;


-- ================================================================
-- 🔷 QUERY 2: KPIs PRINCIPAIS (Scorecards)
-- ================================================================
SELECT 
    COUNT(*) AS total_servicos,
    COUNT(DISTINCT polo) AS total_polos,
    COUNT(DISTINCT equipe) AS total_equipes,
    COUNTIF(colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '') AS servicos_com_baixa,
    COUNTIF(colaboradora_baixa IS NULL OR colaboradora_baixa = '') AS servicos_sem_baixa,
    ROUND(COUNTIF(colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '') * 100.0 / COUNT(*), 1) AS percentual_baixa,
    MIN(data_servico) AS primeira_data,
    MAX(data_servico) AS ultima_data,
    DATE_DIFF(MAX(data_servico), MIN(data_servico), DAY) AS dias_operacao,
    ROUND(COUNT(*) * 1.0 / NULLIF(DATE_DIFF(MAX(data_servico), MIN(data_servico), DAY), 0), 1) AS media_servicos_dia
FROM `meu-projeto-manutencao.manutencao.servicos`;


-- ================================================================
-- 🔷 QUERY 3: RESUMO POR POLO (Gráfico de Barras/Pizza)
-- ================================================================
SELECT 
    polo,
    COUNT(*) AS total_servicos,
    COUNT(DISTINCT equipe) AS qtd_equipes,
    COUNTIF(colaboradora_baixa IS NOT NULL AND colaboradora_baixa != '') AS com_baixa,
    COUNTIF(colaboradora_baixa IS NULL OR colaboradora_baixa = '') AS sem_baixa,
    ROUND(COUNTIF(colaboradora_baixa IS NOT NULL) * 100.0 / COUNT(*), 1) AS pct_baixa,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct_total,
    MIN(data_servico) AS primeira_data,
    MAX(data_servico) AS ultima_data
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY polo
ORDER BY total_servicos DESC;


-- ================================================================
-- 🔷 QUERY 4: TIMELINE DIÁRIA (Gráfico de Linha)
-- ================================================================
SELECT 
    data_servico,
    FORMAT_DATE('%d/%m', data_servico) AS data_curta,
    FORMAT_DATE('%A', data_servico) AS dia_semana,
    COUNT(*) AS total_servicos,
    COUNT(DISTINCT polo) AS polos_ativos,
    COUNT(DISTINCT equipe) AS equipes_ativas,
    
    -- Média móvel 7 dias
    ROUND(AVG(COUNT(*)) OVER(ORDER BY data_servico ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS media_movel_7d,
    
    -- Acumulado
    SUM(COUNT(*)) OVER(ORDER BY data_servico) AS acumulado

FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY data_servico
ORDER BY data_servico;


-- ================================================================
-- 🔷 QUERY 5: COMPARATIVO DIÁRIO COM VARIAÇÃO
-- ================================================================
SELECT 
    data_servico,
    FORMAT_DATE('%d/%m/%Y', data_servico) AS data_formatada,
    FORMAT_DATE('%A', data_servico) AS dia_semana,
    servicos_hoje,
    servicos_ontem,
    variacao_absoluta,
    CASE 
        WHEN servicos_ontem = 0 THEN NULL
        ELSE ROUND((variacao_absoluta * 100.0) / servicos_ontem, 1)
    END AS variacao_percentual,
    CASE 
        WHEN variacao_absoluta > 0 THEN '📈 Aumento'
        WHEN variacao_absoluta < 0 THEN '📉 Queda'
        ELSE '➡️ Estável'
    END AS tendencia
FROM (
    SELECT 
        data_servico,
        COUNT(*) AS servicos_hoje,
        LAG(COUNT(*)) OVER (ORDER BY data_servico) AS servicos_ontem,
        COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY data_servico) AS variacao_absoluta
    FROM `meu-projeto-manutencao.manutencao.servicos`
    GROUP BY data_servico
)
ORDER BY data_servico DESC;


-- ================================================================
-- 🔷 QUERY 6: RANKING DE EQUIPES
-- ================================================================
SELECT 
    equipe,
    polo,
    COUNT(*) AS total_servicos,
    RANK() OVER(ORDER BY COUNT(*) DESC) AS ranking_geral,
    RANK() OVER(PARTITION BY polo ORDER BY COUNT(*) DESC) AS ranking_polo,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct_total,
    COUNT(DISTINCT data_servico) AS dias_trabalhados,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT data_servico), 1) AS media_por_dia,
    MIN(data_servico) AS primeira_data,
    MAX(data_servico) AS ultima_data
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY equipe, polo
ORDER BY total_servicos DESC;


-- ================================================================
-- 🔷 QUERY 7: HEATMAP - POLO x DIA DA SEMANA
-- ================================================================
SELECT 
    polo,
    CASE EXTRACT(DAYOFWEEK FROM data_servico)
        WHEN 1 THEN '1-Domingo'
        WHEN 2 THEN '2-Segunda'
        WHEN 3 THEN '3-Terça'
        WHEN 4 THEN '4-Quarta'
        WHEN 5 THEN '5-Quinta'
        WHEN 6 THEN '6-Sexta'
        WHEN 7 THEN '7-Sábado'
    END AS dia_semana,
    EXTRACT(DAYOFWEEK FROM data_servico) AS dia_num,
    COUNT(*) AS total_servicos
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY polo, dia_semana, dia_num
ORDER BY polo, dia_num;


-- ================================================================
-- 🔷 QUERY 8: ANÁLISE SEMANAL
-- ================================================================
SELECT 
    EXTRACT(YEAR FROM data_servico) AS ano,
    EXTRACT(WEEK FROM data_servico) AS semana,
    MIN(data_servico) AS inicio_semana,
    MAX(data_servico) AS fim_semana,
    COUNT(*) AS total_servicos,
    COUNT(DISTINCT polo) AS polos_ativos,
    COUNT(DISTINCT equipe) AS equipes_ativas,
    COUNT(DISTINCT data_servico) AS dias_trabalhados,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT data_servico), 1) AS media_por_dia
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY ano, semana
ORDER BY ano, semana;


-- ================================================================
-- 🔷 QUERY 9: TOP 10 DIAS COM MAIS SERVIÇOS
-- ================================================================
SELECT 
    data_servico,
    FORMAT_DATE('%d/%m/%Y (%A)', data_servico) AS data_completa,
    COUNT(*) AS total_servicos,
    STRING_AGG(DISTINCT polo, ', ') AS polos,
    COUNT(DISTINCT equipe) AS equipes
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY data_servico
ORDER BY total_servicos DESC
LIMIT 10;


-- ================================================================
-- 🔷 QUERY 10: COMPARATIVO POR POLO E DATA
-- ================================================================
SELECT 
    data_servico,
    FORMAT_DATE('%d/%m', data_servico) AS data_curta,
    SUM(CASE WHEN polo = 'MARABA' THEN 1 ELSE 0 END) AS maraba,
    SUM(CASE WHEN polo = 'TUCURUI' THEN 1 ELSE 0 END) AS tucurui,
    SUM(CASE WHEN polo = 'PARAUAPEBAS' THEN 1 ELSE 0 END) AS parauapebas,
    SUM(CASE WHEN polo = 'REDENÇÃO' THEN 1 ELSE 0 END) AS redencao,
    COUNT(*) AS total
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY data_servico
ORDER BY data_servico;


-- ================================================================
-- 🔷 QUERY 11: RESUMO EXECUTIVO (Para relatório)
-- ================================================================
SELECT 
    'Total de Serviços' AS metrica,
    CAST(COUNT(*) AS STRING) AS valor
FROM `meu-projeto-manutencao.manutencao.servicos`

UNION ALL

SELECT 
    'Polos Ativos',
    CAST(COUNT(DISTINCT polo) AS STRING)
FROM `meu-projeto-manutencao.manutencao.servicos`

UNION ALL

SELECT 
    'Equipes Mobilizadas',
    CAST(COUNT(DISTINCT equipe) AS STRING)
FROM `meu-projeto-manutencao.manutencao.servicos`

UNION ALL

SELECT 
    'Período',
    CONCAT(
        FORMAT_DATE('%d/%m/%Y', MIN(data_servico)),
        ' a ',
        FORMAT_DATE('%d/%m/%Y', MAX(data_servico))
    )
FROM `meu-projeto-manutencao.manutencao.servicos`

UNION ALL

SELECT 
    'Média Diária',
    CAST(ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT data_servico), 1) AS STRING)
FROM `meu-projeto-manutencao.manutencao.servicos`;


-- ================================================================
-- 🔷 QUERY 12: DETALHES COMPLETOS (Tabela)
-- ================================================================
SELECT 
    ordem_servico AS `Ordem`,
    abrir_am AS `Tipo`,
    polo AS `Polo`,
    equipe AS `Equipe`,
    FORMAT_DATE('%d/%m/%Y', data_servico) AS `Data`,
    horario_inicio AS `Início`,
    horario_fim AS `Fim`,
    COALESCE(colaboradora_baixa, '-') AS `Baixa`,
    COALESCE(observacao, '-') AS `Observação`
FROM `meu-projeto-manutencao.manutencao.servicos`
ORDER BY data_servico DESC, polo, equipe;


-- ================================================================
-- 🔷 QUERY 13: PRODUTIVIDADE POR EQUIPE E MÊS
-- ================================================================
SELECT 
    equipe,
    polo,
    FORMAT_DATE('%Y-%m', data_servico) AS mes,
    FORMAT_DATE('%B %Y', data_servico) AS mes_nome,
    COUNT(*) AS servicos,
    COUNT(DISTINCT data_servico) AS dias,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT data_servico), 1) AS media_dia
FROM `meu-projeto-manutencao.manutencao.servicos`
GROUP BY equipe, polo, mes, mes_nome
ORDER BY mes DESC, servicos DESC;


-- ================================================================
-- 🔷 QUERY 14: ÚLTIMOS 7 DIAS vs SEMANA ANTERIOR
-- ================================================================
WITH ultimos_7_dias AS (
    SELECT COUNT(*) AS total
    FROM `meu-projeto-manutencao.manutencao.servicos`
    WHERE data_servico >= DATE_SUB((SELECT MAX(data_servico) FROM `meu-projeto-manutencao.manutencao.servicos`), INTERVAL 6 DAY)
),
semana_anterior AS (
    SELECT COUNT(*) AS total
    FROM `meu-projeto-manutencao.manutencao.servicos`
    WHERE data_servico >= DATE_SUB((SELECT MAX(data_servico) FROM `meu-projeto-manutencao.manutencao.servicos`), INTERVAL 13 DAY)
      AND data_servico < DATE_SUB((SELECT MAX(data_servico) FROM `meu-projeto-manutencao.manutencao.servicos`), INTERVAL 6 DAY)
)
SELECT 
    u.total AS ultimos_7_dias,
    s.total AS semana_anterior,
    u.total - s.total AS variacao,
    ROUND((u.total - s.total) * 100.0 / NULLIF(s.total, 0), 1) AS variacao_pct
FROM ultimos_7_dias u, semana_anterior s
