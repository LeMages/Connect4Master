/// <reference lib="webworker" />
import iaSource from '../ia.py?raw'
import type { Board } from './game'

const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/'

export type ThinkRequest = { id: number; board: Board; maxTime: number; maxDepth: number | null }

export type WorkerMessage =
  | { type: 'ready' }
  | { type: 'failed' }
  | { type: 'progress'; id: number; json: string }
  | { type: 'done'; id: number; col: number }

interface PyProxy {
  destroy(): void
}

interface Pyodide {
  loadPackage(name: string): Promise<unknown>
  FS: { writeFile(path: string, data: string): void }
  pyimport(name: string): {
    IA_Decision: {
      callKwargs(board: PyProxy, maxTime: number, kwargs: Record<string, unknown>): number
    }
  }
  toPy(value: unknown): PyProxy
}

const post = (message: WorkerMessage) => self.postMessage(message)

async function boot() {
  const { loadPyodide } = await import(/* @vite-ignore */ `${PYODIDE_URL}pyodide.mjs`)
  const pyodide: Pyodide = await loadPyodide({ indexURL: PYODIDE_URL })
  await pyodide.loadPackage('numpy')
  pyodide.FS.writeFile('ia.py', iaSource)
  return { pyodide, ia: pyodide.pyimport('ia') }
}

const engine = boot()

engine.then(
  () => post({ type: 'ready' }),
  () => post({ type: 'failed' }),
)

self.onmessage = async ({ data }: MessageEvent<ThinkRequest>) => {
  try {
    const { pyodide, ia } = await engine
    const board = pyodide.toPy(data.board)
    const col = ia.IA_Decision.callKwargs(board, data.maxTime, {
      // Un null JavaScript ne devient pas None : on omet l'argument.
      ...(data.maxDepth !== null && { max_depth: data.maxDepth }),
      on_progress: (json: string) => post({ type: 'progress', id: data.id, json }),
    })
    board.destroy()
    post({ type: 'done', id: data.id, col })
  } catch (error) {
    console.error(error)
    post({ type: 'failed' })
  }
}
