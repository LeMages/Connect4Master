import type { CSSProperties } from 'react'
import type { Analysis } from '../engine'
import type { Strings } from '../i18n'

const WIN_SCORE = 1e14

// Les scores vont de quelques points à ±1e14 : tanh les ramène sur une échelle lisible.
const normalize = (score: number) => (Math.tanh(score / 30) + 1) / 2

function verdict(t: Strings, analysis: Analysis, best: number | undefined) {
  if (analysis.reason === 'win') return t.verdictWin
  if (analysis.reason === 'block') return t.verdictBlock
  if (best !== undefined && best >= WIN_SCORE) return t.verdictForced
  if (best !== undefined && best <= -WIN_SCORE) return t.verdictLost
  return t.verdictSearch(analysis.depth)
}

export function AiPanel({ t, analysis, cols }: { t: Strings; analysis: Analysis | null; cols: number }) {
  if (!analysis) {
    return (
      <section className="panel">
        <h2>{t.brain}</h2>
        <p className="muted">{t.brainEmpty}</p>
      </section>
    )
  }

  const best = analysis.scores[analysis.best]
  const advantage = best === undefined ? (analysis.reason === 'win' ? 1 : 0.5) : normalize(best)

  return (
    <section className="panel">
      <h2>{t.brain}</h2>
      <p className="verdict">{verdict(t, analysis, best)}</p>

      <div className="stats-row">
        <div>
          <span className="stat-value">{analysis.depth || '–'}</span>
          <span className="stat-label">{t.depth}</span>
        </div>
        <div>
          <span className="stat-value">{t.seconds(analysis.elapsed)}</span>
          <span className="stat-label">{t.time}</span>
        </div>
      </div>

      <div className="gauge" role="img" aria-label={`${t.ai} ${Math.round(advantage * 100)} %`}>
        <div className="gauge-labels">
          <span>{t.you}</span>
          <span>{t.ai}</span>
        </div>
        <div className="gauge-track">
          <div className="gauge-fill" style={{ width: `${advantage * 100}%` }} />
        </div>
      </div>

      {analysis.reason === 'search' && (
        <>
          <div className="bars" style={{ '--cols': cols } as CSSProperties} aria-label={t.scoreLegend}>
            {Array.from({ length: cols }, (_, col) => {
              const score = analysis.scores[col]
              const open = score !== undefined
              return (
                <div key={col} className={`bar-column${col === analysis.best ? ' best' : ''}`}>
                  <div className="bar-track">
                    {open && <div className="bar" style={{ height: `${Math.max(normalize(score) * 100, 4)}%` }} />}
                  </div>
                  <span>{col + 1}</span>
                </div>
              )
            })}
          </div>
          <p className="legend">{t.scoreLegend}</p>
        </>
      )}
    </section>
  )
}
