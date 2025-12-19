import { Link } from 'react-router-dom'

const Header = () => {
  return (
    <header className="relative overflow-hidden">
      {/* Background com gradiente */}
      <div className="absolute inset-0 bg-gradient-to-r from-[#0d2e5a] via-[#1a4d8f] to-[#2d6bb5]"></div>
      
      <div className="relative container mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-4 group">
            <img 
              src="/logo-equatorial.png" 
              alt="Equatorial" 
              className="h-12 w-auto brightness-0 invert"
              onError={(e) => {
                e.target.style.display = 'none'
              }}
            />
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
                Portal de Dashboards
              </h1>
              <p className="text-blue-200/80 text-sm font-medium">
                Grupo Equatorial • Análise de Dados
              </p>
            </div>
          </Link>
          
          {/* Status indicator */}
          <div className="hidden md:flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
            <span className="text-white/90 text-sm">Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
