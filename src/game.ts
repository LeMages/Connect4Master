// Règles côté interface, pour que le coup du joueur reste instantané.
// Même convention que ia.py : la rangée 0 est en bas.

export const PLAYER = 1
export const AI = -1

export type Piece = typeof PLAYER | typeof AI
export type Board = number[][]
export type Cell = readonly [row: number, col: number]

export const createBoard = (rows: number, cols: number): Board =>
  Array.from({ length: rows }, () => Array<number>(cols).fill(0))

export const isValidMove = (board: Board, col: number) => board[board.length - 1][col] === 0

export const nextOpenRow = (board: Board, col: number) => board.findIndex((row) => row[col] === 0)

export const isFull = (board: Board) => board[board.length - 1].every((cell) => cell !== 0)

export const place = (board: Board, row: number, col: number, piece: Piece): Board =>
  board.map((cells, r) => (r === row ? cells.map((cell, c) => (c === col ? piece : cell)) : cells))

const DIRECTIONS = [
  [0, 1],
  [1, 0],
  [1, 1],
  [-1, 1],
] as const

/** Retourne les quatre cases alignées, ou null s'il n'y a pas de gagnant. */
export function findWinningPieces(board: Board): Cell[] | null {
  for (let r = 0; r < board.length; r++) {
    for (let c = 0; c < board[0].length; c++) {
      const piece = board[r][c]
      if (piece === 0) continue
      for (const [dr, dc] of DIRECTIONS) {
        const line: Cell[] = [0, 1, 2, 3].map((i) => [r + dr * i, c + dc * i])
        if (line.every(([y, x]) => board[y]?.[x] === piece)) return line
      }
    }
  }
  return null
}
