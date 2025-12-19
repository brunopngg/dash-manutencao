import { XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart, CartesianGrid } from 'recharts'

const LineChartComponent = ({ data, compact = false }) => {
  const height = compact ? 220 : 280
  
  // Pegar apenas os últimos 30 pontos se houver muitos dados
  const displayData = data.length > 30 ? data.slice(-30) : data
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={displayData} margin={{ top: 20, right: 20, left: 10, bottom: 20 }}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1a4d8f" stopOpacity={0.4}/>
            <stop offset="95%" stopColor="#1a4d8f" stopOpacity={0.05}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 10, fill: '#64748b' }}
          tickFormatter={(date) => {
            const d = new Date(date)
            return `${d.getDate()}/${d.getMonth() + 1}`
          }}
          interval="preserveStartEnd"
          axisLine={{ stroke: '#e2e8f0' }}
          tickLine={{ stroke: '#e2e8f0' }}
        />
        <YAxis 
          tick={{ fontSize: 10, fill: '#64748b' }} 
          axisLine={{ stroke: '#e2e8f0' }}
          tickLine={{ stroke: '#e2e8f0' }}
        />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
          }}
          labelFormatter={(date) => {
            const d = new Date(date)
            return d.toLocaleDateString('pt-BR')
          }}
        />
        <Area 
          type="monotone" 
          dataKey="value" 
          stroke="#1a4d8f" 
          strokeWidth={2.5}
          fillOpacity={1}
          fill="url(#colorValue)"
          dot={false}
          activeDot={{ fill: '#1a4d8f', strokeWidth: 2, r: 5, stroke: '#fff' }}
          animationDuration={800}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export default LineChartComponent
