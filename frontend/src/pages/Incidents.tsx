import { useState, useEffect } from 'react'
import client from '../api/client'
import type { Incident } from '../types'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  FireIcon,
  BoltIcon,
  ClockIcon,
  UserIcon,
  DocumentTextIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'

const severityConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  critical: { label: 'Critical', color: 'bg-red-500', icon: <FireIcon className="w-3.5 h-3.5" /> },
  high: { label: 'High', color: 'bg-amber-500', icon: <ExclamationTriangleIcon className="w-3.5 h-3.5" /> },
  medium: { label: 'Medium', color: 'bg-blue-500', icon: <BoltIcon className="w-3.5 h-3.5" /> },
  low: { label: 'Low', color: 'bg-gray-500', icon: <ClockIcon className="w-3.5 h-3.5" /> },
}

const statusConfig: Record<string, { label: string; color: string }> = {
  open: { label: 'Open', color: 'bg-red-500' },
  investigating: { label: 'Investigating', color: 'bg-amber-500' },
  in_progress: { label: 'In Progress', color: 'bg-blue-500' },
  resolved: { label: 'Resolved', color: 'bg-emerald-500' },
  closed: { label: 'Closed', color: 'bg-gray-500' },
}

const priorityConfig: Record<string, { label: string; color: string }> = {
  P1: { label: 'P1', color: 'bg-red-600' },
  P2: { label: 'P2', color: 'bg-amber-600' },
  P3: { label: 'P3', color: 'bg-blue-600' },
  P4: { label: 'P4', color: 'bg-gray-600' },
}

