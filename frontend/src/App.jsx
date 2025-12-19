import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Manutencao from './pages/Manutencao'
import Header from './components/Header'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/30">
        <Header />
        <main className="container mx-auto px-6 py-10">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/manutencao" element={<Manutencao />} />
          </Routes>
        </main>
        <footer className="text-center py-8 border-t border-gray-100 bg-white/50 backdrop-blur-sm">
          <p className="text-gray-500 text-sm">© 2024 Grupo Equatorial • Todos os direitos reservados</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
