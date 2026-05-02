import { useState, useEffect, useRef } from "react";
import "./RecommendedPage.css";

const API = "http://localhost:8000/api";

export default function App() {
  // Logic State
  const [topic, setTopic] = useState("");
  const [newQuestions, setNewQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [activeMode, setActiveMode] = useState("topic");
  const [answers, setAnswers] = useState([]);
  const [results, setResults] = useState([]);
  const [maxReached, setMaxReached] = useState(0);
  const [allQuestions, setAllQuestions] = useState([]);
  const [showQuiz, setShowQuiz] = useState(false);
  
  // New Document & Level Logic State
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [difficultyLevel, setDifficultyLevel] = useState(1);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const fileInputRef = useRef(null);

  // -------------------------------
  // FETCH DOCUMENTS
  // -------------------------------
  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/documents/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setDocuments(data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDocuments();
    window.addEventListener("documentsUpdated", fetchDocuments);
    return () => window.removeEventListener("documentsUpdated", fetchDocuments);
  }, []);

  // -------------------------------
  // FILE UPLOAD
  // -------------------------------
  const processFile = async (file) => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API}/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);

      setSelectedDoc({ id: data.id, file_name: file.name });
      window.dispatchEvent(new Event("documentsUpdated"));
      setShowUploadModal(false);
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  };

  // -------------------------------
  // GENERATE QUESTIONS
  // -------------------------------
  const makeQuestions = async () => {
    if (activeMode === "topic" && !topic.trim()) return;
    if (activeMode === "pdf" && !selectedDoc) return;

    setLoading(true);
    setDifficultyLevel(1);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/conceptual/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          topic: topic || "",
          document_id: selectedDoc?.id || null,
          difficulty_level: 1
        })
      });

      const data = await res.json();
      const questions = data?.questions || [];

      setAllQuestions(questions);
      setNewQuestions(questions);
      setIndex(0);
      setAnswer("");
      setEvaluationResult(null);
      setAnswers([]);
      setResults([]);
      setMaxReached(0);
      setShowQuiz(true);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const generateMoreQuestions = async () => {
    if (difficultyLevel >= 3) return;
    const nextLevel = difficultyLevel + 1;
    setDifficultyLevel(nextLevel);
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/conceptual/generate-more`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          topic: topic || "",
          document_id: selectedDoc?.id || null,
          current_questions: allQuestions || [],
          difficulty_level: nextLevel
        })
      });

      const data = await res.json();
      const more = data?.questions || [];
      const updated = [...allQuestions, ...more];
      setAllQuestions(updated);
      setNewQuestions(updated);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  // -------------------------------
  // EVALUATE & NAV
  // -------------------------------
  const submit = async () => {
    setEvaluating(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API}/conceptual/evaluate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          question: newQuestions[index],
          answer
        })
      });

      const data = await res.json();
      setEvaluationResult(data);
      const updatedAnswers = [...answers];
      updatedAnswers[index] = answer;
      setAnswers(updatedAnswers);
      const updatedResults = [...results];
      updatedResults[index] = data;
      setResults(updatedResults);
      if (index + 1 > maxReached) setMaxReached(index + 1);
    } catch (e) {
      console.error(e);
    }
    setEvaluating(false);
  };

  const next = () => {
    const nextIndex = index + 1;
    setIndex(nextIndex);
    setAnswer(answers[nextIndex] || "");
    setEvaluationResult(results[nextIndex] || null);
  };

  const retry = () => {
    setAnswer("");
    setEvaluationResult(null);
    const updatedResults = [...results];
    updatedResults[index] = null;
    setResults(updatedResults);
  };

  const resetQuiz = () => {
    setShowQuiz(false);
    setNewQuestions([]);
    setAllQuestions([]);
    setIndex(0);
    setAnswer("");
    setEvaluationResult(null);
    setAnswers([]);
    setResults([]);
    setMaxReached(0);
    setTopic("");
    setSelectedDoc(null);
    setDifficultyLevel(1);
  };

  const goToQuestion = (i) => {
    setIndex(i);
    setAnswer(answers[i] || "");
    setEvaluationResult(results[i] || null);
  };

  const completedCount = answers.filter(a => a && a.trim()).length;
  const progress = newQuestions.length ? (completedCount / newQuestions.length) * 100 : 0;

  // -------------------------------
  // UI RENDERING
  // -------------------------------

  if (!showQuiz) {
    return (
      <div className="rec-app">
        <div className="rec-container">
          <div className="rec-hero">
            <h1 className="rec-hero-title">Test your understanding</h1>
            <p className="rec-hero-subtitle">
              Generate AI-powered questions and get instant feedback
            </p>
          </div>

          <div className="rec-mode-toggle">
            <button 
              className={`rec-mode-toggle-btn ${activeMode === 'topic' ? 'active' : ''}`}
              onClick={() => setActiveMode('topic')}
            >
              Topic Search
            </button>
            <button 
              className={`rec-mode-toggle-btn ${activeMode === 'pdf' ? 'active' : ''}`}
              onClick={() => setActiveMode('pdf')}
            >
              Upload Document
            </button>
          </div>

          <div className="rec-input-area">
            {activeMode === 'topic' ? (
              <div className="rec-search-box">
                <i className="fa-solid fa-magnifying-glass"></i>
                <input
                  type="text"
                  placeholder="e.g., Artificial Intelligence, React.js..."
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && makeQuestions()}
                />
                <button onClick={makeQuestions} disabled={loading || !topic.trim()}>
                  {loading ? 'Generating...' : 'Generate →'}
                </button>
              </div>
            ) : (
              <div className="rec-pdf-area">
                <div className="rec-upload-area" onClick={() => setShowUploadModal(true)}>
                  <div className="rec-upload-content">
                    <i className="fa-solid fa-file-pdf"></i>
                    <span>{selectedDoc ? selectedDoc.file_name : 'Click to choose or upload document'}</span>
                  </div>
                </div>
                <button onClick={makeQuestions} disabled={loading || !selectedDoc}>
                  {loading ? 'Processing...' : 'Generate →'}
                </button>
              </div>
            )}
          </div>

          <div className="rec-promo-grid">
            <div className="rec-promo-card">
              <span className="rec-promo-icon">🤖</span>
              <div className="rec-promo-text"><h4>AI-Powered</h4></div>
            </div>
            <div className="rec-promo-card">
              <span className="rec-promo-icon">📊</span>
              <div className="rec-promo-text"><h4>Instant Feedback</h4></div>
            </div>
            <div className="rec-promo-card">
              <span className="rec-promo-icon">🎯</span>
              <div className="rec-promo-text"><h4>Adaptive Learning</h4></div>
            </div>
          </div>
        </div>

        {/* Upload/Selection Modal */}
        {showUploadModal && (
          <div className="rec-modal-overlay" onClick={() => setShowUploadModal(false)}>
            <div className="rec-modal-content" onClick={e => e.stopPropagation()}>
              <div className="rec-modal-header">
                <h3>Select Document</h3>
                <button className="rec-modal-close" onClick={() => setShowUploadModal(false)}>&times;</button>
              </div>
              <div className="rec-document-list">
                <label className="rec-modal-upload-btn">
                  <input type="file" accept=".pdf" onChange={handleFileChange} hidden />
                  <i className="fa-solid fa-plus"></i> Upload New PDF
                </label>
                {documents.map(doc => (
                  <div 
                    key={doc.id} 
                    className="rec-doc-item" 
                    onClick={() => { setSelectedDoc(doc); setShowUploadModal(false); }}
                  >
                    <i className="fa-solid fa-file-lines"></i>
                    <span>{doc.file_name}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Quiz Page
  return (
    <div className="rec-app">
      <div className="rec-container">
        <div className="rec-quiz-header">
          <button className="rec-back-home" onClick={resetQuiz}>
            <i className="fa-solid fa-arrow-left"></i> Back
          </button>
          
          <div className="rec-question-nav-wrapper">
            <div className="rec-question-nav">
              {newQuestions.map((_, i) => (
                <button
                  key={i}
                  className={`rec-q-dot ${index === i ? 'active' : ''} ${answers[i] ? 'done' : ''}`}
                  onClick={() => goToQuestion(i)}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          </div>
          
          <div className="rec-quiz-progress">
            <div className="rec-progress-text">{completedCount} / {newQuestions.length} Completed</div>
            <div className="rec-progress-bar">
              <div className="rec-progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>
        </div>

        <div className="rec-quiz-main">
          <div className="rec-question-card">
            <div className="rec-question-badge">Question {index + 1} (Level {difficultyLevel})</div>
            <h2 className="rec-question-text">{newQuestions[index]}</h2>
            
            <textarea
              className="rec-answer-input"
              value={answer}
              onChange={(e) => {
                setAnswer(e.target.value);
                setEvaluationResult(null);
              }}
              placeholder="Write your answer here..."
            />

            {evaluating && (
              <div className="rec-evaluating">
                <i className="fa-solid fa-spinner fa-spin"></i>
                <span>Evaluating your answer...</span>
              </div>
            )}

            {!evaluationResult && !evaluating ? (
              <button className="rec-submit-btn" onClick={submit} disabled={!answer.trim()}>
                Submit Answer <i className="fa-solid fa-paper-plane"></i>
              </button>
            ) : evaluationResult && (
              <div className="rec-evaluation">
                <div className="rec-score-card">
                   <div className="rec-score-circle">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="45" fill="none" stroke="#2a2a2a" strokeWidth="4"/>
                      <circle 
                        cx="50" cy="50" r="45" fill="none" stroke="#10b981" strokeWidth="4"
                        strokeDasharray={`${2 * Math.PI * 45}`}
                        strokeDashoffset={`${2 * Math.PI * 45 * (1 - (evaluationResult.percentage || 0) / 100)}`}
                        transform="rotate(-90 50 50)"
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="rec-score-text">
                      <span className="rec-score-value">{evaluationResult.percentage || 0}</span>
                      <span className="rec-score-unit">%</span>
                    </div>
                  </div>
                  <div className="rec-score-badge">{evaluationResult.correctness}</div>
                </div>

                <div className="rec-feedback-list">
                  <div className="rec-feedback-item feedback">
                    <i className="fa-solid fa-lightbulb"></i>
                    <div>
                      <strong>AI Feedback</strong>
                      <p>{evaluationResult.feedback}</p>
                    </div>
                  </div>
                </div>

                <div className="rec-action-buttons">
                  <button className="rec-btn-retry" onClick={retry}>
                    <i className="fa-solid fa-rotate-left"></i> Try Again
                  </button>
                  {index < newQuestions.length - 1 ? (
                    <button className="rec-btn-next" onClick={next}>
                      Next Question <i className="fa-solid fa-arrow-right"></i>
                    </button>
                  ) : (
                    <div className="rec-finish-group">
                      {difficultyLevel < 3 && (
                        <button className="rec-btn-more" onClick={generateMoreQuestions} disabled={loading}>
                          <i className="fa-solid fa-arrow-up-right-dots"></i> 
                          {loading ? 'Leveling up...' : 'More (Next Level)'}
                        </button>
                      )}
                      <button className="rec-btn-finish" onClick={resetQuiz}>
                        <i className="fa-solid fa-flag-checkered"></i> Finish
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}