export interface Asset {
  id: number
  hostname: string
  ip_address: string
  mac_address: string | null
  asset_type: string
  operating_system: string | null
  location: string | null
  production_line: string | null
  status: 'online' | 'offline' | 'warning' | 'maintenance'
  owner_team: string | null
  criticality: 'low' | 'medium' | 'high' | 'critical'
  description: string | null
  is_active: boolean
  last_check: string | null
  created_at: string
  updated_at: string
}

export interface Incident {
  id: number
  incident_id: string
  asset_id: number
  category: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  priority: 'P1' | 'P2' | 'P3' | 'P4'
  status: 'open' | 'investigating' | 'in_progress' | 'resolved' | 'closed'
  title: string
  description: string | null
  detected_at: string
  resolved_at: string | null
  assigned_technician: string | null
  root_cause: string | null
  resolution_notes: string | null
  risk_score: number | null
  production_impact: string | null
}

export interface MonitoringResult {
  id: number
  asset_id: number
  check_type: 'icmp' | 'tcp' | 'http'
  result: 'success' | 'failure' | 'timeout' | 'error'
  response_time_ms: number | null
  packet_loss_percent: number | null
  status_code: number | null
  message: string | null
  checked_at: string
}

export interface DashboardStats {
  total_assets: number
  online_assets: number
  offline_assets: number
  warning_assets: number
  maintenance_assets: number
  active_incidents: number
  critical_incidents: number
  high_incidents: number
  medium_incidents: number
  low_incidents: number
  overall_health: number
  production_health: number
  network_health: number
  server_health: number
  risk_score: number
  risk_band: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
}
