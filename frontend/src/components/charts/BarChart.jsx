import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = ['#0d2e5a', '#1a4d8f', '#2d6bb5', '#4a90d9', '#6bb3fa', '#8ec8ff', '#b1dcff']

const BarChartComponent = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <XAxis 
          dataKey="name" 
          angle={-45} 
          textAnchor="end" 
          interval={0}
          tick={{ fontSize: 11, fill: '#1a4d8f' }}
        />
        <YAxis tick={{ fill: '#1a4d8f' }} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '2px solid #1a4d8f',
            borderRadius: '8px'
          }}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default BarChartComponent
