import Dashboard from './components/Dashboard'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Dashboard />
      </main>
      <footer className="text-center py-6 text-[#1a4d8f]">
        <p>© 2024 Grupo Equatorial - Todos os direitos reservados</p>
      </footer>
    </div>
  )
}

export default App
