import { useMemo } from 'react'

// Mini Sparkline Component
const Sparkline = ({ data, color = '#fff' }) => {
  if (!data || data.length < 2) return null
  
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  
  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * 60
    const y = 20 - ((value - min) / range) * 18
    return `${x},${y}`
  }).join(' ')
  
  return (
    <svg width="60" height="24" className="opacity-60">
      <polyline
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        points={points}
      />
    </svg>
  )
}

// Gradientes para cada tipo de KPI
const GRADIENTS = {
  '📋': 'from-blue-600 to-indigo-700',
  '🏢': 'from-emerald-500 to-teal-600',
  '👥': 'from-violet-500 to-purple-600',
  '✅': 'from-amber-500 to-orange-600',
  'default': 'from-[#1a4d8f] to-[#0d2e5a]'
}

const KPICard = ({ title, value, icon, trend, sparklineData }) => {
  const gradient = GRADIENTS[icon] || GRADIENTS.default
  
  // Calcula tendência
  const trendInfo = useMemo(() => {
    if (trend === undefined) return null
    const isPositive = trend >= 0
    return {
      isPositive,
      text: `${isPositive ? '+' : ''}${trend.toFixed(1)}%`,
      icon: isPositive ? '↑' : '↓'
    }
  }, [trend])

  return (
    <div className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${gradient} p-5`}>
      {/* Padrão de fundo */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-white/20"></div>
        <div className="absolute -left-4 -bottom-4 w-24 h-24 rounded-full bg-white/10"></div>
      </div>
      
      {/* Conteúdo */}
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <p className="text-white/80 text-sm font-medium mb-1">{title}</p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold text-white">{value}</p>
              {trendInfo && (
                <span className={`text-sm font-medium ${trendInfo.isPositive ? 'text-green-300' : 'text-red-300'}`}>
                  {trendInfo.icon} {trendInfo.text}
                </span>
              )}
            </div>
          </div>
          <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <span className="text-2xl">{icon}</span>
          </div>
        </div>
        
        {/* Sparkline */}
        {sparklineData && sparklineData.length > 0 && (
          <div className="mt-2 pt-2 border-t border-white/20">
            <Sparkline data={sparklineData} color="#fff" />
          </div>
        )}
      </div>
    </div>
  )
}

export default KPICard
