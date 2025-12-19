import DashboardCard from './DashboardCard'

// Lista de dashboards disponíveis
const dashboards = [
  {
    id: 1,
    title: 'Manutenção',
    description: 'Controle de serviços de manutenção, equipes e polos. Acompanhe indicadores de desempenho e produtividade.',
    icon: '🔧',
    color: 'from-blue-500 to-blue-700',
    url: 'http://localhost:8501', // URL do Streamlit
    stats: {
      label: 'Serviços',
      value: '3.900+'
    }
  },
  // Adicione mais dashboards aqui no futuro
  // {
  //   id: 2,
  //   title: 'Outro Dashboard',
  //   description: 'Descrição do dashboard',
  //   icon: '📊',
  //   color: 'from-green-500 to-green-700',
  //   url: 'http://localhost:8502',
  //   stats: { label: 'Registros', value: '1.000+' }
  // },
]

const Dashboard = () => {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-[#0d2e5a] mb-2">
          Dashboards Disponíveis
        </h2>
        <p className="text-gray-600">
          Selecione um dashboard para visualizar os dados e análises
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboards.map((dashboard) => (
          <DashboardCard key={dashboard.id} dashboard={dashboard} />
        ))}
        
        {/* Card para adicionar novo dashboard (placeholder) */}
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center text-gray-400 hover:border-[#1a4d8f] hover:text-[#1a4d8f] transition-all cursor-pointer min-h-[250px]">
          <span className="text-4xl mb-2">➕</span>
          <span className="font-medium">Em breve</span>
          <span className="text-sm">Novos dashboards</span>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
