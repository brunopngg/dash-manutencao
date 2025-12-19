const Header = () => {
  return (
    <header className="bg-gradient-to-r from-[#0d2e5a] via-[#1a4d8f] to-[#2d6bb5] shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-4">
          <img 
            src="/logo-equatorial.png" 
            alt="Equatorial" 
            className="h-12 w-auto"
            onError={(e) => {
              e.target.style.display = 'none'
            }}
          />
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              Portal de Dashboards
            </h1>
            <p className="text-blue-200 text-sm">
              Grupo Equatorial - Análise de Dados
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
