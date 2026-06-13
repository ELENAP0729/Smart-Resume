'use client';
import { useEffect, useState } from 'react';

type AnyObj = Record<string, any>;
const API = 'http://127.0.0.1:8000';

function List({ items }: { items?: string[] }) {
  if (!items || items.length === 0) return <p className="empty">No data yet.</p>;
  return <ul>{items.map((x, i) => <li key={i}>{x}</li>)}</ul>;
}

function ResultView({ result }: { result: AnyObj | null }) {
  if (!result) return <div className="empty">Upload a resume, choose an output language, and optionally paste job requirements to generate the resume analysis report.</div>;
  const job = result.job_fit_analysis || {};
  const opt = result.resume_optimization || {};
  return <>
    <div className="metrics">
      <div className="metric"><div className="num">{job.overall_match_score ?? 0}</div><div className="label">Job Match / 100</div></div>
      <div className="metric"><div className="num">{result.extracted_skills?.length ?? 0}</div><div className="label">Extracted Skills</div></div>
      <div className="metric"><div className="num">{result.evidence_map?.length ?? 0}</div><div className="label">Evidence Items</div></div>
    </div>

    <div className="section"><h3>Profile Summary</h3><p>{result.profile_summary}</p></div>

    <div className="section"><h3>Extracted Skills</h3><div className="tags">{(result.extracted_skills || []).map((s: string, i: number) => <span className="tag" key={i}>{s}</span>)}</div></div>

    <div className="section"><h3>Job Fit Analysis</h3><p>{job.target_role_summary}</p><h4>Matched Requirements</h4><List items={job.matched_requirements}/><h4>Missing Requirements</h4><List items={job.missing_requirements}/><h4>Transferable Strengths</h4><List items={job.transferable_strengths}/><h4>Risk Factors</h4><List items={job.risk_factors}/><h4>Hiring Recommendation</h4><p>{job.hiring_recommendation}</p></div>

    <div className="section"><h3>Resume Optimization</h3><p>{opt.summary}</p><h4>Priority Fixes</h4><List items={opt.priority_fixes}/><h4>Missing Keywords</h4><List items={opt.missing_keywords}/><h4>Rewritten Bullets</h4><List items={opt.rewritten_bullets}/><h4>Structure Suggestions</h4><List items={opt.structure_suggestions}/></div>

    <div className="section"><h3>Capability Scores</h3><table><thead><tr><th>Capability</th><th>Score</th><th>Reason</th></tr></thead><tbody>{(result.capability_scores || []).map((x: AnyObj, i: number) => <tr key={i}><td>{x.capability}</td><td>{x.score}</td><td>{x.reason}</td></tr>)}</tbody></table></div>

    <div className="section"><h3>Evidence Map</h3><table><thead><tr><th>Skill</th><th>Category</th><th>Evidence</th><th>Confidence</th></tr></thead><tbody>{(result.evidence_map || []).map((x: AnyObj, i: number) => <tr key={i}><td>{x.skill}</td><td>{x.category}</td><td>{x.evidence}</td><td>{Math.round((x.confidence || 0) * 100)}%</td></tr>)}</tbody></table></div>

    <div className="section"><h3>Interview Questions</h3><List items={job.interview_questions}/></div>
  </>;
}

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState('');
  const [language, setLanguage] = useState('English');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<AnyObj | null>(null);
  const [history, setHistory] = useState<AnyObj[]>([]);

  async function loadHistory() {
    try { const r = await fetch(`${API}/api/history`); setHistory(await r.json()); } catch {}
  }
  useEffect(() => { loadHistory(); }, []);

  async function submit() {
    if (!file) { setError('Please choose a resume or document first.'); return; }
    setLoading(true); setError(''); setResult(null);
    const form = new FormData(); form.append('file', file); form.append('job_description', job); form.append('language', language);
    try {
      const r = await fetch(`${API}/api/analyse`, { method: 'POST', body: form });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || 'Request failed');
      setResult(data.result); await loadHistory();
    } catch (e: any) { setError(e.message || String(e)); }
    finally { setLoading(false); }
  }

  async function openHistory(id: string) {
    setError('');
    const r = await fetch(`${API}/api/history/${id}`);
    const data = await r.json();
    if (!r.ok) { setError(data.detail || 'Failed to load history record.'); return; }
    setResult(data.result);
    setJob(data.job_description || '');
    setLanguage(data.language || 'English');
  }

  async function deleteHistory(id: string, e: React.MouseEvent<HTMLButtonElement>) {
    e.stopPropagation();
    const ok = window.confirm('Delete this analysis history record?');
    if (!ok) return;
    setError('');
    try {
      const r = await fetch(`${API}/api/history/${id}`, { method: 'DELETE' });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || 'Failed to delete history record.');
      await loadHistory();
    } catch (err: any) {
      setError(err.message || String(err));
    }
  }

  return <main className="page">
    <section className="hero"><h1>Smart Resume Analysis Assistant</h1><p>Analyse resumes against target job requirements with AI-powered document parsing, evidence mapping, job-fit scoring, gap analysis, resume optimization suggestions, bilingual reports, and saved analysis history.</p></section>
    <div className="grid">
      <aside>
        <div className="card"><h2>New Analysis</h2><label>Upload resume / PDF / Word / Markdown / image</label><input type="file" onChange={e => setFile(e.target.files?.[0] || null)} /><label>Analysis Language</label><select value={language} onChange={e => setLanguage(e.target.value)}><option value="English">English</option><option value="Chinese">中文</option></select><label>Target Job Requirements</label><textarea value={job} onChange={e => setJob(e.target.value)} placeholder="Paste the role description, required skills, responsibilities, selection criteria... / 可粘贴岗位要求、技能要求、职责描述..."/><button className="primary" disabled={loading} onClick={submit}>{loading ? 'Analysing...' : 'Generate Resume Analysis'}</button></div>
        <div className="card" style={{marginTop: 18}}><h2>History</h2>{history.length === 0 ? <p className="empty">No history yet.</p> : history.map(h => <div className="history-item" key={h.id} onClick={() => openHistory(h.id)}><div className="history-row"><div><div className="history-title">{h.filename}</div><div className="history-meta">Score: {h.match_score}/100 · {h.language || 'English'} · {new Date(h.created_at).toLocaleString()}</div></div><button className="delete-btn" onClick={(e) => deleteHistory(h.id, e)}>Delete</button></div></div>)}</div>
      </aside>
      <section className="card"><h2>Analysis Result</h2>{error && <div className="error"><b>Error</b><br/>{error}</div>}<ResultView result={result}/></section>
    </div>
  </main>;
}
