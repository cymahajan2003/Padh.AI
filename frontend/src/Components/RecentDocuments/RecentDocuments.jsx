import { useState, useEffect } from 'react';
import { FiFile, FiChevronRight, FiX } from 'react-icons/fi';
import './RecentDocuments.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const buildApiUrl = (path) => {
  const base = API_BASE.replace(/\/+$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (base.endsWith('/api')) {
    return `${base}${cleanPath}`;
  }
  return `${base}/api${cleanPath}`;
};

const RecentDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [showAll, setShowAll] = useState(false);
  const [allDocuments, setAllDocuments] = useState([]);

  const mapApiDocument = (doc, index) => ({
    id: doc.id ?? `${doc.file_url || 'doc'}-${index}`,
    name: doc.file_name || 'Untitled Document',
    size: '—',
    date: doc.created_at || new Date().toISOString(),
    fileUrl: doc.file_url || '',
    plagiarismScore: doc.plagiarism_score,
  });

  // Load per-user documents from backend (Supabase-backed).
  const loadDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setAllDocuments([]);
        setDocuments([]);
        return;
      }

      const response = await fetch(buildApiUrl('/documents/'), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.error('Failed to fetch documents:', response.status);
        setAllDocuments([]);
        setDocuments([]);
        return;
      }

      const data = await response.json().catch(() => []);
      const parsedDocs = Array.isArray(data)
        ? data.map((doc, index) => mapApiDocument(doc, index))
        : [];

      setAllDocuments(parsedDocs);

      setDocuments(showAll ? parsedDocs : parsedDocs.slice(0, 3));
    } catch (err) {
      console.error('Load error:', err);
      setAllDocuments([]);
      setDocuments([]);
    }
  };

  // Initial load
  useEffect(() => {
    loadDocuments();
  }, []);

  // Keep displayed slice in sync with showAll state.
  useEffect(() => {
    setDocuments(showAll ? allDocuments : allDocuments.slice(0, 3));
  }, [showAll, allDocuments]);

  // Listen for updates from upload flow and re-fetch from backend.
  useEffect(() => {
    const handleCustomUpdate = () => {
      loadDocuments();
    };

    window.addEventListener('documentsUpdated', handleCustomUpdate);

    return () => {
      window.removeEventListener('documentsUpdated', handleCustomUpdate);
    };
  }, []);

  // 🧾 FORMAT DATE
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  // 🗑 DELETE
  const handleDeleteDocument = (e, docId) => {
    e.stopPropagation();
    alert('Delete is not implemented yet for Supabase documents.');
  };

  // 📂 CLICK
  const handleDocumentClick = (doc) => {
    if (doc.fileUrl) {
      window.open(doc.fileUrl, '_blank', 'noopener,noreferrer');
      return;
    }
    alert(`Opening: ${doc.name}`);
  };

  // 🔁 TOGGLE VIEW
  const toggleViewAll = () => {
    if (showAll) {
      setDocuments(allDocuments.slice(0, 3));
      setShowAll(false);
    } else {
      setDocuments(allDocuments);
      setShowAll(true);
    }
  };

  // 🧠 SAFE DISPLAY
  const displayDocs = showAll ? (documents || []) : [...(documents || [])];

  // Fill empty slots
  if (!showAll && displayDocs.length < 3) {
    while (displayDocs.length < 3) {
      displayDocs.push({ id: `empty-${displayDocs.length}`, empty: true });
    }
  }

  return (
    <div className="recent-docs-wrapper">
      <section className="recent-docs">

        <div className="qa-header">
          <h2 className="qa-title">Recent Documents</h2>
        </div>

        <div className="recent-card">

          <div className="recent-list">
            {allDocuments.length > 0 ? (
              displayDocs.map((doc, index) => (
                <div
                  key={doc.id || index}
                  className={`recent-row ${doc.empty ? 'empty-row' : ''}`}
                  onClick={() => !doc.empty && handleDocumentClick(doc)}
                >
                  <div className="doc-content">
                    <div className="doc-icon-text">
                      <div className="doc-icon-wrapper">
                        <FiFile className="doc-icon" />
                      </div>

                      <div className="doc-details">
                        {doc.empty ? (
                          <>
                            <span className="doc-name empty-name">No document uploaded</span>
                            <span className="doc-date empty-date">Upload a document</span>
                          </>
                        ) : (
                          <>
                            <span className="doc-name">{doc.name}</span>
                            <span className="doc-date">
                              {formatDate(doc.date)} • {doc.size || "—"}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {!doc.empty && (
                    <div className="doc-row-actions">
                      <button
                        className="doc-remove-btn"
                        onClick={(e) => handleDeleteDocument(e, doc.id)}
                      >
                        <FiX />
                      </button>
                      <FiChevronRight />
                    </div>
                  )}
                </div>
              ))
            ) : (
              [1, 2, 3].map((_, index) => (
                <div key={index} className="recent-row empty-row">
                  <div className="doc-content">
                    <div className="doc-icon-text">
                      <div className="doc-icon-wrapper">
                        <FiFile className="doc-icon" />
                      </div>
                      <div className="doc-details">
                        <span className="doc-name empty-name">No document uploaded</span>
                        <span className="doc-date empty-date">Upload a document</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="recent-footer">
            <p>
              {showAll ? 'Showing all documents' : 'View all your uploaded documents'}
            </p>
            <button onClick={toggleViewAll}>
              {showAll ? 'Show Less' : 'View All'}
            </button>
          </div>

        </div>
      </section>
    </div>
  );
};

export default RecentDocuments;