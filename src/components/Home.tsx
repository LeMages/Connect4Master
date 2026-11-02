import type { Settings, Stats } from '../App'
import type { Difficulty } from '../engine'
import { AI, PLAYER, createBoard, place, type Board as BoardState, type Cell, type Piece } from '../game'
import type { Strings } from '../i18n'
import { Board } from './Board'
import { EngineStatus } from './EngineStatus'

const LEVELS: Difficulty[] = ['easy', 'medium', 'hard']

const SHOWCASE: [number, number, Piece][] = [
  [0, 2, PLAYER], [0, 3, PLAYER], [1, 3, PLAYER], [0, 4, PLAYER], [2, 4, PLAYER],
  [0, 1, AI], [1, 2, AI], [2, 3, AI], [1, 4, AI], [3, 4, AI], [0, 5, AI],
]
const SHOWCASE_LINE: Cell[] = [[0, 1], [1, 2], [2, 3], [3, 4]]

const showcaseBoard = (): BoardState =>
  SHOWCASE.reduce((board, [r, c, piece]) => place(board, r, c, piece), createBoard(6, 7))

type Props = {
  t: Strings
  settings: Settings
  stats: Stats
  onChange: (settings: Settings) => void
  onPlay: () => void
}

export function Home({ t, settings, stats, onChange, onPlay }: Props) {
  const stepper = (key: 'rows' | 'cols', label: string) => (
    <div className="stepper">
      <span>{label}</span>
      <div>
        <button
          className="ghost"
          aria-label={`${t.fewer} : ${label}`}
          onClick={() => onChange({ ...settings, [key]: Math.max(5, settings[key] - 1) })}
        >−</button>
        <output>{settings[key]}</output>
        <button
          className="ghost"
          aria-label={`${t.more} : ${label}`}
          onClick={() => onChange({ ...settings, [key]: Math.min(10, settings[key] + 1) })}
        >+</button>
      </div>
    </div>
  )

  return (
    <main className="home">
      <div className="home-copy">
        <h1>Connect4<span>Master</span></h1>
        <p className="tagline">{t.tagline}</p>

        <h2>{t.difficulty}</h2>
        <div className="levels">
          {LEVELS.map((level) => (
            <button
              key={level}
              className={`level${settings.difficulty === level ? ' selected' : ''}`}
              aria-pressed={settings.difficulty === level}
              onClick={() => onChange({ ...settings, difficulty: level })}
            >
              <strong>{t[level]}</strong>
              <span>{t[`${level}Hint`]}</span>
            </button>
          ))}
        </div>

        <h2>{t.boardSize}</h2>
        <div className="steppers">
          {stepper('rows', t.rows)}
          {stepper('cols', t.cols)}
        </div>

        <button className="primary" onClick={onPlay}>{t.play}</button>
        <EngineStatus t={t} />
      </div>

      <div className="home-side">
        <Board t={t} board={showcaseBoard()} winning={SHOWCASE_LINE} />
        <dl className="record" aria-label={t.record}>
          <div><dd>{stats.wins}</dd><dt>{t.wins}</dt></div>
          <div><dd>{stats.losses}</dd><dt>{t.losses}</dt></div>
          <div><dd>{stats.draws}</dd><dt>{t.draws}</dt></div>
        </dl>
      </div>
    </main>
  )
}
