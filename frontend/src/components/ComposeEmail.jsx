import { useState } from 'react';

function ComposeEmail({ onSend, onCancel }) {
  const [email, setEmail] = useState({
    to: '',
    subject: '',
    body: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    await onSend(email);
    setIsLoading(false);
  };

  const handleChange = (field, value) => {
    setEmail(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="compose-modal">
      <div className="compose-content">
        <div className="compose-header">
          <h2>✉️ Compose New Email</h2>
          <button className="btn-close" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="compose-form">
          <div className="form-group">
            <label htmlFor="to">To:</label>
            <input
              type="email"
              id="to"
              value={email.to}
              onChange={(e) => handleChange('to', e.target.value)}
              placeholder="recipient@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="subject">Subject:</label>
            <input
              type="text"
              id="subject"
              value={email.subject}
              onChange={(e) => handleChange('subject', e.target.value)}
              placeholder="Email subject"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="body">Message:</label>
            <textarea
              id="body"
              value={email.body}
              onChange={(e) => handleChange('body', e.target.value)}
              placeholder="Write your message here..."
              rows={12}
              required
            />
          </div>

          <div className="compose-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? 'Sending...' : '📤 Send Email'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ComposeEmail;