const categoryLabels: Record<string, string> = {
  network: 'Network',
  server: 'Server',
  workstation: 'Workstation',
  application: 'Application',
  hardware: 'Hardware',
  security: 'Security',
  cloud: 'Cloud',
  other: 'Other',
}

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    fetchIncidents()
    const interval = setInterval(fetchIncidents, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchIncidents = async () => {
    try {
      const res = await client.get('/api/incidents?limit=500')
      setIncidents(res.data)
    } catch (err) {
      console.error('Failed to fetch incidents:', err)
    } finally {
      setLoading(false)
    }
  }

  const filteredIncidents = incidents
    .filter(i => {
      const matchesSearch = i.incident_id.toLowerCase().includes(search.toLowerCase()) ||
        i.title.toLowerCase().includes(search.toLowerCase()) ||
        i.description?.toLowerCase().includes(search.toLowerCase()) ||
        i.assigned_technician?.toLowerCase().includes(search.toLowerCase())
      const matchesStatus = filterStatus === 'all' || i.status === filterStatus
      const matchesSeverity = filterSeverity === 'all' || i.severity === filterSeverity
      const matchesCategory = filterCategory === 'all' || i.category === filterCategory
      return matchesSearch && matchesStatus && matchesSeverity && matchesCategory
    })
    .sort((a, b) => new Date(b.detected_at).getTime() - new Date(a.detected_at).getTime())

  const statuses = ['open', 'investigating', 'in_progress', 'resolved', 'closed']
  const severities = ['critical', 'high', 'medium', 'low']
  const categories = [...new Set(incidents.map(i => i.category))].sort()

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading incidents...</p>
      </div>
    )
  }

  const stats = {
    total: incidents.length,
    open: incidents.filter(i => i.status === 'open').length,
    investigating: incidents.filter(i => i.status === 'investigating').length,
    in_progress: incidents.filter(i => i.status === 'in_progress').length,
    resolved: incidents.filter(i => i.status === 'resolved').length,
    critical: incidents.filter(i => i.severity === 'critical' && !['resolved', 'closed'].includes(i.status)).length,
  }

  return (
    <div className="dashboard">
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">Incident Management</h1>
          <span className="page-subtitle">
            {stats.total} total • {stats.open + stats.investigating + stats.in_progress} active • {stats.critical} critical
          </span>
        </div>
        <button className="btn-primary">
          <PlusIcon className="w-3.5 h-3.5 mr-2" />
          Create Incident
        </button>
      </div>

      <div className="status-cards-grid">
        <div className="status-card status-card-danger">
          <div className="status-card-header">
            <div className="status-card-icon"><FireIcon className="w-3.5 h-3.5" /></div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{stats.critical}</span>
            <span className="status-card-title">Critical Active</span>
          </div>
        </div>
        <div className="status-card status-card-warning">
          <div className="status-card-header">
            <div className="status-card-icon"><ExclamationTriangleIcon className="w-3.5 h-3.5" /></div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{stats.open + stats.investigating + stats.in_progress - stats.critical}</span>
            <span className="status-card-title">Other Active</span>
          </div>
        </div>
        <div className="status-card status-card-success">
          <div className="status-card-header">
            <div className="status-card-icon"><CheckCircleIcon className="w-3.5 h-3.5" /></div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{stats.resolved}</span>
            <span className="status-card-title">Resolved</span>
          </div>
        </div>
        <div className="status-card status-card-info">
          <div className="status-card-header">
            <div className="status-card-icon"><ClockIcon className="w-3.5 h-3.5" /></div>
          </div>
          <div className="status-card-body">
            <span className="status-card-value">{stats.total}</span>
            <span className="status-card-title">Total Incidents</span>
          </div>
        </div>
      </div>

      <div className="filters-bar">
        <div className="search-box">
          <MagnifyingGlassIcon className="w-4 h-4" />
          <input
            type="text"
            placeholder="Search incident ID, title, description, technician..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="filter-select">
            <option value="all">All Status</option>
            {statuses.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1).replace('_', ' ')}</option>)}
          </select>
          <select value={filterSeverity} onChange={e => setFilterSeverity(e.target.value)} className="filter-select">
            <option value="all">All Severity</option>
            {severities.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>
          <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)} className="filter-select">
            <option value="all">All Categories</option>
            {categories.map(c => <option key={c} value={c}>{categoryLabels[c] || c}</option>)}
          </select>
          <button className="btn-secondary" onClick={() => { setSearch(''); setFilterStatus('all'); setFilterSeverity('all'); setFilterCategory('all') }}>
            <ArrowPathIcon className="w-3.5 h-3.5 mr-1" />
            Reset
          </button>
        </div>
      </div>

      <div className="infrastructure-section">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Category</th>
                <th>Asset</th>
                <th>Technician</th>
                <th>Detected</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredIncidents.length > 0 ? (
                filteredIncidents.map(incident => (
                  <React.Fragment key={incident.id}>
                    <tr className={expandedId === incident.id ? 'expanded' : ''} onClick={() => setExpandedId(expandedId === incident.id ? null : incident.id)}>
                      <td className="font-mono font-medium">{incident.incident_id}</td>
                      <td className="font-medium max-w-xs truncate">{incident.title}</td>
                      <td>
                        <span className={`severity-badge ${severityConfig[incident.severity]?.color || 'bg-gray-500'}`}>
                          {severityConfig[incident.severity]?.icon}
                          {severityConfig[incident.severity]?.label}
                        </span>
                      </td>
                      <td>
                        <span className={`priority-badge ${priorityConfig[incident.priority]?.color || 'bg-gray-500'}`}>
                          {priorityConfig[incident.priority]?.label}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${statusConfig[incident.status]?.color || 'bg-gray-500'}`}>
                          {statusConfig[incident.status]?.label}
                        </span>
                      </td>
                      <td><span className="category-badge">{categoryLabels[incident.category] || incident.category}</span></td>
                      <td className="font-mono text-sm">{incident.asset_id}</td>
                      <td>{incident.assigned_technician || <span className="text-slate-500">Unassigned</span>}</td>
                      <td className="text-sm text-slate-400">{new Date(incident.detected_at).toLocaleString()}</td>
                      <td>
                        <div className="action-buttons">
                          <button className="action-btn" title="View">
                            <MagnifyingGlassIcon className="w-3.5 h-3.5" />
                          </button>
                          <button className="action-btn" title="Edit">
                            <PencilIcon className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                    {expandedId === incident.id && (
                      <tr className="expanded-row">
                        <td colSpan={10} className="expanded-content">
                          <div className="expanded-grid">
                            <div>
                              <label>Description</label>
                              <p>{incident.description || 'No description'}</p>
                            </div>
                            <div>
                              <label>Root Cause</label>
                              <p>{incident.root_cause || 'Not determined'}</p>
                            </div>
                            <div>
                              <label>Resolution Notes</label>
                              <p>{incident.resolution_notes || 'Not resolved'}</p>
                            </div>
                            <div>
                              <label>Production Impact</label>
                              <p>{incident.production_impact || 'Not assessed'}</p>
                            </div>
                            <div>
                              <label>Risk Score</label>
                              <p>{incident.risk_score !== null && incident.risk_score !== undefined ? incident.risk_score : 'Not calculated'}</p>
                            </div>
                            <div>
                              <label>Resolved At</label>
                              <p>{incident.resolved_at ? new Date(incident.resolved_at).toLocaleString() : 'Not resolved'}</p>
                            </div>
                          </div>
                          <div className="expanded-actions">
                            <button className="btn-secondary">
                              <PencilIcon className="w-3.5 h-3.5 mr-1" />
                              Edit
                            </button>
                            <button className="btn-secondary">
                              <DocumentTextIcon className="w-3.5 h-3.5 mr-1" />
                              View Timeline
                            </button>
                            <button className="btn-primary">
                              <CheckCircleIcon className="w-3.5 h-3.5 mr-1" />
                              Resolve
                            </button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="empty-cell">No incidents match your filters</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {filteredIncidents.length !== incidents.length && (
          <div className="table-footer">
            Showing {filteredIncidents.length} of {incidents.length} incidents
          </div>
        )}
      </div>
    </div>
  )
}