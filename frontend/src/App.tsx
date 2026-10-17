import { FormEvent, useState } from "react";

type RunResponse = {
  run_id: string;
  question: string;
  status: "pending_integration";
  created_at: string;
  stages: string[];
  message: string;
};

const sampleQuestion = "Can AI detect river pollution using satellite imagery?";

export default function App() {
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<RunResponse | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setRun(null);

    if (!question.trim()) {
      setError("Enter a research question to continue.");
      return;
    }

    setSubmitting(true);
    try {
      const response = await fetch("/api/research-runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        if (response.status === 404 || response.status >= 500) {
          throw new Error("Could not reach the API. Check that the backend is running.");
        }
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail?.[0]?.msg ?? "The question could not be submitted.");
      }

      setRun((await response.json()) as RunResponse);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="wordmark" href="/" aria-label="ResearchPilot AI home">
          <span className="brand-mark">R</span>
          <span>ResearchPilot <span className="muted">AI</span></span>
        </a>
        <span className="status-pill"><span className="status-dot" /> Research workbench</span>
      </header>

      <section className="hero">
        <p className="eyebrow">RESEARCH, WITH RECEIPTS</p>
        <h1>Move from question<br /><span>to evidence.</span></h1>
        <p className="hero-copy">
          A research assistant designed to make sources, disagreements, and unanswered
          questions visible—not just produce another answer.
        </p>
      </section>

      <section className="workspace" aria-labelledby="question-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">START A RESEARCH RUN</p>
            <h2 id="question-heading">What do you want to investigate?</h2>
          </div>
          <span className="step-count">01 / QUESTION</span>
        </div>

        <form onSubmit={handleSubmit}>
          <label className="sr-only" htmlFor="research-question">Research question</label>
          <textarea
            id="research-question"
            rows={4}
            maxLength={1000}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a focused scientific or technical question…"
          />
          <div className="form-footer">
            <button className="sample-button" type="button" onClick={() => setQuestion(sampleQuestion)}>
              Use example question ↗
            </button>
            <span className="character-count">{question.length}/1000</span>
          </div>
          <div className="submit-row">
            <p>Reports should make evidence and search limitations explicit.</p>
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? "Submitting…" : "Start research run"} <span aria-hidden="true">→</span>
            </button>
          </div>
        </form>

        {error && <p className="alert error" role="alert">{error}</p>}

        {run && (
          <section className="run-panel" aria-live="polite">
            <div className="run-panel-heading">
              <div>
                <p className="eyebrow">RUN CREATED</p>
                <h3>Research pipeline</h3>
              </div>
              <span className="pending-pill">Integration pending</span>
            </div>
            <p className="run-question">“{run.question}”</p>
            <ol className="pipeline">
              {run.stages.map((stage, index) => (
                <li key={stage}>
                  <span className="pipeline-number">{String(index + 1).padStart(2, "0")}</span>
                  <span>{stage}</span>
                  <span className="stage-status">Not started</span>
                </li>
              ))}
            </ol>
            <p className="alert notice">{run.message}</p>
            <p className="run-id">Run ID: <code>{run.run_id}</code></p>
          </section>
        )}
      </section>

      <section className="principles" aria-label="Product principles">
        <article>
          <span className="principle-icon">01</span>
          <h3>Traceable claims</h3>
          <p>Findings should link to original sources and supporting evidence.</p>
        </article>
        <article>
          <span className="principle-icon">02</span>
          <h3>Visible uncertainty</h3>
          <p>Conflicts, limitations, and confidence rationale should be explicit.</p>
        </article>
        <article>
          <span className="principle-icon">03</span>
          <h3>Honest research gaps</h3>
          <p>A thin search is a search limitation—not proof of global novelty.</p>
        </article>
      </section>

      <footer className="footer">
        <span>ResearchPilot AI · Team ByteForge · AzinHack</span>
        <span>Early MVP foundation</span>
      </footer>
    </main>
  );
}
