import { useEffect, useState } from 'react'
import type { Difficulty } from './engine'
import { Game } from './components/Game'
import { Home } from './components/Home'
import { STRINGS, type Lang } from './i18n'
import { load, save } from './storage'

export type Settings = { difficulty: Difficulty; rows: number; cols: number; lang: Lang }
export type Stats = { wins: number; losses: number; draws: number }

const browserLang: Lang = navigator.language.startsWith('fr') ? 'fr' : 'en'

export function App() {
  const [settings, setSettings] = useState<Settings>(() =>
    load('c4m-settings', { difficulty: 'medium', rows: 6, cols: 7, lang: browserLang }),
  )
  const [stats, setStats] = useState<Stats>(() => load('c4m-stats', { wins: 0, losses: 0, draws: 0 }))
  const [gameId, setGameId] = useState<number | null>(null)

  useEffect(() => save('c4m-settings', settings), [settings])
  useEffect(() => save('c4m-stats', stats), [stats])
  useEffect(() => void (document.documentElement.lang = settings.lang), [settings.lang])

  const t = STRINGS[settings.lang]
  const toggleLang = () => setSettings((s) => ({ ...s, lang: s.lang === 'fr' ? 'en' : 'fr' }))

  return (
    <div className="app">
      <header className="topbar">
        <button className="brand" onClick={() => setGameId(null)} aria-label={t.menu}>
          <span className="brand-mark" aria-hidden="true">
            <i /><i /><i /><i />
          </span>
          Connect4Master
        </button>
        <button className="ghost lang" onClick={toggleLang}>
          {settings.lang === 'fr' ? 'EN' : 'FR'}
        </button>
      </header>

      {gameId === null ? (
        <Home t={t} settings={settings} stats={stats} onChange={setSettings} onPlay={() => setGameId(Date.now())} />
      ) : (
        <Game
          key={gameId}
          t={t}
          settings={settings}
          stats={stats}
          onFinish={(result) => setStats((s) => ({ ...s, [result]: s[result] + 1 }))}
          onReplay={() => setGameId(Date.now())}
          onMenu={() => setGameId(null)}
        />
      )}
    </div>
  )
}
