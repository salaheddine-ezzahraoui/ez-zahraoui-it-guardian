import { useState, useEffect } from 'react'
import client from '../api/client'
import type { Asset } from '../types'
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
  ServerStackIcon,
  ComputerDesktopIcon,
  DevicePhoneMobileIcon,
  CpuChipIcon,
  BuildingOffice2Icon,
  PrinterIcon,
  GlobeAltIcon,
} from '@heroicons/react/24/outline'

const typeIcons: Record<string, React.ReactNode> = {
  production_pc: <ComputerDesktopIcon className="w-2 h-2" />,
  server: <ServerStackIcon className="w-2 h-2" />,
  switch: <CpuChipIcon className="w-2 h-2" />,
  router: <CpuChipIcon className="w-2 h-2" />,
  printer: <PrinterIcon className="w-2 h-2" />,
  application: <GlobeAltIcon className="w-2 h-2" />,
  network_service: <GlobeAltIcon className="w-2 h-2" />,
}

const typeLabels: Record<string, string> = {
  production_pc: 'Production PC',
  server: 'Server',
  switch: 'Switch',
  router: 'Router',
  printer: 'Printer',
  application: 'Application',
  network_service: 'Network Service',
}

const statusIcons: Record<string, React.ReactNode> = {
  online: <CheckCircleIcon className="w-3 h-3 text-emerald-500" />,
  warning: <ExclamationTriangleIcon className="w-3 h-3 text-amber-500" />,
  offline: <XCircleIcon className="w-3 h-3 text-red-500" />,
  maintenance: <ArrowPathIcon className="w-3 h-3 text-blue-500" />,
}

const statusLabels: Record<string, string> = {
  online: 'Online',
  warning: 'Warning',
  offline: 'Offline',
  maintenance: 'Maintenance',
}

const criticalityColors: Record<string, string> = {
  low: 'bg-gray-500',
  medium: 'bg-blue-500',
  high: 'bg-amber-500',
  critical: 'bg-red-500',
}

export default function Assets() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [sortField, setSortField] = useState<string>('hostname')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  useEffect(() => {
    fetchAssets()
  }, [])

  const fetchAssets = async () => {
    try {
      const res = await client.get('/api/assets?limit=500')
      setAssets(res.data)
    } catch (err) {
      console.error('Failed to fetch assets:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const filteredAssets = assets
    .filter(a => {
      const matchesSearch = a.hostname.toLowerCase().includes(search.toLowerCase()) ||
        a.ip_address.includes(search) ||
        a.production_line?.toLowerCase().includes(search.toLowerCase())
      const matchesType = filterType === 'all' || a.asset_type === filterType
      const matchesStatus = filterStatus === 'all' || a.status === filterStatus
      return matchesSearch && matchesType && matchesStatus
    })
    .sort((a, b) => {
      const aVal = a[sortField as keyof Asset]
      const bVal = b[sortField as keyof Asset]
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1
      const cmp = String(aVal).localeCompare(String(bVal))
      return sortDir === 'asc' ? cmp : -cmp
    })

  const types = [...new Set(assets.map(a => a.asset_type))].sort()
  const statuses = ['online', 'warning', 'offline', 'maintenance']

  const typeIcon = (type: string) => typeIcons[type] || <DevicePhoneMobileIcon className="w-4 h-4" />
  const statusIcon = (status: string) => statusIcons[status] || <ArrowPathIcon className="w-3.5 h-3.5 text-slate-500" />
  const statusLabel = (status: string) => statusLabels[status] || status

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading assets...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">Asset Inventory</h1>
          <span className="page-subtitle">{assets.length} total assets • {assets.filter(a => a.status === 'online').length} online</span>
        </div>
        <button className="btn-primary">
          <PlusIcon className="w-3 h-3 mr-2" />
          Add Asset
        </button>
      </div>

      {/* Search & Filters */}
      <div className="filters-bar">
        <div className="search-box">
          <MagnifyingGlassIcon className="w-3.5 h-3.5" />
          <input
            type="text"
            placeholder="Search hostname, IP, production line..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <select value={filterType} onChange={e => setFilterType(e.target.value)} className="filter-select">
            <option value="all">All Types</option>
            {types.map(t => <option key={t} value={t}>{typeLabels[t] || t}</option>)}
          </select>
          <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="filter-select">
            <option value="all">All Status</option>
            {statuses.map(s => <option key={s} value={s}>{statusLabel(s)}</option>)}
          </select>
          <button className="btn-secondary" onClick={() => { setSearch(''); setFilterType('all'); setFilterStatus('all') }}>
            <ArrowPathIcon className="w-3 h-3 mr-1" />
            Reset
          </button>
        </div>
      </div>

      {/* Assets Table */}
      <div className="infrastructure-section">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('hostname')}>
                  Hostname <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('asset_type')}>
                  Type <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('ip_address')}>
                  IP Address <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('production_line')}>
                  Production Line <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('status')}>
                  Status <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('criticality')}>
                  Criticality <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('location')}>
                  Location <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th onClick={() => handleSort('last_check')}>
                  Last Check <ArrowPathIcon className="w-3 h-3 inline ml-1" />
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssets.length > 0 ? (
                filteredAssets.map(asset => (
                  <tr key={asset.id}>
                    <td className="font-medium">{asset.hostname}</td>
                    <td>
                      <span className="type-badge">
                        {typeIcon(asset.asset_type)}
                        {typeLabels[asset.asset_type] || asset.asset_type}
                      </span>
                    </td>
                    <td className="font-mono text-sm">{asset.ip_address}</td>
                    <td>{asset.production_line || <span className="text-slate-500">—</span>}</td>
                    <td>
                      <span className="status-badge">
                        {statusIcon(asset.status)}
                        {statusLabel(asset.status)}
                      </span>
                    </td>
                    <td>
                      <span className={`criticality-badge ${criticalityColors[asset.criticality] || 'bg-gray-500'}`}>
                        {asset.criticality}
                      </span>
                    </td>
                    <td className="text-sm text-slate-400">{asset.location || '—'}</td>
                    <td className="text-sm text-slate-400">
                      {asset.last_check ? new Date(asset.last_check).toLocaleString() : 'Never'}
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button className="action-btn" title="View">
                          <MagnifyingGlassIcon className="w-3 h-3" />
                        </button>
                        <button className="action-btn" title="Edit">
                          <PencilIcon className="w-3 h-3" />
                        </button>
                        <button className="action-btn danger" title="Delete">
                          <TrashIcon className="w-3 h-3" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="empty-cell">No assets match your filters</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {filteredAssets.length !== assets.length && (
          <div className="table-footer">
            Showing {filteredAssets.length} of {assets.length} assets
          </div>
        )}
      </div>
    </div>
  )
}