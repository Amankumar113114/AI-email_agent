function Sidebar({ activeFilter, onFilterChange, stats }) {
  const filters = [
    { id: 'all', label: 'All Emails', icon: '📧' },
    { id: 'unread', label: 'Unread', icon: '🔔' },
    { id: 'urgent', label: 'Urgent', icon: '🔥' },
    { id: 'work', label: 'Work', icon: '💼' },
    { id: 'personal', label: 'Personal', icon: '👤' },
    { id: 'meetings', label: 'Meetings', icon: '📅' },
    { id: 'followup', label: 'Follow-up', icon: '🔄' },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1 className="app-title">📬 AI Email Agent</h1>
      </div>

      <button className="btn-compose" onClick={() => window.dispatchEvent(new CustomEvent('compose-email'))}>
        ✉️ Compose
      </button>

      <nav className="sidebar-nav">
        {filters.map(filter => (
          <button
            key={filter.id}
            className={`nav-item ${activeFilter === filter.id ? 'active' : ''}`}
            onClick={() => onFilterChange(filter.id)}
          >
            <span className="nav-icon">{filter.icon}</span>
            <span className="nav-label">{filter.label}</span>
            {stats[filter.id] > 0 && (
              <span className="nav-badge">{stats[filter.id]}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="stats-card">
          <h4>📊 Today's Stats</h4>
          <div className="stat-row">
            <span>Processed</span>
            <span>{stats.processed || 0}</span>
          </div>
          <div className="stat-row">
            <span>Replies Sent</span>
            <span>{stats.replies || 0}</span>
          </div>
          <div className="stat-row">
            <span>Time Saved</span>
            <span>{stats.timeSaved || '0m'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
