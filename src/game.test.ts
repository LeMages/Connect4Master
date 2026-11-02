import { describe, expect, it } from 'vitest'
import { AI, PLAYER, createBoard, findWinningPieces, isFull, isValidMove, nextOpenRow, place } from './game'

describe('règles', () => {
  it('empile les jetons depuis le bas', () => {
    let board = createBoard(6, 7)
    expect(nextOpenRow(board, 3)).toBe(0)
    board = place(board, 0, 3, PLAYER)
    expect(nextOpenRow(board, 3)).toBe(1)
  })

  it('refuse une colonne pleine', () => {
    let board = createBoard(5, 5)
    for (let r = 0; r < 5; r++) board = place(board, r, 0, r % 2 ? AI : PLAYER)
    expect(isValidMove(board, 0)).toBe(false)
    expect(isValidMove(board, 1)).toBe(true)
  })

  it('détecte une grille pleine', () => {
    const board = createBoard(5, 5).map((row) => row.map(() => PLAYER))
    expect(isFull(board)).toBe(true)
  })

  it.each([
    ['horizontal', [[0, 1], [0, 2], [0, 3], [0, 4]]],
    ['vertical', [[0, 2], [1, 2], [2, 2], [3, 2]]],
    ['diagonale ascendante', [[0, 0], [1, 1], [2, 2], [3, 3]]],
    ['diagonale descendante', [[3, 1], [2, 2], [1, 3], [0, 4]]],
  ])('trouve un alignement %s', (_, cells) => {
    let board = createBoard(6, 7)
    for (const [r, c] of cells) board = place(board, r, c, AI)
    const found = findWinningPieces(board)
    expect(found?.map(String).sort()).toEqual(cells.map(String).sort())
  })

  it("ne voit pas de gagnant sans quatre jetons de la même couleur", () => {
    let board = createBoard(6, 7)
    board = place(board, 0, 0, PLAYER)
    board = place(board, 0, 1, PLAYER)
    board = place(board, 0, 2, PLAYER)
    board = place(board, 0, 3, AI)
    expect(findWinningPieces(board)).toBeNull()
  })
})
