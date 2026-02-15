import { useState } from 'react';

function EmailList({ emails, selectedEmail, onSelectEmail }) {
  const getPriorityColor = (priority) => {
    const colors = {
      critical: '#ff4444',
      high: '#ff8800',
      medium: '#ffaa00',
      low: '#00aa00'
    };
    return colors[priority] || '#888';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      Work: '💼',
      Personal: '👤',
      Finance: '💰',
      Promotions: '📢',
      Support: '🎧',
      Urgent: '🔥',
      Meeting: '📅',
      'Follow-up': '🔄',
      Other: '📧'
    };
    return icons[category] || '📧';
  };

  return (
    <div className="email-list">
      <div className="email-list-header">
        <h2>Inbox</h2>
        <span className="email-count">{emails.length} emails</span>
      </div>
      
      <div className="email-items">
        {emails.map((email) => (
          <div
            key={email.id}
            className={`email-item ${selectedEmail?.id === email.id ? 'selected' : ''} ${!email.is_read ? 'unread' : ''}`}
            onClick={() => onSelectEmail(email)}
          >
            <div className="email-item-header">
              <span className="category-icon">{getCategoryIcon(email.category)}</span>
              <span className="sender">{email.sender_name || email.sender}</span>
              <span 
                className="priority-dot"
                style={{ backgroundColor: getPriorityColor(email.priority) }}
                title={`Priority: ${email.priority}`}
              />
            </div>
            
            <div className="email-subject">{email.subject}</div>
            
            <div className="email-preview">
              {email.body.substring(0, 80)}...
            </div>
            
            <div className="email-meta">
              <span className="timestamp">
                {email.timestamp ? new Date(email.timestamp).toLocaleDateString() : 'Unknown'}
              </span>
              {email.thread_id && (
                <span className="thread-indicator">🧵 Thread</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EmailList;
