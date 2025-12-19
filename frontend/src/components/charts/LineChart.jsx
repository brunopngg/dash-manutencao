import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

const LineChartComponent = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
        <defs>
          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1a4d8f" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#1a4d8f" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 10, fill: '#1a4d8f' }}
          tickFormatter={(date) => {
            const d = new Date(date)
            return `${d.getDate()}/${d.getMonth() + 1}`
          }}
          interval="preserveStartEnd"
        />
        <YAxis tick={{ fill: '#1a4d8f' }} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '2px solid #1a4d8f',
            borderRadius: '8px'
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
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorValue)"
          dot={{ fill: '#1a4d8f', strokeWidth: 2, r: 3 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export default LineChartComponent
