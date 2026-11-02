import type { Board } from './game'
import type { ThinkRequest, WorkerMessage } from './engine.worker'

export type EngineStatus = 'loading' | 'ready' | 'error'
export type Difficulty = 'easy' | 'medium' | 'hard'

export type Analysis = {
  depth: number
  scores: Record<string, number>
  best: number
  reason: 'win' | 'block' | 'search'
  elapsed: number
}

export const DIFFICULTY: Record<Difficulty, { maxTime: number; maxDepth: number | null }> = {
  easy: { maxTime: 3, maxDepth: 2 },
  medium: { maxTime: 3, maxDepth: 4 },
  hard: { maxTime: 4, maxDepth: null },
}

type Pending = { resolve: (col: number) => void; onProgress: (analysis: Analysis) => void }

// Le worker exécute IA_Decision d'un bloc : un calcul lancé ne peut pas être interrompu.
// Une partie abandonnée ignore simplement sa réponse, et le moteur reste chargé.
class Engine {
  status: EngineStatus = 'loading'
  private worker!: Worker
  private listeners = new Set<() => void>()
  private pending = new Map<number, Pending>()
  private nextId = 0

  constructor() {
    this.start()
  }

  private start() {
    this.worker = new Worker(new URL('./engine.worker.ts', import.meta.url), { type: 'module' })
    this.worker.onmessage = ({ data }: MessageEvent<WorkerMessage>) => this.receive(data)
    this.worker.onerror = () => this.setStatus('error')
  }

  private receive(message: WorkerMessage) {
    if (message.type === 'ready') this.setStatus('ready')
    else if (message.type === 'failed') this.setStatus('error')
    else if (message.type === 'progress') this.pending.get(message.id)?.onProgress(JSON.parse(message.json))
    else {
      this.pending.get(message.id)?.resolve(message.col)
      this.pending.delete(message.id)
    }
  }

  private setStatus(status: EngineStatus) {
    this.status = status
    this.listeners.forEach((listener) => listener())
  }

  subscribe = (listener: () => void) => {
    this.listeners.add(listener)
    return () => void this.listeners.delete(listener)
  }

  getStatus = () => this.status

  retry() {
    this.worker.terminate()
    this.setStatus('loading')
    this.start()
    // Les demandes en attente sont rejouées par la partie, qui observe le statut.
    this.pending.clear()
  }

  think(board: Board, difficulty: Difficulty, onProgress: Pending['onProgress']) {
    const id = this.nextId++
    const request: ThinkRequest = { id, board, ...DIFFICULTY[difficulty] }
    this.worker.postMessage(request)
    return new Promise<number>((resolve) => this.pending.set(id, { resolve, onProgress }))
  }
}

export const engine = new Engine()
