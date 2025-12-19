const KPICard = ({ title, value, icon }) => {
  return (
    <div className="group relative overflow-hidden">
      {/* Card principal */}
      <div className="relative bg-white rounded-2xl p-6 border border-gray-200 hover:border-[#1a4d8f] transition-all duration-300">
        {/* Gradiente de fundo no hover */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a4d8f] to-[#0d2e5a] opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
        
        {/* Conteúdo */}
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <p className="text-gray-500 group-hover:text-blue-200 text-sm font-medium mb-1 transition-colors">{title}</p>
            <p className="text-3xl font-bold text-[#0d2e5a] group-hover:text-white transition-colors">{value}</p>
          </div>
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#1a4d8f]/10 to-[#2d6bb5]/10 group-hover:from-white/20 group-hover:to-white/10 flex items-center justify-center transition-all">
            <span className="text-3xl">{icon}</span>
          </div>
        </div>
        
        {/* Barra inferior */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-[#1a4d8f] to-[#2d6bb5] transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left rounded-b-2xl"></div>
      </div>
    </div>
  )
}

export default KPICard
