import { Outlet, Link, useLocation, NavLink } from 'react-router-dom'
import {
  Squares2X2Icon,
  ServerStackIcon,
  ExclamationTriangleIcon,
  SignalIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

export default function Layout() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Squares2X2Icon },
    { path: '/assets', label: 'Assets', icon: ServerStackIcon },
    { path: '/incidents', label: 'Incidents', icon: ExclamationTriangleIcon },
    { path: '/monitoring', label: 'Monitoring', icon: SignalIcon },
    { path: '/settings', label: 'Settings', icon: Cog6ToothIcon },
  ]

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">EZ</div>
          <div className="brand-text">
            <span className="brand-title">EZ-ZAHRAOUI</span>
            <span className="brand-subtitle">IT GUARDIAN</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-indicator">
            <span className="status-dot online"></span>
            <span>System Online</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="top-bar">
          <div className="top-bar-left">
            <h1 className="page-title">
              {location.pathname === '/assets' ? 'Asset Inventory' :
               location.pathname === '/incidents' ? 'Incident Management' :
               location.pathname === '/monitoring' ? 'Monitoring' :
               location.pathname === '/settings' ? 'Settings' :
               'Operations Dashboard'}
            </h1>
            <span className="page-subtitle">
              {location.pathname === '/assets' ? 'Manage and monitor all infrastructure assets' :
               location.pathname === '/incidents' ? 'Track and resolve IT incidents' :
               location.pathname === '/monitoring' ? 'Real-time infrastructure monitoring results' :
               location.pathname === '/settings' ? 'Configure platform settings' :
               'IT Production Monitoring & Infrastructure Intelligence'}
            </span>
          </div>
          <div className="top-bar-right">
            <div className="top-bar-badge">
              <span className="badge-label">Environment</span>
              <span className="badge-value production">PRODUCTION</span>
            </div>
            <div className="top-bar-time" id="current-time">
              {new Date().toLocaleString()}
            </div>
          </div>
        </header>

        <div className="dashboard-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}