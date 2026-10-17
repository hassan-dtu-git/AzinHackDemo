import { FormEvent, useEffect, useState } from "react";

type Citation = { url: string; title: string };
type EvidenceNode = { id: string; type: "source" | "claim"; label: string; url?: string };
type EvidenceEdge = { source: string; target: string; relation: string };
type EvidenceGraph = { nodes: EvidenceNode[]; edges: EvidenceEdge[] };
type GapCandidate = { description: string; source_url: string; source_title: string; basis: string };
type RunHistoryResponse = { runs: RunResponse[] };
type RunResponse = {
  run_id: string;
  question: string;
  status: string;
  created_at: string;
  stages: string[];
  message: string;
  report?: string | null;
  citations?: Citation[];
  error?: string | null;
  evidence_graph?: EvidenceGraph;
  gap_candidates?: GapCandidate[];
  gap_analysis_note?: string;
};

const sampleQuestion = "Can AI detect river pollution using satellite imagery?";
const terminalStatuses = new Set(["COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"]);

export default function App() {
  const [question, setQuestion] = useState("");
  const [run, setRun] = useState<RunResponse | null>(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState<RunResponse[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  async function refreshHistory() {
    try {
      const response = await fetch("/api/research-runs");
      if (response.ok) {
        const body = (await response.json()) as RunHistoryResponse;
        setHistory(body.runs);
      }
    } catch {
      // History is an enhancement; the current run remains usable if this request fails.
    } finally {
      setLoadingHistory(false);
    }
  }

  async function reopenRun(runId: string) {
    setError("");
    try {
      const response = await fetch(`/api/research-runs/${encodeURIComponent(runId)}`);
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? "Could not reopen this research run.");
      }
      setRun((await response.json()) as RunResponse);
      void refreshHistory();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not reopen this research run.");
    }
  }

  useEffect(() => {
    void refreshHistory();
  }, []);

  useEffect(() => {
    if (!run || terminalStatuses.has(run.status)) return;
    const timeout = window.setTimeout(async () => {
      try {
        const response = await fetch(`/api/research-runs/${encodeURIComponent(run.run_id)}`);
        if (!response.ok) {
          const body = await response.json().catch(() => null);
          throw new Error(body?.detail ?? "Could not retrieve research status.");
        }
        setRun((await response.json()) as RunResponse);
        void refreshHistory();
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Could not refresh research status.");
        setRun((current) => current ? { ...current, message: "Status refresh failed; retrying shortly." } : current);
      }
    }, 5000);
    return () => window.clearTimeout(timeout);
  }, [run]);

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
        const detail = await response.json().catch(() => null);
        throw new Error(
          typeof detail?.detail === "string"
            ? detail.detail
            : "Could not start research. Check the backend and TinyFish configuration.",
        );
      }

      setRun((await response.json()) as RunResponse);
      void refreshHistory();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error.");
    } finally {
      setSubmitting(false);
    }
  }

  const isTerminal = run ? terminalStatuses.has(run.status) : false;
  const hasReport = Boolean(run?.report);

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

        <section className="history-section" aria-labelledby="history-heading">
          <div className="history-heading-row">
            <div>
              <p className="eyebrow">YOUR WORK</p>
              <h3 id="history-heading">Recent research runs</h3>
            </div>
            <button className="sample-button" type="button" onClick={() => void refreshHistory()}>
              Refresh history
            </button>
          </div>
          {loadingHistory ? (
            <p className="muted-note">Loading saved runs…</p>
          ) : history.length === 0 ? (
            <p className="muted-note">Your submitted research runs will appear here so you can reopen them later.</p>
          ) : (
            <ul className="history-list">
              {history.map((item) => (
                <li key={item.run_id}>
                  <button className="history-item" type="button" onClick={() => void reopenRun(item.run_id)}>
                    <span className="history-item-copy">
                      <strong>{item.question || "Research question"}</strong>
                      <small>{new Date(item.created_at).toLocaleString()}</small>
                    </span>
                    <span className={`history-status history-status-${item.status.toLowerCase()}`}>{item.status.replaceAll("_", " ")}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        {error && <p className="alert error" role="alert">{error}</p>}

        {run && (
          <section className="run-panel" aria-live="polite">
            <div className="run-panel-heading">
              <div>
                <p className="eyebrow">RESEARCH RUN</p>
                <h3>Research pipeline</h3>
              </div>
              <span className={isTerminal && run.status !== "COMPLETED" ? "pending-pill failed-pill" : "pending-pill"}>
                {run.status.replaceAll("_", " ")}
              </span>
            </div>
            <p className="run-question">“{run.question || question}”</p>
            <ol className="pipeline">
              {run.stages.map((stage, index) => (
                <li key={stage}>
                  <span className="pipeline-number">{String(index + 1).padStart(2, "0")}</span>
                  <span>{stage}</span>
                </li>
              ))}
            </ol>
            <p className="alert notice">{run.message}</p>
            {run.error && (
              <p className="alert error">
                Provider reported a terminal error. Partial results may still be available.
              </p>
            )}
            <p className="run-id">Run ID: <code>{run.run_id}</code></p>

            {hasReport && (
              <section className="report-section">
                <p className="eyebrow">SOURCE-BACKED REPORT</p>
                <h3>Research findings</h3>
                <pre className="report-text">{run.report}</pre>
                <p className="source-heading">Sources returned by TinyFish ({run.citations?.length ?? 0})</p>
                {run.citations && run.citations.length > 0 ? (
                  <ol className="source-list">
                    {run.citations.map((citation) => (
                      <li key={citation.url}>
                        <a href={citation.url} target="_blank" rel="noreferrer">
                          {citation.title || citation.url}
                        </a>
                        {citation.title && <span className="source-url">{citation.url}</span>}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="muted-note">The provider response did not include a normalized citation list. Review the report and provider evidence before relying on its claims.</p>
                )}
              </section>
            )}
            {run.evidence_graph && run.evidence_graph.nodes.length > 0 && (
              <section className="evidence-graph" aria-labelledby="evidence-graph-heading">
                <p className="eyebrow">TRACEABLE EVIDENCE</p>
                <h3 id="evidence-graph-heading">Evidence graph</h3>
                <p className="muted-note">
                  Nodes and links are derived from explicit provider evidence. “Associated” means a source was linked to a claim; it is not a verified support or contradiction judgment.
                </p>
                <div className="graph-nodes">
                  {run.evidence_graph.nodes.map((node) => (
                    <article className={`graph-node graph-node-${node.type}`} key={node.id}>
                      <span className="graph-node-type">{node.type === "source" ? "SOURCE" : "CLAIM"}</span>
                      {node.type === "source" && node.url ? (
                        <a href={node.url} target="_blank" rel="noreferrer">{node.label}</a>
                      ) : (
                        <p>{node.label}</p>
                      )}
                    </article>
                  ))}
                </div>
                <h4 className="relationship-heading">Relationships ({run.evidence_graph.edges.length})</h4>
                {run.evidence_graph.edges.length > 0 ? (
                  <ul className="relationship-list">
                    {run.evidence_graph.edges.map((edge, index) => {
                      const source = run.evidence_graph?.nodes.find((node) => node.id === edge.source);
                      const target = run.evidence_graph?.nodes.find((node) => node.id === edge.target);
                      return (
                        <li key={`${edge.source}-${edge.target}-${index}`}>
                          <span>{source?.label ?? edge.source}</span>
                          <strong>{edge.relation.replaceAll("_", " ")}</strong>
                          <span>{target?.label ?? edge.target}</span>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p className="muted-note">No explicit source-to-claim links were available in the provider evidence.</p>
                )}
              </section>
            )}
            {run.gap_candidates && run.gap_candidates.length > 0 && (
              <section className="gap-analysis" aria-labelledby="gap-analysis-heading">
                <p className="eyebrow">CANDIDATE RESEARCH GAPS</p>
                <h3 id="gap-analysis-heading">Limitations and future-work leads</h3>
                <p className="muted-note">
                  {run.gap_analysis_note ?? "These are leads from explicit source limitations, not proof that a topic is globally novel."}
                </p>
                <ol className="gap-list">
                  {run.gap_candidates.map((candidate, index) => (
                    <li key={`${candidate.source_url}-${index}`}>
                      <p>{candidate.description}</p>
                      <a href={candidate.source_url} target="_blank" rel="noreferrer">
                        {candidate.source_title || candidate.source_url}
                      </a>
                      <small>{candidate.basis}</small>
                    </li>
                  ))}
                </ol>
              </section>
            )}

            {isTerminal && !hasReport && (
              <p className="muted-note">This run ended without a final report. Check the provider configuration/quota and try again only after confirming the previous run's status.</p>
            )}
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
        <span>Early MVP · TinyFish Research API</span>
      </footer>
    </main>
  );
}
