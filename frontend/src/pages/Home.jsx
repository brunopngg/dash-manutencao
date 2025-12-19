import { Link } from 'react-router-dom'

// Lista de dashboards disponíveis
const dashboards = [
  {
    id: 1,
    title: 'Manutenção',
    description: 'Controle de serviços de manutenção, equipes e polos. Acompanhe indicadores de desempenho e produtividade.',
    icon: '🔧',
    gradient: 'from-blue-600 via-blue-500 to-cyan-400',
    path: '/manutencao',
    stats: {
      label: 'Serviços',
      value: '3.900+'
    }
  },
]

const Home = () => {
  return (
    <div className="py-4">
      <div className="mb-10">
        <h2 className="text-3xl font-bold text-[#0d2e5a] mb-3 tracking-tight">
          Dashboards Disponíveis
        </h2>
        <p className="text-gray-500 text-lg">
          Selecione um dashboard para visualizar os dados e análises
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {dashboards.map((dashboard) => (
          <Link key={dashboard.id} to={dashboard.path} className="group">
            <div className="relative bg-white rounded-3xl border border-gray-200 hover:border-[#1a4d8f] transition-all duration-500 cursor-pointer overflow-hidden">
              {/* Header com gradiente */}
              <div className={`relative bg-gradient-to-br ${dashboard.gradient} p-8 overflow-hidden`}>
                {/* Círculos decorativos */}
                <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
                <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
                
                <div className="relative flex justify-between items-start">
                  <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                    <span className="text-4xl">{dashboard.icon}</span>
                  </div>
                  <div className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                    <span className="text-white text-sm font-bold">
                      {dashboard.stats.value}
                    </span>
                    <span className="text-white/80 text-xs ml-1">
                      {dashboard.stats.label}
                    </span>
                  </div>
                </div>
              </div>

              {/* Conteúdo */}
              <div className="p-6">
                <h3 className="text-xl font-bold text-[#0d2e5a] mb-2 group-hover:text-[#1a4d8f] transition-colors">
                  {dashboard.title}
                </h3>
                <p className="text-gray-500 text-sm leading-relaxed mb-5">
                  {dashboard.description}
                </p>
                
                {/* Botão de acesso */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className="text-[#1a4d8f] font-semibold text-sm flex items-center gap-2">
                    Acessar Dashboard
                    <svg 
                      className="w-5 h-5 transform group-hover:translate-x-2 transition-transform duration-300" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}
        
        {/* Card para adicionar novo dashboard (placeholder) */}
        <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-dashed border-gray-300 rounded-3xl p-8 flex flex-col items-center justify-center text-gray-400 hover:border-[#1a4d8f] hover:text-[#1a4d8f] hover:from-blue-50 hover:to-indigo-50 transition-all duration-300 cursor-pointer min-h-[320px] group">
          <div className="w-16 h-16 rounded-2xl bg-gray-200 group-hover:bg-[#1a4d8f]/10 flex items-center justify-center mb-4 transition-colors">
            <span className="text-4xl">➕</span>
          </div>
          <span className="font-bold text-lg">Em breve</span>
          <span className="text-sm">Novos dashboards</span>
        </div>
      </div>
    </div>
  )
}

export default Home
