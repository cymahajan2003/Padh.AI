import { useState } from "react";
import "./RecommendedPage.css";
import Footer from "../Components/Footer/Footer";

const API = "http://localhost:8000/api";

export default function RecommendedPage() { // ✅ FIXED NAME
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

      if (!res.ok) {
        alert(data.detail || "Failed to generate questions");
        return;
      }

      setNewQuestions(data.questions || []);
      setIndex(0);
      setAnswer("");
      setEvaluationResult(null);
      setAnswers([]);
      setResults([]);
      setMaxReached(0);
    } catch (e) {
      console.error(e);
      alert("Server error");
    } finally {
      setLoading(false);
    }
  };

  const generateFromPDF = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const token = localStorage.getItem("token");

    if (!token) {
      alert("Please login first");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API}/generate-pdf`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.detail || "Failed to process PDF");
        return;
      }

      setNewQuestions(data.questions || []);
      setIndex(0);
      setAnswers([]);
      setResults([]);
      setMaxReached(0);

    } catch (e) {
      console.error(e);
      alert("Server error");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    try {
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

    } catch (e) {
      console.error(e);
      alert("Evaluation failed");
    }
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
                <div className="mode-options">
                  <button className="btn1" onClick={() => setMode("topic")}>
                    Use Topic
                  </button>
                  <button className="btn1" onClick={() => setMode("pdf")}>
                    Upload PDF
                  </button>
                </div>
              </div>
            )}

            {mode === "topic" && (
              <div className="rec-topic-group">
                <h2 className="title">Enter Topic</h2>
                <div className="rec-combined-input">
                  <input
                    className="input"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g. OSI Model"
                  />
                  <button className="rec-btn-attached" onClick={makeQuestions}>
                    Generate
                  </button>
                </div>
              </div>
            )}

            {mode === "pdf" && (
              <div className="input-group">
                <h2 className="title">Select Document</h2>
                <div className="rec-combined-upload">
                  <input
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                  />
                  <button onClick={generateFromPDF}>Process</button>
                </div>
              </div>
            )}

            {loading && <p className="msg">Processing...</p>}
          </div>

          <div className="rec-right-side">

            {newQuestions.length > 0 ? (
              <div className="content">

                <h1>Question {index + 1}</h1>
                <p>{newQuestions[index]}</p>

                <textarea
                  value={answer}
                  onChange={(e) => {
                    setAnswer(e.target.value);
                    setEvaluationResult(null);
                  }}
                />

                {!evaluationResult ? (
                  <button onClick={submit}>Submit</button>
                ) : (
                  <>
                    <p><b>Score:</b> {evaluationResult.percentage}%</p>
                    <p><b>Feedback:</b> {evaluationResult.feedback}</p>

                    {index < newQuestions.length - 1 ? (
                      <button onClick={next}>Next</button>
                    ) : (
                      <button onClick={finish}>Finish</button>
                    )}
                  </>
                )}

              </div>
            ) : (
              <div className="rec-empty-state">
                <h2>Start learning today</h2>
                <p>Smart questioning for better learning</p>
              </div>
            )}

          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}