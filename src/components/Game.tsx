import { useCallback, useEffect, useRef, useState } from 'react'
import type { Settings, Stats } from '../App'
import { engine, type Analysis } from '../engine'
import {
  AI,
  PLAYER,
  createBoard,
  findWinningPieces,
  isFull,
  isValidMove,
  nextOpenRow,
  place,
  type Cell,
  type Piece,
} from '../game'
import type { Strings } from '../i18n'
import { AiPanel } from './AiPanel'
import { Board, dropDuration } from './Board'
import { EngineStatus, useEngineStatus } from './EngineStatus'

const MIN_THINK_MS = 500

type Props = {
  t: Strings
  settings: Settings
  stats: Stats
  onFinish: (result: keyof Stats) => void
  onReplay: () => void
  onMenu: () => void
}

export function Game({ t, settings, stats, onFinish, onReplay, onMenu }: Props) {
  const [board, setBoard] = useState(() => createBoard(settings.rows, settings.cols))
  const [turn, setTurn] = useState<Piece>(() => (Math.random() < 0.5 ? PLAYER : AI))
  const [lastMove, setLastMove] = useState<Cell | null>(null)
  const [winning, setWinning] = useState<Cell[] | null>(null)
  const [isDraw, setIsDraw] = useState(false)
  const [dropping, setDropping] = useState(false)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const engineStatus = useEngineStatus()
  const dropTimer = useRef(0)

  const over = winning !== null || isDraw

  const play = useCallback((col: number, piece: Piece) => {
    const row = nextOpenRow(board, col)
    const next = place(board, row, col, piece)
    setBoard(next)
    setLastMove([row, col])
    setDropping(true)

    dropTimer.current = window.setTimeout(() => {
      setDropping(false)
      const line = findWinningPieces(next)
      if (line) {
        setWinning(line)
        onFinish(piece === PLAYER ? 'wins' : 'losses')
      } else if (isFull(next)) {
        setIsDraw(true)
        onFinish('draws')
      } else {
        setTurn(piece === PLAYER ? AI : PLAYER)
      }
    }, dropDuration(settings.rows - row))
  }, [board, onFinish, settings.rows])

  useEffect(() => () => clearTimeout(dropTimer.current), [])

  useEffect(() => {
    if (turn !== AI || over || dropping || engineStatus === 'error') return

    let cancelled = false
    // Le délai évite un calcul inutile si l'effet est annulé tout de suite.
    const timer = window.setTimeout(async () => {
      const started = performance.now()
      const col = await engine.think(board, settings.difficulty, (update) => {
        if (!cancelled) setAnalysis(update)
      })
      const remaining = MIN_THINK_MS - (performance.now() - started)
      if (remaining > 0) await new Promise((resolve) => setTimeout(resolve, remaining))
      if (!cancelled) play(col, AI)
    }, 50)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [turn, over, dropping, engineStatus, board, settings.difficulty, play])

  const canPlay = turn === PLAYER && !over && !dropping
  const handlePlay = (col: number) => {
    if (canPlay && isValidMove(board, col)) play(col, PLAYER)
  }

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onMenu()
      const col = Number(event.key) - 1
      if (col >= 0 && col < settings.cols) handlePlay(col)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })

  const winner = winning ? board[winning[0][0]][winning[0][1]] : null
  const title = winner === PLAYER ? t.youWon
    : winner === AI ? t.aiWon
    : isDraw ? t.draw
    : turn === PLAYER ? t.yourTurn : t.aiTurn
  const tone = over ? (winner === PLAYER ? 'player' : winner === AI ? 'ai' : 'neutral') : turn === PLAYER ? 'player' : 'ai'

  return (
    <main className="game">
      <Board
        t={t}
        board={board}
        lastMove={lastMove}
        winning={winning}
        ghost={canPlay ? PLAYER : null}
        onPlay={handlePlay}
      />

      <aside className="side">
        <section className={`status ${tone}${!over && turn === AI ? ' thinking' : ''}`} aria-live="polite">
          <span className={`status-token token ${tone}`} aria-hidden="true" />
          <h1>{title}</h1>
          {over && <button className="primary" onClick={onReplay}>{t.playAgain}</button>}
        </section>

        {engineStatus !== 'ready' && <EngineStatus t={t} />}

        <AiPanel t={t} analysis={analysis} cols={settings.cols} />

        <div className="side-footer">
          <p className="muted">{t[settings.difficulty]} · {stats.wins} – {stats.losses} – {stats.draws}</p>
          <button className="ghost" onClick={onMenu}>{t.menu}</button>
        </div>
        <p className="credit">{t.engineCredit}</p>
      </aside>
    </main>
  )
}
