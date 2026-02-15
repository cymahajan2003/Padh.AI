// QuickActions.jsx - With side by side layout
import './QuickActions.css';
import {
  FiUpload,
  FiFileText,
  FiCheckSquare,
  FiCpu,
  FiChevronRight,
  FiZap
} from 'react-icons/fi';
import { useCallback, useRef } from 'react';

function QuickActions() {
  const fileInputRef = useRef(null);

  const handleCardClick = useCallback((action) => {
    console.log(`✨ ${action} clicked`);
    
    if (action === 'upload') {
      handleUpload();
    }
  }, []);

  const handleUpload = useCallback(() => {
    if (!fileInputRef.current) {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png';
      input.multiple = false;
      
      input.onchange = (event) => {
        const file = event.target.files?.[0];
        if (file) {
          const fileName = file.name;
          const fileType = fileName.split('.').pop().toLowerCase();
          
          if (window.addRecentDocument) {
            window.addRecentDocument(fileName, fileType);
          }
          
          console.log(`📄 Uploaded: ${fileName}`);
        }
        input.remove();
      };
      
      fileInputRef.current = input;
    }
    
    fileInputRef.current.click();
  }, []);

  const quickActions = [
    { 
      id: 'upload', 
      title: 'Upload', 
      desc: 'Add documents', 
      icon: FiUpload
    },
    { 
      id: 'summary', 
      title: 'Summary', 
      desc: 'AI insights', 
      icon: FiFileText
    },
    { 
      id: 'quiz', 
      title: 'Quiz', 
      desc: 'Test yourself', 
      icon: FiCheckSquare
    },
    { 
      id: 'assistant', 
      title: 'Assistant', 
      desc: '24/7 help', 
      icon: FiCpu
    }
  ];

  return (
    <div className="quick-actions-wrapper">
      <section className="quick-actions">
        <div className="qa-container">
          {/* NEW: Side by side wrapper */}
          <div className="qa-sections-wrapper">
            {/* Quick Actions Section */}
            <div className="qa-section">
              <div className="qa-header">
                <div className="header-left">
                  <h2 className="qa-title">Quick Actions</h2>
                </div>
                <span className="header-badge">{quickActions.length}</span>
              </div>

              <div className="qa-scroll-container">
                <div className="qa-cards">
                  {quickActions.map(({ id, title, desc, icon: Icon }) => (
                    <div
                      key={id}
                      className={`qa-card ${id}`}
                      onClick={() => handleCardClick(id)}
                      role="button"
                      tabIndex={0}
                      aria-label={`${title} - ${desc}`}
                    >
                      <div className="card-top">
                        <div className="card-icon-wrapper">
                          <Icon className="qa-icon" />
                        </div>
                        <FiChevronRight className="card-arrow" />
                      </div>
                      <div className="card-text">
                        <h3 className="card-title">{title}</h3>
                        <p className="card-desc">{desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommended Section */}
            <div className="recommended-section">
              <div className="qa-header">
                <div className="header-left">
                  <h2 className="qa-title">Recommended</h2>
                </div>
                <span className="header-badge">New</span>
              </div>

              <div className="recommended-card">
                <div className="recommended-content">
                  <div className="recommended-icon">
                    <FiZap />
                  </div>
                  
                  <div className="recommended-text">
                    <h3 className="recommended-title">Anti-Lazy AI</h3>
                    <p className="recommended-tagline">Learn actively</p>
                  </div>
                </div>
                
                <div className="recommended-footer">
                  <p className="recommended-desc">
                    Smart questioning for better learning
                  </p>
                  <button 
                    className="try-now-btn"
                    onClick={() => console.log('🎯 Try now clicked')}
                  >
                    Try
                  </button>
                </div>
              </div>

              {/* Optional stats */}
              {/* <div className="stats-mini">
                <div className="stat-item">
                  <span className="stat-dot"></span>
                  <span className="stat-label">Docs</span>
                  <span className="stat-value">1.2k</span>
                </div>
                <div className="stat-item">
                  <span className="stat-dot"></span>
                  <span className="stat-label">Quiz</span>
                  <span className="stat-value">856</span>
                </div>
              </div> */}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default QuickActions;