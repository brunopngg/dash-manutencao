import { useState, useEffect, useMemo } from 'react'
import Papa from 'papaparse'
import { Link } from 'react-router-dom'
import KPICard from '../components/KPICard'
import BarChartComponent from '../components/charts/BarChart'
import PieChartComponent from '../components/charts/PieChart'
import LineChartComponent from '../components/charts/LineChart'
import DataTable from '../components/DataTable'
import Filters from '../components/Filters'

const Manutencao = () => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    ano: 'Todos',
    mes: 'Todos',
    polo: 'Todos',
    equipe: 'Todas'
  })

  // URL do Google Sheets (exportar como CSV)
  const GOOGLE_SHEETS_URL = 'https://docs.google.com/spreadsheets/d/1LChFOFxxBUY4hpQz2K4lZS6oC-NVhIBAqgCVYyKZZHw/export?format=csv&gid=0'

  // Mapeamento para normalizar POLO
  const mapeamentoPolo = {
    'MARABA': 'MARABÁ',
    'MARABÃ': 'MARABÁ',
    'CANAA': 'CANAÃ',
    'CANAÃ': 'CANAÃ',
    'JACUNDA': 'JACUNDÁ',
    'JACUNDÃ': 'JACUNDÁ',
    'TUCURUI': 'TUCURUÍ',
    'TUCURUÃ': 'TUCURUÍ',
    'REDENÃÃO': 'REDENÇÃO',
    'REDENCAO': 'REDENÇÃO',
    'REDEÃÃO': 'REDENÇÃO',
  }

  const [ultimaAtualizacao, setUltimaAtualizacao] = useState(null)

  // Função para carregar dados do Google Sheets
  const carregarDados = () => {
    fetch(GOOGLE_SHEETS_URL)
      .then(response => response.text())
      .then(csvText => {
        Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const processedData = results.data
              .map(row => {
                // Normalizar POLO
                let polo = (row['POLO'] || '').trim().toUpperCase()
                polo = mapeamentoPolo[polo] || polo

                // Normalizar EQUIPE
                let equipe = (row['EQUIPE'] || '').trim().toUpperCase().replace(/\s+/g, '')

                // Processar data
                const dataServico = row['DATA DO SERVIÇO']
                let dataObj = null
                if (dataServico) {
                  const parts = dataServico.split('/')
                  if (parts.length === 3) {
                    dataObj = new Date(parts[2], parts[1] - 1, parts[0])
                  }
                }

                return {
                  ...row,
                  POLO: polo,
                  EQUIPE: equipe,
                  DATA_SERVICO: dataObj,
                  ANO: dataObj ? dataObj.getFullYear() : null,
                  MES: dataObj ? dataObj.getMonth() + 1 : null
                }
              })
              .filter(row => row.DATA_SERVICO && row.POLO && row.ANO >= 2020 && row.ANO <= 2030)

            setData(processedData)
            setLoading(false)
            setUltimaAtualizacao(new Date())
          }
        })
      })
  }

  useEffect(() => {
    // Carrega dados na primeira vez
    carregarDados()

    // Atualiza automaticamente a cada 5 minutos (300000ms)
    const intervalo = setInterval(() => {
      carregarDados()
    }, 5 * 60 * 1000)

    // Limpa o intervalo quando o componente é desmontado
    return () => clearInterval(intervalo)
  }, [])

  // Filtrar dados
  const filteredData = useMemo(() => {
    return data.filter(row => {
      if (filters.ano !== 'Todos' && row.ANO !== parseInt(filters.ano)) return false
      if (filters.mes !== 'Todos' && row.MES !== parseInt(filters.mes)) return false
      if (filters.polo !== 'Todos' && row.POLO !== filters.polo) return false
      if (filters.equipe !== 'Todas' && row.EQUIPE !== filters.equipe) return false
      return true
    })
  }, [data, filters])

  // Opções de filtros
  const filterOptions = useMemo(() => {
    // Filtrar apenas anos válidos (entre 2020 e 2030)
    const anos = [...new Set(data.map(d => d.ANO).filter(ano => ano >= 2020 && ano <= 2030))].sort()
    const polos = [...new Set(data.map(d => d.POLO).filter(Boolean))].sort()
    const equipes = [...new Set(data.map(d => d.EQUIPE).filter(Boolean))].sort()
    return { anos, polos, equipes }
  }, [data])

  // KPIs
  const kpis = useMemo(() => {
    const total = filteredData.length
    const polosAtivos = new Set(filteredData.map(d => d.POLO)).size
    const equipesAtivas = new Set(filteredData.map(d => d.EQUIPE)).size
    const comBaixa = filteredData.filter(d => d['COLABORADORA (BAIXA)'] && d['COLABORADORA (BAIXA)'].trim()).length

    return { total, polosAtivos, equipesAtivas, comBaixa }
  }, [filteredData])

  // Sparkline data (últimos 7 dias)
  const sparklineData = useMemo(() => {
    const ultimos7Dias = []
    const hoje = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const dia = new Date(hoje)
      dia.setDate(dia.getDate() - i)
      dia.setHours(0, 0, 0, 0)
      
      const count = data.filter(row => {
        if (!row.DATA_SERVICO) return false
        const dataRow = new Date(row.DATA_SERVICO)
        dataRow.setHours(0, 0, 0, 0)
        return dataRow.getTime() === dia.getTime()
      }).length
      
      ultimos7Dias.push(count)
    }
    
    return ultimos7Dias
  }, [data])

  // Serviços do dia de hoje por equipe
  const servicosDoDia = useMemo(() => {
    const hoje = new Date()
    hoje.setHours(0, 0, 0, 0)
    
    const dadosHoje = data.filter(row => {
      if (!row.DATA_SERVICO) return false
      const dataRow = new Date(row.DATA_SERVICO)
      dataRow.setHours(0, 0, 0, 0)
      return dataRow.getTime() === hoje.getTime()
    })
    
    const porEquipe = Object.entries(
      dadosHoje.reduce((acc, row) => {
        acc[row.EQUIPE] = (acc[row.EQUIPE] || 0) + 1
        return acc
      }, {})
    ).map(([equipe, qtd]) => ({ equipe, qtd }))
     .sort((a, b) => b.qtd - a.qtd)
    
    return { total: dadosHoje.length, porEquipe }
  }, [data])

  // Dados para gráficos
  const chartData = useMemo(() => {
    // Por Polo
    const byPolo = Object.entries(
      filteredData.reduce((acc, row) => {
        acc[row.POLO] = (acc[row.POLO] || 0) + 1
        return acc
      }, {})
    ).map(([name, value]) => ({ name, value }))
     .sort((a, b) => b.value - a.value)

    // Por Equipe (top 15)
    const byEquipe = Object.entries(
      filteredData.reduce((acc, row) => {
        acc[row.EQUIPE] = (acc[row.EQUIPE] || 0) + 1
        return acc
      }, {})
    ).map(([name, value]) => ({ name, value }))
     .sort((a, b) => b.value - a.value)
     .slice(0, 15)

    // Por Data (timeline)
    const byDate = Object.entries(
      filteredData.reduce((acc, row) => {
        if (row.DATA_SERVICO) {
          const dateKey = row.DATA_SERVICO.toISOString().split('T')[0]
          acc[dateKey] = (acc[dateKey] || 0) + 1
        }
        return acc
      }, {})
    ).map(([date, value]) => ({ date, value }))
     .sort((a, b) => new Date(a.date) - new Date(b.date))

    return { byPolo, byEquipe, byDate }
  }, [filteredData])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#1a4d8f] border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div>
      {/* Breadcrumb */}
      <div className="mb-8">
        <Link to="/" className="inline-flex items-center gap-2 text-[#1a4d8f] hover:text-[#0d2e5a] font-medium transition-colors group">
          <svg className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Voltar ao Portal
        </Link>
      </div>

      {/* Título */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-400 flex items-center justify-center">
              <span className="text-2xl">🔧</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-[#0d2e5a] tracking-tight">Dashboard de Manutenção</h1>
              <p className="text-gray-500">Controle de Serviços e Equipes</p>
            </div>
          </div>
          {/* Indicador de atualização */}
          <div className="text-right">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Atualização automática: 5 min
            </div>
            {ultimaAtualizacao && (
              <p className="text-xs text-gray-400 mt-1">
                Última: {ultimaAtualizacao.toLocaleTimeString('pt-BR')}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Filtros */}
      <Filters 
        filters={filters} 
        setFilters={setFilters} 
        options={filterOptions}
      />

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <KPICard title="Total de Serviços" value={kpis.total.toLocaleString()} icon="📋" sparklineData={sparklineData} />
        <KPICard title="Polos Ativos" value={kpis.polosAtivos} icon="🏢" />
        <KPICard title="Equipes" value={kpis.equipesAtivas} icon="👥" />
        <KPICard title="Com Baixa" value={kpis.comBaixa.toLocaleString()} icon="✅" />
      </div>

      {/* Serviços do Dia */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-bold text-[#0d2e5a] flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white text-sm">📅</span>
            Serviços de Hoje
            <span className="text-xs font-normal text-gray-400">
              {new Date().toLocaleDateString('pt-BR')}
            </span>
          </h2>
          <span className="text-xl font-bold text-[#1a4d8f] bg-blue-50 px-3 py-1 rounded-lg">{servicosDoDia.total}</span>
        </div>
        
        {servicosDoDia.porEquipe.length > 0 ? (
          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
            {servicosDoDia.porEquipe.map(({ equipe, qtd }) => (
              <div 
                key={equipe} 
                className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg p-2 border border-slate-200"
              >
                <div className="text-[10px] text-slate-500 truncate font-medium" title={equipe}>{equipe}</div>
                <div className="text-lg font-bold text-[#0d2e5a]">{qtd}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6 text-gray-400">
            <span className="text-3xl mb-1 block">📭</span>
            <p className="text-sm">Nenhum serviço hoje</p>
          </div>
        )}
      </div>

      {/* Gráficos - Linha 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
              <span className="text-white text-sm">📊</span>
            </div>
            <h3 className="text-base font-bold text-[#0d2e5a]">Serviços por Polo</h3>
          </div>
          <BarChartComponent data={chartData.byPolo} compact />
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
              <span className="text-white text-sm">🥧</span>
            </div>
            <h3 className="text-base font-bold text-[#0d2e5a]">Distribuição por Polo</h3>
          </div>
          <PieChartComponent data={chartData.byPolo} compact />
        </div>
      </div>

      {/* Timeline e Equipes - Lado a lado */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
              <span className="text-white text-sm">📈</span>
            </div>
            <h3 className="text-base font-bold text-[#0d2e5a]">Evolução Diária</h3>
          </div>
          <LineChartComponent data={chartData.byDate} compact />
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
              <span className="text-white text-sm">👥</span>
            </div>
            <h3 className="text-base font-bold text-[#0d2e5a]">Top 15 Equipes</h3>
          </div>
          <BarChartComponent data={chartData.byEquipe} compact />
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-2xl border border-gray-200 p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
            <span className="text-white text-sm">📋</span>
          </div>
          <h3 className="text-base font-bold text-[#0d2e5a]">Dados Detalhados</h3>
        </div>
        <DataTable data={filteredData} />
      </div>
    </div>
  )
}

export default Manutencao
