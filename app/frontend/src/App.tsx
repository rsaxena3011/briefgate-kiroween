import { useEffect, useState } from 'react'

type Finding = {
  finding_id: string
  type: string
  severity: 'blocker' | 'warning'
  timestamp_in_s: number
  timestamp_out_s: number | null
  frame_url: string | null
  expected: string
  observed: string
  confidence: number
  status: 'open' | 'approved' | 'dismissed'
  reviewer_note: string
}

type Run = {
  id: string
  created_at: string
  video_name: string
  duration_s: number
  status: string
  brief: { project: string }
  checks_run: string[]
  not_checked: { scope: string; reason: string }[]
  summary: {
    total: number
    blocker: number
    warning: number
    approved: number
    dismissed: number
    open: number
    scenes_matched: number
    scenes_total: number
    shots: number
    run_seconds: number
  }
  findings: Finding[]
}

const SEV = { blocker: 'BLOCKER', warning: 'WARNING' } as const

function fmtT(s: number) {
  const m = Math.floor(s / 60)
  const sec = (s % 60).toFixed(1).padStart(4, '0')
  return `${m}:${sec}`
}

export default function App() {
  const [run, setRun] = useState<Run | null>(null)
  const [runs, setRuns] = useState<{ id: string; video_name: string; status: string; created_at: string }[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [video, setVideo] = useState<File | null>(null)
  const [brief, setBrief] = useState<File | null>(null)
  const [logo, setLogo] = useState<File | null>(null)

  const loadRuns = () =>
    fetch('/api/runs')
      .then((r) => r.json())
      .then(setRuns)
      .catch(() => undefined)

  useEffect(() => {
    loadRuns()
  }, [])

  const sel = run?.findings.find((f) => f.finding_id === selected) ?? run?.findings[0]

  async function startRun(e: React.FormEvent) {
    e.preventDefault()
    if (!video || !brief || !logo) {
      setError('Attach all three: video, brief JSON, approved logo PNG.')
      return
    }
    setBusy(true)
    setError('')
    const fd = new FormData()
    fd.append('video', video)
    fd.append('brief', brief)
    fd.append('logo', logo)
    try {
      const r = await fetch('/api/runs', { method: 'POST', body: fd })
      if (!r.ok) throw new Error(await r.text())
      const data: Run = await r.json()
      setRun(data)
      setSelected(data.findings[0]?.finding_id ?? null)
      setNote('')
      loadRuns()
    } catch (err) {
      setError(String(err))
    } finally {
      setBusy(false)
    }
  }

  async function decide(status: 'approved' | 'dismissed') {
    if (!run || !sel) return
    setBusy(true)
    const r = await fetch(`/api/runs/${run.id}/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ finding_id: sel.finding_id, status, note }),
    })
    if (r.ok) {
      const data: Run = await r.json()
      setRun(data)
      setNote('')
    } else {
      setError(await r.text())
    }
    setBusy(false)
  }

  async function openRun(id: string) {
    const r = await fetch(`/api/runs/${id}`)
    if (r.ok) {
      const data: Run = await r.json()
      setRun(data)
      setSelected(data.findings[0]?.finding_id ?? null)
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>BriefGate</h1>
          <p className="tag">The brief is the truth. The video has to prove it.</p>
        </div>
        <div className="hdr-right">brief-vs-final QC gate · v1</div>
      </header>

      <section className="upload panel">
        <h2>1 · Start a run</h2>
        <form onSubmit={startRun}>
          <label>
            Client video (.mp4/.mov, ≤3 min, ≤500 MB)
            <input type="file" accept=".mp4,.mov" onChange={(e) => setVideo(e.target.files?.[0] ?? null)} />
          </label>
          <label>
            Brief (JSON — project, scenes, brand, technical)
            <input type="file" accept=".json" onChange={(e) => setBrief(e.target.files?.[0] ?? null)} />
          </label>
          <label>
            Approved logo (PNG)
            <input type="file" accept=".png" onChange={(e) => setLogo(e.target.files?.[0] ?? null)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Running the gate…' : 'Run the gate'}
          </button>
        </form>
        <p className="hint">
          Try it with the sample pack in the repo: <code>sample-pack/sample_video.mp4</code> +{' '}
          <code>sample-pack/brief.json</code> + <code>sample-pack/approved_logo.png</code> — planted wrong
          logo at 0:42, one missing scene, one 3-second black segment.
        </p>
        {error && <p className="error">{error}</p>}
      </section>

      {run && (
        <>
          <section className="summary panel">
            <h2>
              {run.brief.project} — {run.video_name}
            </h2>
            <p>
              Run {run.id} · {run.duration_s.toFixed(1)}s · {run.summary.shots} shots ·{' '}
              {run.summary.scenes_matched}/{run.summary.scenes_total} scenes matched · ran in{' '}
              {run.summary.run_seconds}s · checks: {run.checks_run.join(', ')}
            </p>
            <p>
              <strong>{run.summary.total} findings</strong> — {run.summary.blocker} blocker,{' '}
              {run.summary.warning} warning · {run.summary.approved} approved, {run.summary.dismissed}{' '}
              dismissed, {run.summary.open} open
            </p>
            {run.not_checked.map((n) => (
              <p key={n.scope} className="notchecked">
                Not checked: {n.scope} — {n.reason}
              </p>
            ))}
            <div className="exports">
              <a href={`/api/runs/${run.id}/report.pdf`}>Export PDF</a>
              <a href={`/api/runs/${run.id}/report.json`}>Export JSON</a>
            </div>
          </section>

          <div className="review">
            <section className="findings panel">
              <h2>2 · Findings</h2>
              {run.findings.length === 0 && <p>No findings. The video passed every check that could be verified.</p>}
              <ul>
                {run.findings.map((f) => (
                  <li
                    key={f.finding_id}
                    className={sel?.finding_id === f.finding_id ? 'active' : ''}
                    onClick={() => {
                      setSelected(f.finding_id)
                      setNote(f.reviewer_note || '')
                    }}
                  >
                    <span className={`sev ${f.severity}`}>{SEV[f.severity]}</span>
                    <span className="ts">{fmtT(f.timestamp_in_s)}</span>
                    <span className="ftype">{f.type}</span>
                    <span className="fstatus">{f.status}</span>
                    <span className="fobs">{f.observed}</span>
                  </li>
                ))}
              </ul>
            </section>

            {sel && (
              <section className="evidence panel">
                <h2>3 · Evidence — {sel.finding_id}</h2>
                {sel.frame_url ? (
                  <img src={sel.frame_url} alt={`Frame at ${fmtT(sel.timestamp_in_s)} from the submitted video`} />
                ) : (
                  <p>No frame available for this finding.</p>
                )}
                <dl>
                  <dt>Timestamp</dt>
                  <dd>
                    {fmtT(sel.timestamp_in_s)}
                    {sel.timestamp_out_s !== null ? ` – ${fmtT(sel.timestamp_out_s)}` : ''}
                  </dd>
                  <dt>Expected (from the brief)</dt>
                  <dd>{sel.expected}</dd>
                  <dt>Observed</dt>
                  <dd>{sel.observed}</dd>
                  <dt>Confidence</dt>
                  <dd>{sel.confidence.toFixed(2)}</dd>
                  <dt>Status</dt>
                  <dd>{sel.status}</dd>
                </dl>
                <label>
                  Reviewer note
                  <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Optional note…" />
                </label>
                <div className="actions">
                  <button className="approve" disabled={busy} onClick={() => decide('approved')}>
                    Approve — real defect
                  </button>
                  <button className="dismiss" disabled={busy} onClick={() => decide('dismissed')}>
                    Dismiss — false alarm
                  </button>
                </div>
              </section>
            )}
          </div>
        </>
      )}

      {runs.length > 0 && (
        <section className="history panel">
          <h2>Previous runs</h2>
          <ul>
            {runs.map((r) => (
              <li key={r.id} onClick={() => openRun(r.id)}>
                {r.id} · {r.video_name} · {r.status} · {r.created_at}
              </li>
            ))}
          </ul>
        </section>
      )}

      <footer>
        BriefGate v1 — the gate reports; it never modifies the deliverable. Every finding carries a frame
        extracted from the submitted video, or the check reports not-checked.
      </footer>
    </div>
  )
}
