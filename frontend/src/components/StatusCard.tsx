interface StatusCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
}

export default function StatusCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  trendValue,
  variant = 'default',
}: StatusCardProps) {
  return (
    <div className={`status-card status-card-${variant}`}>
      <div className="status-card-header">
        <div className="status-card-icon">{icon}</div>
        {trend && (
          <span className={`status-card-trend trend-${trend}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
          </span>
        )}
      </div>
      <div className="status-card-body">
        <span className="status-card-value">{value}</span>
        <span className="status-card-title">{title}</span>
        {subtitle && <span className="status-card-subtitle">{subtitle}</span>}
      </div>
    </div>
  )
}
