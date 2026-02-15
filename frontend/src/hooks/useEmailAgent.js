import { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export function useEmailAgent() {
  const [emails, setEmails] = useState([]);
  const [threads, setThreads] = useState({});
  const [analysis, setAnalysis] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendAvailable, setBackendAvailable] = useState(true);

  // Check backend availability
  const checkBackend = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/`, { method: 'GET' });
      setBackendAvailable(response.ok);
      return response.ok;
    } catch {
      setBackendAvailable(false);
      return false;
    }
  }, []);

  // Fetch all emails
  const fetchEmails = useCallback(async (filter = null) => {
    try {
      setLoading(true);
      const url = filter ? `${API_BASE_URL}/emails?filter_type=${filter}` : `${API_BASE_URL}/emails`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch emails');
      const data = await response.json();
      setEmails(data.emails || []);
      setBackendAvailable(true);
    } catch (err) {
      setError(err.message);
      setBackendAvailable(false);
      // Fallback to demo data if API is not available
      setEmails(getDemoEmails());
    } finally {
      setLoading(false);
    }
  }, []);

  // Process email with AI
  const processEmail = useCallback(async (email) => {
    // Return cached analysis if available
    if (analysis[email.id]) {
      return analysis[email.id];
    }

    try {
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      if (!response.ok) throw new Error('Failed to process email');
      const result = await response.json();
      setAnalysis(prev => ({ ...prev, [email.id]: result }));
      return result;
    } catch (err) {
      // Fallback: simulate processing
      const mockResult = simulateProcessing(email);
      setAnalysis(prev => ({ ...prev, [email.id]: mockResult }));
      return mockResult;
    }
  }, [analysis]);

  // Generate AI reply
  const generateReply = useCallback(async (email, tone = 'professional') => {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_id: email.id, tone }),
      });
      if (!response.ok) throw new Error('Failed to generate reply');
      return await response.json();
    } catch (err) {
      // Fallback: generate mock reply
      return generateMockReply(email);
    }
  }, []);

  // Send reply
  const sendReply = useCallback(async (email, content) => {
    try {
      const response = await fetch(`${API_BASE_URL}/send-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_id: email.id, content }),
      });
      if (!response.ok) throw new Error('Failed to send reply');
      // Mark email as read in local state
      setEmails(prev => prev.map(e => 
        e.id === email.id ? { ...e, is_read: true } : e
      ));
      return await response.json();
    } catch (err) {
      console.log('Reply sent (mock):', content);
      setEmails(prev => prev.map(e => 
        e.id === email.id ? { ...e, is_read: true } : e
      ));
      return { success: true };
    }
  }, []);

  // Get thread details
  const getThread = useCallback(async (threadId) => {
    if (threads[threadId]) {
      return threads[threadId];
    }

    try {
      const response = await fetch(`${API_BASE_URL}/threads/${threadId}`);
      if (!response.ok) throw new Error('Failed to fetch thread');
      const result = await response.json();
      setThreads(prev => ({ ...prev, [threadId]: result }));
      return result;
    } catch (err) {
      const mockThread = generateMockThread(threadId, emails);
      setThreads(prev => ({ ...prev, [threadId]: mockThread }));
      return mockThread;
    }
  }, [emails, threads]);

  // Send new email
  const sendEmail = useCallback(async (emailData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData),
      });
      if (!response.ok) throw new Error('Failed to send email');
      await fetchEmails(); // Refresh list
      return await response.json();
    } catch (err) {
      console.log('Email sent (mock):', emailData);
      return { success: true };
    }
  }, [fetchEmails]);

  // Mark email as read
  const markAsRead = useCallback(async (emailId) => {
    try {
      await fetch(`${API_BASE_URL}/emails/${emailId}/mark-read`, {
        method: 'POST',
      });
      setEmails(prev => prev.map(e => 
        e.id === emailId ? { ...e, is_read: true } : e
      ));
    } catch (err) {
      setEmails(prev => prev.map(e => 
        e.id === emailId ? { ...e, is_read: true } : e
      ));
    }
  }, []);

  // Get stats
  const getStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) throw new Error('Failed to fetch stats');
      return await response.json();
    } catch (err) {
      return {
        total: emails.length,
        unread: emails.filter(e => !e.is_read).length,
        urgent: emails.filter(e => e.priority === 'critical' || e.priority === 'high').length,
        processed: Object.keys(analysis).length
      };
    }
  }, [emails, analysis]);

  // Load emails on mount
  useEffect(() => {
    checkBackend();
    fetchEmails();
  }, [checkBackend, fetchEmails]);

  return {
    emails,
    threads,
    analysis,
    loading,
    error,
    backendAvailable,
    fetchEmails,
    processEmail,
    generateReply,
    sendReply,
    getThread,
    sendEmail,
    markAsRead,
    getStats,
  };
}

