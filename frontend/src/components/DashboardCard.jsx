const DashboardCard = ({ dashboard }) => {
  const handleClick = () => {
    window.open(dashboard.url, '_blank')
  }

  return (
    <div 
      onClick={handleClick}
      className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer overflow-hidden group hover:-translate-y-2"
    >
      {/* Header colorido */}
      <div className={`bg-gradient-to-r ${dashboard.color} p-6 relative`}>
        <div className="flex justify-between items-start">
          <span className="text-5xl">{dashboard.icon}</span>
          <div className="bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1">
            <span className="text-white text-sm font-medium">
              {dashboard.stats.value} {dashboard.stats.label}
            </span>
          </div>
        </div>
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-all" />
      </div>

      {/* Conteúdo */}
      <div className="p-6">
        <h3 className="text-xl font-bold text-[#0d2e5a] mb-2 group-hover:text-[#1a4d8f] transition-colors">
          {dashboard.title}
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed mb-4">
          {dashboard.description}
        </p>
        
        {/* Botão de acesso */}
        <div className="flex items-center justify-between">
          <span className="text-[#1a4d8f] font-medium text-sm flex items-center gap-2 group-hover:gap-3 transition-all">
            Acessar Dashboard
            <svg 
              className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
          <div className="w-8 h-8 rounded-full bg-[#1a4d8f]/10 flex items-center justify-center group-hover:bg-[#1a4d8f] transition-colors">
            <svg 
              className="w-4 h-4 text-[#1a4d8f] group-hover:text-white transition-colors" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardCard
