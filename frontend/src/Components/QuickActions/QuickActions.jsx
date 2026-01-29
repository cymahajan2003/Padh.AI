import './QuickActions.css';
import {
  FiUpload,
  FiFileText,
  FiCheckSquare,
  FiCpu,
  FiChevronRight,
  FiStar,
  FiZap
} from 'react-icons/fi';

function QuickActions() {
  const handleCardClick = (action) => {
    console.log(`Clicked: ${action}`);
    // Add your click handler logic here
  };

  return (
    <section className="quick-actions">
      <div className="qa-container">
        <div className="qa-header">
          <h2 className="qa-title">Quick Actions</h2>
        </div>

        <div className="qa-scroll">
          <div className="qa-cards">
            {/* Upload Card */}
            <div 
              className="qa-card upload"
              onClick={() => handleCardClick('Upload Document')}
            >
              <div className="card-content">
                <div className="card-text">
                  <h3 className="card-title">Upload Docs</h3>
                  <p className="card-desc">Start learning with AI</p>
                </div>
                <div className="card-icon-wrapper">
                  <FiUpload className="qa-icon" />
                </div>
              </div>
              <div className="card-hover">
                <span>Get Started</span>
                <FiChevronRight className="hover-arrow" />
              </div>
            </div>

            {/* Summary Card */}
            <div 
              className="qa-card summary"
              onClick={() => handleCardClick('AI Summary')}
            >
              <div className="card-content">
                <div className="card-text">
                  <h3 className="card-title">AI Summary</h3>
                  <p className="card-desc">Quick insights & notes</p>
                </div>
                <div className="card-icon-wrapper">
                  <FiFileText className="qa-icon" />
                </div>
              </div>
              <div className="card-hover">
                <span>Try Now</span>
                <FiChevronRight className="hover-arrow" />
              </div>
            </div>

            {/* Quiz Card */}
            <div 
              className="qa-card quiz"
              onClick={() => handleCardClick('Practice Quiz')}
            >
              <div className="card-content">
                <div className="card-text">
                  <h3 className="card-title">Practice Quiz</h3>
                  <p className="card-desc">Test your knowledge</p>
                </div>
                <div className="card-icon-wrapper">
                  <FiCheckSquare className="qa-icon" />
                </div>
              </div>
              <div className="card-hover">
                <span>Start Quiz</span>
                <FiChevronRight className="hover-arrow" />
              </div>
            </div>

            {/* Assistant Card */}
            <div 
              className="qa-card assistant"
              onClick={() => handleCardClick('AI Assistant')}
            >
              <div className="card-content">
                <div className="card-text">
                  <h3 className="card-title">AI Assistant</h3>
                  <p className="card-desc">Get instant help</p>
                </div>
                <div className="card-icon-wrapper">
                  <FiCpu className="qa-icon" />
                </div>
              </div>
              <div className="card-hover">
                <span>Ask AI</span>
                <FiChevronRight className="hover-arrow" />
              </div>
            </div>
          </div>
        </div>

        {/* Recommended Section */}
        <div className="recommended-section">
          <div className="qa-header">
            <h2 className="qa-title">Recommended</h2>
          </div>

          <div className="recommended-card">
            <div className="recommended-content">
              <div className="recommended-icon-wrapper">
                <FiZap className="recommended-icon" />
              </div>
              
              <div className="recommended-text">
                <div className="recommended-badge">
                  <FiStar className="star-icon" />
                  <span>Top Pick</span>
                </div>
                <h3 className="recommended-title">Anti-Lazy AI</h3>
                <p className="recommended-tagline">Learn by thinking, not copying.</p>
              </div>
            </div>
            
            <div className="recommended-footer">
              <div className="recommended-meta">
                <div className="meta-item">
                  <span className="meta-dot" style={{ background: '#facc15' }}></span>
                  <span>Smart Learning</span>
                </div>
                <div className="meta-item">
                  <span className="meta-dot" style={{ background: '#10b981' }}></span>
                  <span>Proven Results</span>
                </div>
              </div>
              <button className="try-now-btn">
                Try Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default QuickActions;