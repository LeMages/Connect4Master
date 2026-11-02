import { useId, useRef, useState, type CSSProperties, type KeyboardEvent } from 'react'
import { PLAYER, isValidMove, nextOpenRow, type Board as BoardState, type Cell, type Piece } from '../game'
import type { Strings } from '../i18n'

export const dropDuration = (fall: number) => 240 + fall * 60

type Props = {
  t: Strings
  board: BoardState
  lastMove?: Cell | null
  winning?: Cell[] | null
  ghost?: Piece | null
  onPlay?: (col: number) => void
}

export function Board({ t, board, lastMove, winning, ghost, onPlay }: Props) {
  const rows = board.length
  const cols = board[0].length
  const maskId = useId()
  const [hoverCol, setHoverCol] = useState<number | null>(null)
  const columnsRef = useRef<HTMLDivElement>(null)

  const previewCol = ghost && hoverCol !== null && isValidMove(board, hoverCol) ? hoverCol : null

  const focusColumn = (event: KeyboardEvent, col: number) => {
    const step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0
    if (!step) return
    event.preventDefault()
    const target = columnsRef.current?.children[(col + step + cols) % cols]
    if (target instanceof HTMLElement) target.focus()
  }

  return (
    <div className="board" style={{ '--rows': rows, '--cols': cols } as CSSProperties}>
      <div className="board-hover-row">
        {previewCol !== null && (
          <div className="slot" style={{ left: `${(previewCol / cols) * 100}%`, width: `${100 / cols}%`, height: '100%' }}>
            <div className={`token ${ghost === PLAYER ? 'player' : 'ai'}`} />
          </div>
        )}
      </div>

      <div className="board-grid">
        <div className="tokens">
          {previewCol !== null && (
            <div className="slot landing" style={slotStyle(nextOpenRow(board, previewCol), previewCol, rows, cols)}>
              <div className={`token ${ghost === PLAYER ? 'player' : 'ai'}`} />
            </div>
          )}
          {board.flatMap((cells, r) =>
            cells.map((piece, c) => {
              if (piece === 0) return null
              const isLast = lastMove?.[0] === r && lastMove[1] === c
              const isWinning = winning?.some(([y, x]) => y === r && x === c)
              const fall = rows - r
              return (
                <div
                  key={`${r}-${c}`}
                  className={`slot${isLast ? ' dropping' : ''}${isWinning ? ' winning' : ''}${winning && !isWinning ? ' dimmed' : ''}`}
                  style={{ ...slotStyle(r, c, rows, cols), '--fall': fall, '--drop-ms': `${dropDuration(fall)}ms` } as CSSProperties}
                >
                  <div className={`token ${piece === PLAYER ? 'player' : 'ai'}`} />
                </div>
              )
            }),
          )}
        </div>

        <svg className="plate" viewBox={`0 0 ${cols * 100} ${rows * 100}`} aria-hidden="true">
          <defs>
            <linearGradient id={`${maskId}-fill`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#2a3a5e" />
              <stop offset="1" stopColor="#1a2540" />
            </linearGradient>
            <mask id={maskId}>
              <rect width="100%" height="100%" fill="white" />
              {holes(rows, cols).map(([x, y]) => <circle key={`${x}-${y}`} cx={x} cy={y} r="39" fill="black" />)}
            </mask>
          </defs>
          <rect width="100%" height="100%" rx="26" fill={`url(#${maskId}-fill)`} mask={`url(#${maskId})`} />
          {holes(rows, cols).map(([x, y]) => (
            <circle key={`${x}-${y}`} cx={x} cy={y} r="39.5" fill="none" stroke="#0b1120" strokeOpacity=".7" strokeWidth="2" />
          ))}
        </svg>
      </div>

      {onPlay && (
        <div className="columns" ref={columnsRef}>
          {Array.from({ length: cols }, (_, c) => {
            const open = isValidMove(board, c)
            return (
              <button
                key={c}
                className={`column${previewCol === c ? ' active' : ''}`}
                aria-label={open ? t.column(c + 1) : t.columnFull(c + 1)}
                aria-disabled={!open || !ghost}
                onClick={() => open && onPlay(c)}
                onMouseEnter={() => setHoverCol(c)}
                onMouseLeave={() => setHoverCol(null)}
                onFocus={() => setHoverCol(c)}
                onBlur={() => setHoverCol(null)}
                onKeyDown={(event) => focusColumn(event, c)}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

const holes = (rows: number, cols: number) =>
  Array.from({ length: rows * cols }, (_, i) => [(i % cols) * 100 + 50, Math.floor(i / cols) * 100 + 50])

const slotStyle = (row: number, col: number, rows: number, cols: number): CSSProperties => ({
  left: `${(col / cols) * 100}%`,
  top: `${((rows - 1 - row) / rows) * 100}%`,
  width: `${100 / cols}%`,
  height: `${100 / rows}%`,
})
