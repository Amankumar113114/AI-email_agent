import { useState, useEffect, useMemo } from 'react';
import Sidebar from './components/Sidebar';
import EmailList from './components/EmailList';
import EmailDetail from './components/EmailDetail';
import ComposeEmail from './components/ComposeEmail';
import SearchBar from './components/SearchBar';
import ConnectionStatus from './components/ConnectionStatus';
import { useEmailAgent } from './hooks/useEmailAgent';
import './App.css';

function App() {
  const {
    emails,
    threads,
    analysis,
    loading,
    backendAvailable,
    fetchEmails,
    processEmail,
    generateReply,
    sendReply,
    getThread,
    sendEmail,
    markAsRead,
    getStats,
  } = useEmailAgent();

  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [showCompose, setShowCompose] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState({
    all: 0, unread: 0, urgent: 0, work: 0, personal: 0,
    meetings: 0, followup: 0, processed: 0, replies: 0, timeSaved: '0m'
  });

  // Listen for compose event from Sidebar
  useEffect(() => {
    const handleCompose = () => setShowCompose(true);
    window.addEventListener('compose-email', handleCompose);
    return () => window.removeEventListener('compose-email', handleCompose);
  }, []);

  // Load stats
  useEffect(() => {
    const loadStats = async () => {
      const s = await getStats();
      setStats({
        all: s.total || 0,
        unread: s.unread || 0,
        urgent: s.urgent || 0,
        work: s.categories?.Work || 0,
        personal: s.categories?.Personal || 0,
        meetings: s.categories?.Meeting || 0,
        followup: s.categories?.['Follow-up'] || 0,
        processed: s.processed || 0,
        replies: s.replies || 0,
        timeSaved: s.timeSaved || '0m'
      });
    };
    loadStats();
  }, [emails, getStats]);

  // Process email when selected
  useEffect(() => {
    if (selectedEmail && !analysis[selectedEmail.id]) {
      processEmail(selectedEmail);
      markAsRead(selectedEmail.id);
    }
    if (selectedEmail?.thread_id) {
      getThread(selectedEmail.thread_id);
    }
  }, [selectedEmail, analysis, processEmail, getThread, markAsRead]);

  // Filter and search emails
  const filteredEmails = useMemo(() => {
    let filtered = emails;

    // Apply category filter
    switch (activeFilter) {
      case 'unread':
        filtered = filtered.filter(e => !e.is_read);
        break;
      case 'urgent':
        filtered = filtered.filter(e => e.priority === 'critical' || e.priority === 'high');
        break;
      case 'work':
        filtered = filtered.filter(e => e.category === 'Work');
        break;
      case 'personal':
        filtered = filtered.filter(e => e.category === 'Personal');
        break;
      case 'meetings':
        filtered = filtered.filter(e => e.category === 'Meeting');
        break;
      case 'followup':
        filtered = filtered.filter(e => e.category === 'Follow-up');
        break;
      default:
        break;
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(e => 
        e.subject?.toLowerCase().includes(query) ||
        e.body?.toLowerCase().includes(query) ||
        e.sender?.toLowerCase().includes(query) ||
        e.sender_name?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [emails, activeFilter, searchQuery]);

  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
  };

  const handleGenerateReply = async (email, tone = 'professional') => {
    return await generateReply(email, tone);
  };

  const handleSendReply = async (email, content) => {
    await sendReply(email, content);
  };

  const handleSendEmail = async (emailData) => {
    await sendEmail(emailData);
    setShowCompose(false);
  };

  const handleRefresh = () => {
    fetchEmails(activeFilter !== 'all' ? activeFilter : null);
  };

  return (
    <div className="app">
      <Sidebar 
        activeFilter={activeFilter} 
        onFilterChange={setActiveFilter}
        stats={stats}
      />
      
      <main className="main-content">
        <div className="top-bar">
          <SearchBar 
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search emails..."
          />
          <div className="top-bar-actions">
            <button className="btn-icon" onClick={handleRefresh} title="Refresh">
              🔄
            </button>
            <ConnectionStatus connected={backendAvailable} />
          </div>
        </div>

        <div className="content-area">
          <EmailList 
            emails={filteredEmails}
            selectedEmail={selectedEmail}
            onSelectEmail={handleSelectEmail}
          />
          
          <EmailDetail 
            email={selectedEmail}
            thread={selectedEmail?.thread_id ? threads[selectedEmail.thread_id] : null}
            analysis={selectedEmail ? analysis[selectedEmail.id]?.classification : null}
            context={selectedEmail ? analysis[selectedEmail.id]?.context : null}
            onGenerateReply={handleGenerateReply}
            onSendReply={handleSendReply}
          />
        </div>
      </main>

      {showCompose && (
        <ComposeEmail 
          onSend={handleSendEmail}
          onCancel={() => setShowCompose(false)}
        />
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <span>AI is processing...</span>
        </div>
      )}
    </div>
  );
}

export default App;
