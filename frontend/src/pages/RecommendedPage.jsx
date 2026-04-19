import { useState } from "react";
import "./RecommendedPage.css";
import Footer from '../Components/Footer/Footer';

const API = "http://localhost:8000/api";

export default function App() {
  const [topic, setTopic] = useState("");
  const [newQuestions, setNewQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("");
  const [answers, setAnswers] = useState([]);
  const [results, setResults] = useState([]);
  const [maxReached, setMaxReached] = useState(0);

  const makeQuestions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      setNewQuestions(data.questions);
      setIndex(0);
      setAnswer("");
      setEvaluationResult(null);
      setAnswers([]);
      setResults([]);
      setMaxReached(0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const generateFromPDF = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/generate-pdf`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setNewQuestions(data.questions);
      setIndex(0);
      setAnswers([]);
      setResults([]);
      setMaxReached(0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const submit = async () => {
    const res = await fetch(`${API}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: newQuestions[index],
        answer: answer
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
  };

  const next = () => {
    const nextIndex = index + 1;
    setIndex(nextIndex);
    setAnswer(answers[nextIndex] || "");
    setEvaluationResult(results[nextIndex] || null);
    if (nextIndex > maxReached) setMaxReached(nextIndex);
  };

  const retry = () => {
    setAnswer("");
    setEvaluationResult(null);
    const updatedResults = [...results];
    updatedResults[index] = null;
    setResults(updatedResults);
  };

  const finish = () => {
    setTopic("");
    setNewQuestions([]);
    setIndex(0);
    setAnswer("");
    setEvaluationResult(null);
    setMode("");
    setAnswers([]);
    setResults([]);
    setMaxReached(0);
  };

  return (
    <>
      <div id="rec-page-root">
        <div className="rec-full-page">

          <div className="rec-left-side">
            {!mode && (
              <div className="mode">
                <h2 className="title">Select Input Type</h2>
                <button className="btn1" onClick={() => setMode("topic")}>Use Topic</button>
                <button className="btn2" onClick={() => setMode("pdf")}>Upload PDF</button>
              </div>
            )}

            {mode === "topic" && (
              <div className="input">
                <h2 className="title">Enter Topic</h2>
                <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g. OSI Model" />
                <button className="btn3" onClick={makeQuestions}>Generate</button>
              </div>
            )}

            {mode === "pdf" && (
              <div className="input">
                <h2 className="title">Upload PDF</h2>
                <input className="input" type="file" onChange={(e) => setFile(e.target.files[0])} />
                <button className="btn3" onClick={generateFromPDF}>Generate from PDF</button>
              </div>
            )}

            {newQuestions.length > 0 && (
              <div className="left-ques">
                <h3 className="title">Your Attempt:</h3>
                <div className="rec-circle-grid">
                  {Array.from({ length: maxReached + 1 }).map((_, i) => (
                    <div
                      key={i}
                      className={`rec-nav-circle ${index === i ? "active" : ""} ${answers[i] ? "done" : ""}`}
                      onClick={() => {
                        setIndex(i);
                        setAnswer(answers[i] || "");
                        setEvaluationResult(results[i] || null);
                      }}
                    >
                      {i + 1}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {loading && <p className="msg">Processing...</p>}
          </div>

          <div className="rec-right-side">
            {newQuestions.length > 0 && (
              <div className="content">
                <h1 className="heading-ques">Question {index + 1}</h1>
                <p className="text-ques">{newQuestions[index]}</p>

                <textarea
                  className="textarea"
                  value={answer}
                  placeholder="Type your answer here..."
                  onChange={(e) => {
                    setAnswer(e.target.value);
                    setEvaluationResult(null);
                  }}
                />

                {!evaluationResult ? (
                  <button className="btn1" onClick={submit}>Submit Answer</button>
                ) : (
                  <div className="evaluation-rec">
                    <div className="score-eval">
                      <span><b>Correctness:</b> {evaluationResult.correctness}</span>
                      <span><b>Score:</b> {evaluationResult.percentage}%</span>
                    </div>
                    <div className="feedback">
                      <p><b>What is Missing:</b> {evaluationResult.wrong}</p>
                      <p><b>Correct Answer:</b> {evaluationResult.correct_answer}</p>
                      <p><b>Feedback:</b> {evaluationResult.feedback}</p>
                    </div>

                    <div className="rec-action-row">
                      <button className="rec-btn-secondary" onClick={retry}>Retry</button>
                      {index < newQuestions.length - 1 ? (
                        <button className="btn1" onClick={next}>Next</button>
                      ) : (
                        <button className="btn-finish" onClick={finish}>Finish</button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}