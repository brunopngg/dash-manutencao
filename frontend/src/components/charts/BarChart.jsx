import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'

const COLORS = ['#0d2e5a', '#1a4d8f', '#2d6bb5', '#4a90d9', '#6bb3fa', '#8ec8ff', '#b1dcff']

const BarChartComponent = ({ data, compact = false }) => {
  const height = compact ? 250 : 320
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 25, right: 20, left: 10, bottom: compact ? 40 : 55 }}>
        <XAxis 
          dataKey="name" 
          angle={-45} 
          textAnchor="end" 
          interval={0}
          tick={{ fontSize: 10, fill: '#64748b' }}
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
          cursor={{ fill: 'rgba(26, 77, 143, 0.1)' }}
        />
        <Bar dataKey="value" radius={[6, 6, 0, 0]} animationDuration={800}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
          <LabelList 
            dataKey="value" 
            position="top" 
            fill="#374151" 
            fontSize={11} 
            fontWeight="600"
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default BarChartComponent
