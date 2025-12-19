const meses = {
  1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
  5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
  9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}

const Filters = ({ filters, setFilters, options }) => {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-8">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#1a4d8f] to-[#2d6bb5] flex items-center justify-center">
          <span className="text-white text-lg">🎯</span>
        </div>
        <h3 className="text-lg font-bold text-[#0d2e5a]">Filtros</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Ano */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-gray-600">
            <span>📅</span> Ano
          </label>
          <select
            value={filters.ano}
            onChange={(e) => setFilters({ ...filters, ano: e.target.value })}
            className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-[#1a4d8f] focus:bg-white transition-all cursor-pointer hover:border-gray-300"
          >
            <option value="Todos">Todos os anos</option>
            {options.anos.map(ano => (
              <option key={ano} value={ano}>{ano}</option>
            ))}
          </select>
        </div>

        {/* Mês */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-gray-600">
            <span>🗓️</span> Mês
          </label>
          <select
            value={filters.mes}
            onChange={(e) => setFilters({ ...filters, mes: e.target.value })}
            className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-[#1a4d8f] focus:bg-white transition-all cursor-pointer hover:border-gray-300"
          >
            <option value="Todos">Todos os meses</option>
            {Object.entries(meses).map(([num, nome]) => (
              <option key={num} value={num}>{nome}</option>
            ))}
          </select>
        </div>

        {/* Polo */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-gray-600">
            <span>🏢</span> Polo
          </label>
          <select
            value={filters.polo}
            onChange={(e) => setFilters({ ...filters, polo: e.target.value })}
            className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-[#1a4d8f] focus:bg-white transition-all cursor-pointer hover:border-gray-300"
          >
            <option value="Todos">Todos os polos</option>
            {options.polos.map(polo => (
              <option key={polo} value={polo}>{polo}</option>
            ))}
          </select>
        </div>

        {/* Equipe */}
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-gray-600">
            <span>👥</span> Equipe
          </label>
          <select
            value={filters.equipe}
            onChange={(e) => setFilters({ ...filters, equipe: e.target.value })}
            className="w-full bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 focus:outline-none focus:border-[#1a4d8f] focus:bg-white transition-all cursor-pointer hover:border-gray-300"
          >
            <option value="Todas">Todas as equipes</option>
            {options.equipes.map(equipe => (
              <option key={equipe} value={equipe}>{equipe}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}

export default Filters
