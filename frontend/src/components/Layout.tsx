import { Outlet, Link, useLocation } from 'react-router-dom'
import {
  Squares2X2Icon,
  ServerStackIcon,
  ExclamationTriangleIcon,
  SignalIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'

export default function Layout() {
  const location = useLocation()

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
          <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
            <Squares2X2Icon className="w-5 h-5" />
            <span>Dashboard</span>
          </Link>
          <a href="#" className="nav-item" onClick={(e) => e.preventDefault()}>
            <ServerStackIcon className="w-5 h-5" />
            <span>Assets</span>
          </a>
          <a href="#" className="nav-item" onClick={(e) => e.preventDefault()}>
            <ExclamationTriangleIcon className="w-5 h-5" />
            <span>Incidents</span>
          </a>
          <Link to="/monitoring" className={`nav-item ${location.pathname === '/monitoring' ? 'active' : ''}`}>
            <SignalIcon className="w-5 h-5" />
            <span>Monitoring</span>
          </Link>
          <a href="#" className="nav-item" onClick={(e) => e.preventDefault()}>
            <Cog6ToothIcon className="w-5 h-5" />
            <span>Settings</span>
          </a>
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
              {location.pathname === '/monitoring' ? 'Monitoring' : 'Operations Dashboard'}
            </h1>
            <span className="page-subtitle">
              {location.pathname === '/monitoring'
                ? 'Real-time infrastructure monitoring results'
                : 'IT Production Monitoring & Infrastructure Intelligence'}
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
