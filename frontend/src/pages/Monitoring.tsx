import { useState, useEffect } from 'react'
import client from '../api/client'
import {
  SignalIcon,
  ServerStackIcon,
  GlobeAltIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

interface MonitoringResult {
  id: number
  asset_id: number
  check_type: string
  result: string
  response_time_ms: number | null
  packet_loss_percent: number | null
  status_code: number | null
  message: string | null
  checked_at: string
  asset_hostname?: string
}

interface Asset {
  id: number
  hostname: string
  ip_address: string
  asset_type: string
  status: string
  last_check: string | null
}

export default function Monitoring() {
  const [results, setResults] = useState<MonitoringResult[]>([])
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [resultsRes, assetsRes] = await Promise.all([
        client.get('/api/monitoring/results?limit=50'),
        client.get('/api/assets?limit=100'),
      ])
      setResults(resultsRes.data)
      setAssets(assetsRes.data)
      setLastUpdated(new Date())
    } catch (err) {
      console.error('Failed to fetch monitoring data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getResultIcon = (result: string) => {
    switch (result) {
      case 'success':
        return <CheckCircleIcon className="w-4 h-4 text-emerald-500" />
      case 'failure':
        return <XCircleIcon className="w-4 h-4 text-red-500" />
      case 'timeout':
        return <ExclamationTriangleIcon className="w-4 h-4 text-amber-500" />
      default:
        return <ClockIcon className="w-4 h-4 text-slate-500" />
    }
  }

  const getCheckTypeIcon = (type: string) => {
    switch (type) {
      case 'icmp':
        return <SignalIcon className="w-4 h-4" />
      case 'tcp':
        return <ServerStackIcon className="w-4 h-4" />
      case 'http':
        return <GlobeAltIcon className="w-4 h-4" />
      default:
        return <ClockIcon className="w-4 h-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-emerald-500'
      case 'offline':
        return 'bg-red-500'
      case 'warning':
        return 'bg-amber-500'
      default:
        return 'bg-slate-500'
    }
  }

  const filteredResults = filter === 'all'
    ? results
    : results.filter(r => r.check_type === filter)

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading monitoring data...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* Summary Cards */}
      <div className="status-cards-grid">
        <div className="status-card status-card-info">
          <div className="status-card-header">
            <div className="status-card-icon">
              <SignalIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{results.filter(r => r.check_type === 'icmp').length}</span>
            <span className="status-card-title">ICMP Checks</span>
            <span className="status-card-subtitle">Ping monitoring</span>
          </div>
        </div>

        <div className="status-card status-card-success">
          <div className="status-card-header">
            <div className="status-card-icon">
              <ServerStackIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{results.filter(r => r.check_type === 'tcp').length}</span>
            <span className="status-card-title">TCP Checks</span>
            <span className="status-card-subtitle">Port availability</span>
          </div>
        </div>

        <div className="status-card status-card-warning">
          <div className="status-card-header">
            <div className="status-card-icon">
              <GlobeAltIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{results.filter(r => r.check_type === 'http').length}</span>
            <span className="status-card-title">HTTP Checks</span>
            <span className="status-card-subtitle">Web health</span>
          </div>
        </div>

        <div className="status-card status-card-danger">
          <div className="status-card-header">
            <div className="status-card-icon">
              <XCircleIcon className="w-4 h-4" />
            </div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{results.filter(r => r.result === 'failure' || r.result === 'timeout').length}</span>
            <span className="status-card-title">Failures</span>
            <span className="status-card-subtitle">Requires attention</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        <button
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All Checks
        </button>
        <button
          className={`filter-tab ${filter === 'icmp' ? 'active' : ''}`}
          onClick={() => setFilter('icmp')}
        >
          ICMP
        </button>
        <button
          className={`filter-tab ${filter === 'tcp' ? 'active' : ''}`}
          onClick={() => setFilter('tcp')}
        >
          TCP
        </button>
        <button
          className={`filter-tab ${filter === 'http' ? 'active' : ''}`}
          onClick={() => setFilter('http')}
        >
          HTTP
        </button>
      </div>

      {/* Monitoring Results Table */}
      <div className="infrastructure-section">
        <h3 className="section-title">Monitoring Results</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Check</th>
                <th>Result</th>
                <th>Response Time</th>
                <th>Packet Loss</th>
                <th>Message</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {filteredResults.length > 0 ? (
                filteredResults.map((result) => (
                  <tr key={result.id}>
                    <td className="font-medium">{result.asset_hostname || `Asset #${result.asset_id}`}</td>
                    <td>
                      <span className="check-type-badge">
                        {getCheckTypeIcon(result.check_type)}
                        {result.check_type.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <span className="result-badge">
                        {getResultIcon(result.result)}
                        {result.result}
                      </span>
                    </td>
                    <td>{result.response_time_ms ? `${result.response_time_ms.toFixed(1)}ms` : '—'}</td>
                    <td>{result.packet_loss_percent ? `${result.packet_loss_percent.toFixed(1)}%` : '—'}</td>
                    <td className="message-cell">{result.message || '—'}</td>
                    <td className="time-cell">{new Date(result.checked_at).toLocaleTimeString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="empty-cell">
                    No monitoring results yet. The monitoring engine will populate this data.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Asset Status Overview */}
      <div className="infrastructure-section">
        <h3 className="section-title">Asset Status Overview</h3>
        <div className="assets-grid">
          {assets.slice(0, 20).map((asset) => (
            <div key={asset.id} className="asset-status-card">
              <div className="asset-status-header">
                <span className={`status-dot ${getStatusColor(asset.status)}`}></span>
                <span className="asset-hostname">{asset.hostname}</span>
              </div>
              <div className="asset-status-body">
                <span className="asset-ip">{asset.ip_address}</span>
                <span className="asset-type">{asset.asset_type.replace('_', ' ')}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
        <span>Auto-refresh: 10s</span>
      </div>
    </div>
  )
}
