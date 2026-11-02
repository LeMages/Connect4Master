import { useSyncExternalStore } from 'react'
import { engine } from '../engine'
import type { Strings } from '../i18n'

export function useEngineStatus() {
  return useSyncExternalStore(engine.subscribe, engine.getStatus)
}

export function EngineStatus({ t }: { t: Strings }) {
  const status = useEngineStatus()

  if (status === 'ready') {
    return (
      <p className="engine ready">
        <span className="dot" aria-hidden="true" />
        {t.engineReady}
      </p>
    )
  }

  if (status === 'error') {
    return (
      <div className="engine error" role="alert">
        <p>{t.engineError}</p>
        <button className="ghost" onClick={() => engine.retry()}>{t.retry}</button>
      </div>
    )
  }

  return (
    <div className="engine loading" role="status">
      <p><span className="dot" aria-hidden="true" />{t.engineLoading}</p>
      <p className="muted">{t.engineLoadingHint}</p>
      <div className="loader" aria-hidden="true" />
    </div>
  )
}
