import { useState } from 'react';

function EmailDetail({ email, thread, analysis, context, onGenerateReply, onSendReply }) {
  const [showReply, setShowReply] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [activeTab, setActiveTab] = useState('content');

  if (!email) {
    return (
      <div className="email-detail empty">
        <div className="empty-state">
          <span className="empty-icon">📧</span>
          <p>Select an email to view details</p>
        </div>
      </div>
    );
  }

  const handleGenerateReply = async () => {
    const reply = await onGenerateReply(email);
    setReplyContent(reply.content);
    setShowReply(true);
  };

  const handleSendReply = () => {
    onSendReply(email, replyContent);
    setShowReply(false);
    setReplyContent('');
  };

  const getPriorityBadge = (priority) => {
    const classes = {
      critical: 'priority-critical',
      high: 'priority-high',
      medium: 'priority-medium',
      low: 'priority-low'
    };
    return classes[priority] || 'priority-medium';
  };

  return (
    <div className="email-detail">
      <div className="email-detail-header">
        <div className="email-actions">
          <button className="btn-reply" onClick={handleGenerateReply}>
            🤖 AI Reply
          </button>
          <button className="btn-archive">📥 Archive</button>
          <button className="btn-delete">🗑️ Delete</button>
        </div>
      </div>

      <div className="email-content-wrapper">
        <div className="email-header-info">
          <h1 className="email-subject">{email.subject}</h1>
          <div className="email-meta-row">
            <div className="sender-info">
              <div className="sender-avatar">
                {(email.sender_name || email.sender)[0].toUpperCase()}
              </div>
              <div className="sender-details">
                <span className="sender-name">{email.sender_name || email.sender}</span>
                <span className="sender-email">{email.sender}</span>
              </div>
            </div>
            <span className="email-date">
              {email.timestamp ? new Date(email.timestamp).toLocaleString() : 'Unknown'}
            </span>
          </div>
          {analysis && (
            <div className="analysis-badges">
              <span className={`badge priority ${getPriorityBadge(analysis.priority)}`}>
                {analysis.priority?.toUpperCase()}
              </span>
              <span className="badge category">
                {analysis.primary_category}
              </span>
              {analysis.secondary_categories?.map(cat => (
                <span key={cat} className="badge category-secondary">{cat}</span>
              ))}
            </div>
          )}
        </div>

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'content' ? 'active' : ''}`}
            onClick={() => setActiveTab('content')}
          >
            📧 Email
          </button>
          {thread && (
            <button 
              className={`tab ${activeTab === 'thread' ? 'active' : ''}`}
              onClick={() => setActiveTab('thread')}
            >
              🧵 Thread ({thread.emails?.length || 0})
            </button>
          )}
          {analysis && (
            <button 
              className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('analysis')}
            >
              📊 Analysis
            </button>
          )}
        </div>

        <div className="tab-content">
          {activeTab === 'content' && (
            <div className="email-body">
              {email.body.split('\n').map((paragraph, i) => (
                <p key={i}>{paragraph}</p>
              ))}
            </div>
          )}

          {activeTab === 'thread' && thread && (
            <div className="thread-view">
              {thread.emails?.map((threadEmail, index) => (
                <div key={threadEmail.id} className="thread-email">
                  <div className="thread-email-header">
                    <span className="thread-email-sender">
                      {threadEmail.sender_name || threadEmail.sender}
                    </span>
                    <span className="thread-email-date">
                      {threadEmail.timestamp ? new Date(threadEmail.timestamp).toLocaleString() : 'Unknown'}
                    </span>
                  </div>
                  <div className="thread-email-body">
                    {threadEmail.body.substring(0, 200)}...
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'analysis' && (analysis || context) && (
            <div className="analysis-view">
              {context?.summary && (
                <div className="analysis-section">
                  <h3>📝 Thread Summary</h3>
                  <p>{context.summary}</p>
                </div>
              )}
              
              {context?.key_points && context.key_points.length > 0 && (
                <div className="analysis-section">
                  <h3>🔑 Key Points</h3>
                  <ul>
                    {context.key_points.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
              )}

              {context?.decisions && context.decisions.length > 0 && (
                <div className="analysis-section">
                  <h3>✅ Decisions Made</h3>
                  <ul>
                    {context.decisions.map((decision, i) => (
                      <li key={i}>{decision}</li>
                    ))}
                  </ul>
                </div>
              )}

              {context?.action_items && context.action_items.length > 0 && (
                <div className="analysis-section">
                  <h3>⚡ Action Items</h3>
                  <ul className="action-items">
                    {context.action_items.map((item, i) => (
                      <li key={i}>
                        <span className="action-text">{item.action}</span>
                        {item.owner && <span className="action-owner">@{item.owner}</span>}
                        {item.deadline && <span className="action-deadline">📅 {item.deadline}</span>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {context?.sentiment && (
                <div className="analysis-section">
                  <h3>😊 Sentiment</h3>
                  <span className={`sentiment-badge sentiment-${context.sentiment}`}>
                    {context.sentiment}
                  </span>
                  {context.urgency_score !== undefined && (
                    <div className="urgency-meter">
                      <span>Urgency Score: {Math.round(context.urgency_score * 100)}%</span>
                      <div className="urgency-bar">
                        <div 
                          className="urgency-fill" 
                          style={{ width: `${context.urgency_score * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}

              {analysis?.reasoning && (
                <div className="analysis-section">
                  <h3>🎯 Classification Reasoning</h3>
                  <p className="reasoning">{analysis.reasoning}</p>
                  {analysis.confidence !== undefined && (
                    <div className="confidence-bar">
                      <div 
                        className="confidence-fill" 
                        style={{ width: `${analysis.confidence * 100}%` }}
                      />
                      <span>Confidence: {Math.round(analysis.confidence * 100)}%</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {showReply && (
        <div className="reply-composer">
          <div className="reply-header">
            <h3>🤖 AI-Generated Reply</h3>
            <button className="btn-close" onClick={() => setShowReply(false)}>×</button>
          </div>
          <textarea
            className="reply-textarea"
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder="Generated reply will appear here..."
            rows={8}
          />
          <div className="reply-actions">
            <button className="btn-secondary" onClick={() => setShowReply(false)}>
              Cancel
            </button>
            <button className="btn-primary" onClick={handleSendReply}>
              📤 Send Reply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default EmailDetail;