// Demo data for fallback
function getDemoEmails() {
  return [
    {
      id: 'email-001',
      subject: 'Project Alpha Launch - Timeline Discussion',
      sender: 'sarah.chen@company.com',
      sender_name: 'Sarah Chen',
      recipients: ['you@company.com'],
      body: `Hi team,

I wanted to discuss the timeline for Project Alpha. We're currently scheduled to launch on March 15th, but I'm concerned about the testing phase.

Can we schedule a meeting this week to review the current status? I think we need at least 2 more weeks for proper QA.

Please let me know your availability.

Best,
Sarah`,
      thread_id: 'thread-001',
      timestamp: new Date('2026-02-10T09:00:00').toISOString(),
      is_read: false,
      category: 'Meeting',
      priority: 'high'
    },
    {
      id: 'email-002',
      subject: 'Invoice #1234 - Payment Due',
      sender: 'billing@vendor.com',
      sender_name: 'Vendor Billing',
      recipients: ['you@company.com'],
      body: `Dear Customer,

This is a reminder that Invoice #1234 for $5,000 is due on February 20th, 2026.

Please process the payment at your earliest convenience to avoid late fees.

Thank you for your business.

Regards,
Billing Department`,
      thread_id: 'thread-002',
      timestamp: new Date('2026-02-14T10:30:00').toISOString(),
      is_read: true,
      category: 'Finance',
      priority: 'medium'
    },
    {
      id: 'email-003',
      subject: 'URGENT: Critical bug in production',
      sender: 'dev-team@company.com',
      sender_name: 'Development Team',
      recipients: ['you@company.com'],
      body: `URGENT - Action Required

We've discovered a critical bug in the authentication module that is affecting user logins. This needs immediate attention.

Error: Null pointer exception in AuthHandler.java
Impact: All users unable to login

Please prioritize this fix ASAP.

Thanks`,
      thread_id: 'thread-003',
      timestamp: new Date('2026-02-15T08:00:00').toISOString(),
      is_read: false,
      category: 'Urgent',
      priority: 'critical'
    },
    {
      id: 'email-004',
      subject: 'Weekend plans?',
      sender: 'john.doe@personal.com',
      sender_name: 'John Doe',
      recipients: ['you@company.com'],
      body: `Hey!

Are you free this weekend? A few of us are planning to go hiking on Saturday morning. Let me know if you want to join!

Cheers,
John`,
      thread_id: 'thread-004',
      timestamp: new Date('2026-02-14T18:00:00').toISOString(),
      is_read: true,
      category: 'Personal',
      priority: 'low'
    }
  ];
}

function simulateProcessing(email) {
  return {
    success: true,
    classification: {
      primary_category: email.category || 'Other',
      secondary_categories: [],
      priority: email.priority || 'medium',
      priority_score: email.priority === 'critical' ? 0.9 : email.priority === 'high' ? 0.7 : 0.5,
      confidence: 0.85,
      reasoning: `Classified as ${email.category} based on content analysis.`
    },
    context: {
      summary: `Email from ${email.sender_name || email.sender} regarding ${email.subject}.`,
      key_points: ['Key point 1', 'Key point 2'],
      decisions: [],
      action_items: email.priority === 'critical' ? [{ action: 'Address urgent issue', owner: 'you', deadline: 'ASAP' }] : [],
      sentiment: 'neutral',
      urgency_score: email.priority === 'critical' ? 0.9 : 0.5
    },
    reply: {
      content: `Thank you for your email regarding "${email.subject}". I will review and respond shortly.`,
      tone: 'professional',
      estimated_response_time: '5-10 minutes',
      required_actions: [],
      suggested_attachments: []
    }
  };
}

function generateMockReply(email) {
  const replies = {
    Meeting: `Hi ${email.sender_name || 'there'},

Thank you for reaching out about the meeting. I'd be happy to schedule something this week.

I'm available Wednesday at 10am or Thursday afternoon. Would either of those work for you?

Looking forward to discussing this further.

Best regards`,
    Finance: `Dear Billing Department,

Thank you for the reminder regarding Invoice #1234.

I will process the payment before the due date of February 20th.

Please let me know if you need any additional information.

Best regards`,
    Urgent: `Hi Team,

Thank you for flagging this critical issue. I'm looking into it immediately and will provide an update within the hour.

Please keep me posted on any new developments.

Best`,
    Personal: `Hey!

Thanks for the invite! I'd love to join the hiking trip on Saturday.

What time are you planning to meet?

Cheers`
  };

  return {
    content: replies[email.category] || replies.Meeting,
    tone: email.category === 'Personal' ? 'friendly' : 'professional',
    estimated_response_time: '2 minutes',
    required_actions: email.category === 'Urgent' ? ['Investigate issue', 'Provide update'] : [],
    suggested_attachments: []
  };
}

function generateMockThread(threadId, emails) {
  const threadEmails = emails.filter(e => e.thread_id === threadId);
  return {
    thread_id: threadId,
    emails: threadEmails.length > 0 ? threadEmails : [emails[0]],
    subject: threadEmails[0]?.subject || 'Unknown',
    participants: [...new Set(threadEmails.map(e => e.sender))],
    last_updated: new Date().toISOString()
  };
}
