import { useState, useEffect } from 'react'
import client from '../api/client'
import {
  Cog6ToothIcon,
  ServerStackIcon,
  ShieldCheckIcon,
  BellIcon,
  UserGroupIcon,
  KeyIcon,
  ArrowPathIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

interface MonitoringSettings {
  interval_seconds: number
  timeout_seconds: number
  ping_count: number
}

interface User {
  id: number
  username: string
  role: string
  email: string
  active: boolean
}

export default function Settings() {
  const [activeTab, setActiveTab] = useState<string>('general')
  const [monitoringSettings, setMonitoringSettings] = useState<MonitoringSettings>({
    interval_seconds: 60,
    timeout_seconds: 5,
    ping_count: 4,
  })
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      // In a real app, these would come from an API
      // For now using defaults
    } catch (err) {
      console.error('Failed to fetch settings:', err)
    }
  }

  const handleSave = async (key: string, value: any) => {
    setLoading(true)
    setSaved(false)
    // Simulate API call
    await new Promise(r => setTimeout(r, 500))
    setLoading(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-left">
          <h1 className="page-title">Settings</h1>
          <span className="page-subtitle">Configure monitoring, users, notifications, and system preferences</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="settings-tabs">
        {[
          { id: 'general', label: 'General', icon: Cog6ToothIcon },
          { id: 'monitoring', label: 'Monitoring', icon: ServerStackIcon },
          { id: 'notifications', label: 'Notifications', icon: BellIcon },
          { id: 'users', label: 'Users & Roles', icon: UserGroupIcon },
          { id: 'security', label: 'Security', icon: ShieldCheckIcon },
          { id: 'about', label: 'About', icon: DocumentTextIcon },
        ].map(tab => (
          <button
            key={tab.id}
            className={`settings-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon className="w-5 h-5 mr-2" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="settings-content">
        {activeTab === 'general' && (
          <SettingsSection title="General Settings" description="Basic platform configuration">
            <SettingRow
              label="Platform Name"
              description="Displayed in the header and browser title"
              input={
                <input type="text" defaultValue="EZ-ZAHRAOUI IT Guardian" className="settings-input" />
              }
            />
            <SettingRow
              label="Environment"
              description="Current deployment environment"
              input={
                <select className="settings-select" defaultValue="production">
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </select>
              }
            />
            <SettingRow
              label="Timezone"
              description="Timezone for logs and timestamps"
              input={
                <select className="settings-select" defaultValue="UTC">
                  <option value="UTC">UTC</option>
                  <option value="Europe/Paris">Europe/Paris</option>
                  <option value="America/New_York">America/New_York</option>
                </select>
              }
            />
            <SettingRow
              label="Language"
              description="Default interface language"
              input={
                <select className="settings-select" defaultValue="en">
                  <option value="en">English</option>
                  <option value="fr">French</option>
                </select>
              }
            />
            <SettingRow
              label="Auto Refresh Interval"
              description="Dashboard refresh interval in seconds"
              input={
                <select className="settings-select" defaultValue="15">
                  <option value="15">15 seconds</option>
                  <option value="30">30 seconds</option>
                  <option value="60">1 minute</option>
                  <option value="300">5 minutes</option>
                </select>
              }
            />
          </SettingsSection>
        )}

        {activeTab === 'monitoring' && (
          <SettingsSection title="Monitoring Configuration" description="Configure how the monitoring engine checks your infrastructure">
            <SettingRow
              label="Check Interval"
              description="Seconds between monitoring cycles"
              input={
                <input
                  type="number"
                  defaultValue={60}
                  min={10}
                  max={3600}
                  className="settings-input w-32"
                  onChange={e => handleSave('interval_seconds', parseInt(e.target.value))}
                />
              }
            />
            <SettingRow
              label="Check Timeout"
              description="Seconds before a check is considered timeout"
              input={
                <input
                  type="number"
                  defaultValue={5}
                  min={1}
                  max={60}
                  className="settings-input w-32"
                  onChange={e => handleSave('timeout_seconds', parseInt(e.target.value))}
                />
              }
            />
            <SettingRow
              label="Ping Count"
              description="Number of ping packets per ICMP check"
              input={
                <input
                  type="number"
                  defaultValue={4}
                  min={1}
                  max={10}
                  className="settings-input w-32"
                  onChange={e => handleSave('ping_count', parseInt(e.target.value))}
                />
              }
            />
            <SettingRow
              label="Concurrent ICMP Checks"
              description="Maximum parallel ping checks"
              input={
                <input type="number" defaultValue={20} min={5} max={100} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Concurrent TCP Checks"
              description="Maximum parallel port checks"
              input={
                <input type="number" defaultValue={10} min={5} max={50} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Concurrent HTTP Checks"
              description="Maximum parallel HTTP health checks"
              input={
                <input type="number" defaultValue={10} min={5} max={50} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="TCP Ports for Servers"
              description="Comma-separated list of ports to check on servers"
              input={
                <input type="text" defaultValue="22,80,443,3389,5432,8080" className="settings-input w-96" />
              }
            />
            <SettingRow
              label="HTTP Health Endpoint"
              description="Default path for HTTP health checks"
              input={
                <input type="text" defaultValue="/health" className="settings-input w-48" />
              }
            />
            <div className="settings-actions">
              <button className="btn-secondary" onClick={() => handleSave('monitoring', monitoringSettings)} disabled={loading}>
                {loading ? (
                  <>
                    <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircleIcon className="w-4 h-4 mr-2" />
                    Save Monitoring Settings
                  </>
                )}
              </button>
              {saved && <span className="save-success"><CheckCircleIcon className="w-4 h-4 mr-1" /> Saved!</span>}
            </div>
          </SettingsSection>
        )}

        {activeTab === 'notifications' && (
          <SettingsSection title="Notifications" description="Configure alerting and notification channels">
            <SettingRow
              label="Email Alerts"
              description="Enable email notifications for incidents"
              input={
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              }
            />
            <SettingRow
              label="SMTP Server"
              description="SMTP server for sending emails"
              input={
                <input type="text" placeholder="smtp.example.com" className="settings-input w-64" />
              }
            />
            <SettingRow
              label="SMTP Port"
              description="SMTP server port"
              input={
                <input type="number" defaultValue={587} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="From Email"
              description="Sender email address"
              input={
                <input type="email" placeholder="alerts@example.com" className="settings-input w-64" />
              }
            />
            <SettingRow
              label="Alert Recipients"
              description="Comma-separated email addresses for critical alerts"
              input={
                <input type="text" placeholder="admin@example.com, oncall@example.com" className="settings-input w-96" />
              }
            />
            <SettingRow
              label="Teams/Webhook URL"
              description="Microsoft Teams or Slack webhook for notifications"
              input={
                <input type="url" placeholder="https://outlook.office.com/webhook/..." className="settings-input w-96" />
              }
            />
            <SettingRow
              label="Notify on Critical"
              description="Send notification when critical incident created"
              input={
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              }
            />
            <SettingRow
              label="Notify on High"
              description="Send notification when high severity incident created"
              input={
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              }
            />
            <SettingRow
              label="Notify on Resolution"
              description="Send notification when incident is resolved"
              input={
                <label className="toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="toggle-slider"></span>
                </label>
              }
            />
          </SettingsSection>
        )}

        {activeTab === 'users' && (
          <SettingsSection title="Users & Roles" description="Manage platform users and their permissions">
            <div className="users-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { id: 1, username: 'admin', email: 'admin@ez-zahraoui.com', role: 'Administrator', active: true, lastLogin: '2026-10-10 08:30' },
                    { id: 2, username: 'ahmed.z', email: 'ahmed.z@ez-zahraoui.com', role: 'Technician', active: true, lastLogin: '2026-10-10 07:15' },
                    { id: 3, username: 'sarah.m', email: 'sarah.m@ez-zahraoui.com', role: 'Technician', active: true, lastLogin: '2026-10-10 06:45' },
                    { id: 4, username: 'john.d', email: 'john.d@ez-zahraoui.com', role: 'Viewer', active: false, lastLogin: '2026-10-05 14:20' },
                  ].map(user => (
                    <tr key={user.id}>
                      <td className="font-medium">{user.username}</td>
                      <td>{user.email}</td>
                      <td><span className="role-badge">{user.role}</span></td>
                      <td>
                        <span className={`status-dot ${user.active ? 'online' : 'offline'}`}></span>
                        {user.active ? 'Active' : 'Inactive'}
                      </td>
                      <td className="text-sm text-slate-400">{user.lastLogin}</td>
                      <td>
                        <div className="action-buttons">
                          <button className="action-btn" title="Edit"><PencilIcon className="w-4 h-4" /></button>
                          <button className="action-btn danger" title="Delete"><TrashIcon className="w-4 h-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="settings-actions">
              <button className="btn-primary">
                <PlusIcon className="w-4 h-4 mr-2" />
                Add User
              </button>
            </div>
          </SettingsSection>
        )}

        {activeTab === 'security' && (
          <SettingsSection title="Security" description="Authentication and access control settings">
            <SettingRow
              label="JWT Secret Key"
              description="Secret key for JWT token signing (keep secure!)"
              input={
                <input type="password" defaultValue="••••••••••••••••••••••••••••••••••••" className="settings-input w-96" />
              }
            />
            <SettingRow
              label="JWT Expiration"
              description="Token expiration time in minutes"
              input={
                <input type="number" defaultValue={480} min={15} max={10080} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Password Min Length"
              description="Minimum password length"
              input={
                <input type="number" defaultValue={12} min={8} max={64} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Require MFA"
              description="Enforce multi-factor authentication for all users"
              input={
                <label className="toggle">
                  <input type="checkbox" />
                  <span className="toggle-slider"></span>
                </label>
              }
            />
            <SettingRow
              label="Session Timeout"
              description="Minutes of inactivity before auto-logout"
              input={
                <input type="number" defaultValue={60} min={5} max={480} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Max Login Attempts"
              description="Failed attempts before temporary lockout"
              input={
                <input type="number" defaultValue={5} min={3} max={20} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="Lockout Duration"
              description="Minutes to lock account after max attempts"
              input={
                <input type="number" defaultValue={15} min={5} max={1440} className="settings-input w-32" />
              }
            />
            <SettingRow
              label="CORS Allowed Origins"
              description="Comma-separated allowed origins"
              input={
                <input type="text" defaultValue="http://localhost:3000,http://localhost:5173" className="settings-input w-96" />
              }
            />
            <SettingRow
              label="API Rate Limit"
              description="Requests per minute per IP"
              input={
                <input type="number" defaultValue={1000} min={100} max={10000} className="settings-input w-32" />
              }
            />
          </SettingsSection>
        )}

        {activeTab === 'about' && (
          <SettingsSection title="About" description="Platform information and version details">
            <div className="about-grid">
              <div className="about-card">
                <div className="about-icon">
                  <Cog6ToothIcon className="w-8 h-8" />
                </div>
                <h3>EZ-ZAHRAOUI IT Guardian</h3>
                <p className="text-slate-400">IT Production Monitoring & Incident Management Platform</p>
              </div>
              <div className="about-card">
                <div className="about-icon">
                  <DocumentTextIcon className="w-8 h-8" />
                </div>
                <h3>Version</h3>
                <p className="text-slate-400">0.1.0 (Development)</p>
              </div>
              <div className="about-card">
                <div className="about-icon">
                  <ServerStackIcon className="w-8 h-8" />
                </div>
                <h3>Backend</h3>
                <p className="text-slate-400">FastAPI 0.115 • Python 3.12 • PostgreSQL 16</p>
              </div>
              <div className="about-card">
                <div className="about-icon">
                  <DocumentTextIcon className="w-8 h-8" />
                </div>
                <h3>Frontend</h3>
                <p className="text-slate-400">React 18 • TypeScript • Vite 6</p>
              </div>
              <div className="about-card">
                <div className="about-icon">
                  <ServerStackIcon className="w-8 h-8" />
                </div>
                <h3>Monitoring</h3>
                <p className="text-slate-400">Python asyncio • ICMP/TCP/HTTP</p>
              </div>
              <div className="about-card">
                <div className="about-icon">
                  <DocumentTextIcon className="w-8 h-8" />
                </div>
                <h3>License</h3>
                <p className="text-slate-400">MIT License</p>
              </div>
            </div>

            <div className="settings-actions" style={{ marginTop: '24px' }}>
              <a href="https://github.com/ez-zahraoui/ez-zahraoui-it-guardian" target="_blank" className="btn-secondary">
                <DocumentTextIcon className="w-4 h-4 mr-2" />
                View Source on GitHub
              </a>
              <a href="https://github.com/ez-zahraoui/ez-zahraoui-it-guardian/blob/main/README.md" target="_blank" className="btn-secondary">
                <DocumentTextIcon className="w-4 h-4 mr-2" />
                Documentation
              </a>
            </div>
          </SettingsSection>
        )}
      </div>
    </div>
  )
}

function SettingsSection({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <div className="settings-section">
      <div className="settings-section-header">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      <div className="settings-section-body">
        {children}
      </div>
    </div>
  )
}

function SettingRow({ label, description, input }: { label: string; description: string; input: React.ReactNode }) {
  return (
    <div className="setting-row">
      <div className="setting-label">
        <span>{label}</span>
        <span className="setting-description">{description}</span>
      </div>
      <div className="setting-input-wrapper">{input}</div>
    </div>
  )
}