function ConnectionStatus({ connected }) {
  return (
    <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
      <span className="status-dot"></span>
      <span className="status-text">
        {connected ? 'AI Connected' : 'Demo Mode'}
      </span>
    </div>
  );
}

export default ConnectionStatus;
