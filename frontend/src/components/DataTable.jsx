import { useState, useMemo } from 'react'

const DataTable = ({ data }) => {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const rowsPerPage = 20

  const filteredData = useMemo(() => {
    if (!search) return data
    const searchLower = search.toLowerCase()
    return data.filter(row => 
      Object.values(row).some(val => 
        String(val).toLowerCase().includes(searchLower)
      )
    )
  }, [data, search])

  const paginatedData = useMemo(() => {
    return filteredData.slice(page * rowsPerPage, (page + 1) * rowsPerPage)
  }, [filteredData, page])

  const totalPages = Math.ceil(filteredData.length / rowsPerPage)

  const formatDate = (date) => {
    if (!date) return '-'
    return date.toLocaleDateString('pt-BR')
  }

  return (
    <div>
      {/* Busca */}
      <div className="mb-6">
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
          <input
            type="text"
            placeholder="Buscar nos dados..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0) }}
            className="w-full md:w-80 bg-gray-50 border-2 border-gray-200 rounded-xl pl-12 pr-4 py-3 focus:outline-none focus:border-[#1a4d8f] focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Tabela */}
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gradient-to-r from-[#0d2e5a] to-[#1a4d8f] text-white">
              <th className="px-5 py-4 text-left font-semibold">Ordem</th>
              <th className="px-5 py-4 text-left font-semibold">Polo</th>
              <th className="px-5 py-4 text-left font-semibold">Equipe</th>
              <th className="px-5 py-4 text-left font-semibold">Data</th>
              <th className="px-5 py-4 text-left font-semibold">Hora Início</th>
              <th className="px-5 py-4 text-left font-semibold">Hora Fim</th>
              <th className="px-5 py-4 text-left font-semibold">Baixa</th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, idx) => (
              <tr key={idx} className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'} hover:bg-blue-50 transition-colors`}>
                <td className="px-5 py-3 border-b border-gray-100 font-medium text-[#0d2e5a]">{row['NOTA'] || '-'}</td>
                <td className="px-5 py-3 border-b border-gray-100">{row.POLO}</td>
                <td className="px-5 py-3 border-b border-gray-100">
                  <span className="px-2 py-1 bg-[#1a4d8f]/10 text-[#1a4d8f] rounded-lg text-xs font-medium">{row.EQUIPE}</span>
                </td>
                <td className="px-5 py-3 border-b border-gray-100">{formatDate(row.DATA_SERVICO)}</td>
                <td className="px-5 py-3 border-b border-gray-100">{row['HORÁRIO INÍCIO'] || '-'}</td>
                <td className="px-5 py-3 border-b border-gray-100">{row['HORÁRIO FIM'] || '-'}</td>
                <td className="px-5 py-3 border-b border-gray-100">
                  {row['COLABORADORA (BAIXA)'] ? (
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-lg text-xs font-medium">{row['COLABORADORA (BAIXA)']}</span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      <div className="flex items-center justify-between mt-6">
        <span className="text-gray-500 text-sm">
          Mostrando <span className="font-semibold text-[#0d2e5a]">{page * rowsPerPage + 1}</span> - <span className="font-semibold text-[#0d2e5a]">{Math.min((page + 1) * rowsPerPage, filteredData.length)}</span> de <span className="font-semibold text-[#0d2e5a]">{filteredData.length}</span>
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-5 py-2.5 bg-gradient-to-r from-[#1a4d8f] to-[#2d6bb5] text-white rounded-xl disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/30 transition-all font-medium"
          >
            Anterior
          </button>
          <span className="px-5 py-2.5 text-gray-600 font-medium">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-5 py-2.5 bg-gradient-to-r from-[#1a4d8f] to-[#2d6bb5] text-white rounded-xl disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/30 transition-all font-medium"
          >
            Próximo
          </button>
        </div>
      </div>
    </div>
  )
}

export default DataTable
