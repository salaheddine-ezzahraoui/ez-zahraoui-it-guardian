import { useState, useEffect } from 'react'
import client from '../api/client'
import StatusCard from '../components/StatusCard'
import type { DashboardStats } from '../types'
import {
  ComputerDesktopIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  BoltIcon,
  FireIcon,
  SignalIcon,
  ServerStackIcon,
  BuildingOffice2Icon,
  WifiIcon,
} from '@heroicons/react/24/outline'

interface Event {
  id: number
  event_type: string
  message: string
  created_at: string
}

interface ProductionLine {
  line: string
  total: number
  online: number
  offline: number
  warning: number
  health: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [productionLines, setProductionLines] = useState<ProductionLine[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, 15000)
    return () => clearInterval(interval)
  }, [])

  const fetchAllData = async () => {
    try {
      const [statsRes, eventsRes, linesRes] = await Promise.all([
        client.get('/api/dashboard/stats'),
        client.get('/api/events'),
        client.get('/api/production-lines'),
      ])
      setStats(statsRes.data)
      setEvents(eventsRes.data)
      setProductionLines(linesRes.data)
      setError(null)
      setLastUpdated(new Date())
    } catch (err) {
      setError('API unavailable — showing last known data')
    } finally {
      setLoading(false)
    }
  }

  const getEventDotClass = (eventType: string) => {
    switch (eventType) {
      case 'incident_created':
        return 'critical'
      case 'incident_updated':
        return 'warning'
      case 'incident_resolved':
        return 'success'
      case 'monitoring_check':
        return 'info'
      default:
        return 'info'
    }
  }

  const formatTimeAgo = (dateStr: string) => {
    const now = new Date()
    const then = new Date(dateStr)
    const diffMs = now.getTime() - then.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    return `${Math.floor(diffHours / 24)}d ago`
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading operations data...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* Health Score Section */}
      <div className="health-section">
        <div className="health-score-card">
          <div className="health-score-header">
            <h2>Production Health</h2>
            <span className="health-score-trend">Live</span>
          </div>
          <div className="health-score-value">
            <span className="score-number">{stats?.overall_health ?? 0}</span>
            <span className="score-divider">/</span>
            <span className="score-total">100</span>
          </div>
          <div className="health-score-bar">
            <div
              className="health-score-fill"
              style={{ width: `${stats?.overall_health ?? 0}%` }}
            ></div>
          </div>
          <div className="health-score-labels">
            <span>Critical</span>
            <span>Warning</span>
            <span>Healthy</span>
          </div>
        </div>

        <div className="health-score-card">
          <div className="health-score-header">
            <h2>IT Risk Score</h2>
            <span className={`risk-badge risk-${(stats?.risk_band ?? 'LOW').toLowerCase()}`}>
              {stats?.risk_band ?? 'LOW'}
            </span>
          </div>
          <div className="health-score-value">
            <span className="score-number">{stats?.risk_score ?? 0}</span>
            <span className="score-divider">/</span>
            <span className="score-total">100</span>
          </div>
          <div className="health-score-bar">
            <div
              className={`risk-score-fill risk-${(stats?.risk_band ?? 'LOW').toLowerCase()}`}
              style={{ width: `${stats?.risk_score ?? 0}%` }}
            ></div>
          </div>
          <div className="health-score-labels">
            <span>0-30 Low</span>
            <span>31-60 Med</span>
            <span>61-80 High</span>
            <span>81-100 Crit</span>
          </div>
        </div>
      </div>

      {/* Asset Status Cards */}
      <div className="status-cards-grid">
        <StatusCard
          title="Total Assets"
          value={stats?.total_assets ?? 0}
          subtitle="All monitored devices"
          variant="info"
          icon={<ComputerDesktopIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="Online"
          value={stats?.online_assets ?? 0}
          subtitle="Responding to checks"
          variant="success"
          icon={<CheckCircleIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="Warning"
          value={stats?.warning_assets ?? 0}
          subtitle="Degraded performance"
          variant="warning"
          icon={<ExclamationTriangleIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="Offline"
          value={stats?.offline_assets ?? 0}
          subtitle="Not responding"
          variant="danger"
          icon={<XCircleIcon className="w-4 h-4" />}
        />
      </div>

      {/* Incident Cards */}
      <div className="status-cards-grid">
        <StatusCard
          title="Active Incidents"
          value={stats?.active_incidents ?? 0}
          subtitle="Requires attention"
          variant="info"
          icon={<BoltIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="Critical"
          value={stats?.critical_incidents ?? 0}
          subtitle="Immediate action required"
          variant="danger"
          icon={<FireIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="High"
          value={stats?.high_incidents ?? 0}
          subtitle="Urgent attention needed"
          variant="warning"
          icon={<ExclamationTriangleIcon className="w-4 h-4" />}
        />
        <StatusCard
          title="Medium"
          value={stats?.medium_incidents ?? 0}
          subtitle="Standard priority"
          variant="default"
          icon={<SignalIcon className="w-4 h-4" />}
        />
      </div>

      {/* Infrastructure Health */}
      <div className="infrastructure-section">
        <h3 className="section-title">Infrastructure Health</h3>
        <div className="infrastructure-grid">
          <div className="infra-card">
            <div className="infra-card-header">
              <span className="infra-icon network">
                <WifiIcon className="w-3.5 h-3.5" />
              </span>
              <span className="infra-label">Network</span>
            </div>
            <div className="infra-value">{stats?.network_health ?? 0}%</div>
            <div className="infra-bar">
              <div className="infra-bar-fill" style={{ width: `${stats?.network_health ?? 0}%` }}></div>
            </div>
          </div>

          <div className="infra-card">
            <div className="infra-card-header">
              <span className="infra-icon server">
                <ServerStackIcon className="w-3.5 h-3.5" />
              </span>
              <span className="infra-label">Servers</span>
            </div>
            <div className="infra-value">{stats?.server_health ?? 0}%</div>
            <div className="infra-bar">
              <div className="infra-bar-fill" style={{ width: `${stats?.server_health ?? 0}%` }}></div>
            </div>
          </div>

          <div className="infra-card">
            <div className="infra-card-header">
              <span className="infra-icon production">
                <BuildingOffice2Icon className="w-3.5 h-3.5" />
              </span>
              <span className="infra-label">Production</span>
            </div>
            <div className="infra-value">{stats?.production_health ?? 0}%</div>
            <div className="infra-bar">
              <div className="infra-bar-fill" style={{ width: `${stats?.production_health ?? 0}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Production Lines */}
      {productionLines.length > 0 && (
        <div className="infrastructure-section">
          <h3 className="section-title">Production Lines</h3>
          <div className="infrastructure-grid">
            {productionLines.map((line) => (
              <div key={line.line} className="infra-card">
                <div className="infra-card-header">
                  <span className="infra-icon production">
                    <BuildingOffice2Icon className="w-3.5 h-3.5" />
                  </span>
                  <span className="infra-label">{line.line}</span>
                </div>
                <div className="infra-value">{line.health}%</div>
                <div className="infra-bar">
                  <div
                    className="infra-bar-fill"
                    style={{ width: `${line.health}%` }}
                  ></div>
                </div>
                <div className="production-line-stats">
                  <span>{line.online}/{line.total} online</span>
                  {line.offline > 0 && <span className="text-danger">{line.offline} offline</span>}
                  {line.warning > 0 && <span className="text-warning">{line.warning} warning</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Events */}
      <div className="events-section">
        <h3 className="section-title">Recent Events</h3>
        <div className="events-list">
          {events.length > 0 ? (
            events.slice(0, 10).map((event) => (
              <div key={event.id} className="event-item">
                <span className={`event-dot ${getEventDotClass(event.event_type)}`}></span>
                <div className="event-content">
                  <span className="event-message">{event.message}</span>
                  <span className="event-time">{formatTimeAgo(event.created_at)}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="no-events">No recent events</div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
        {error && <span className="connection-warning">{error}</span>}
      </div>
    </div>
  )
}
