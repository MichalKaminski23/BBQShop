import { useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'

import { api, ApiError, type ResourceDemoResult } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

type ResourceType = 'file' | 'socket'

interface DemoRequest {
  resourceType: ResourceType
  count: number
}

export function FdLeakPage() {
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules, retry: false })
  const fdleak = modules.data?.find((module) => module.name === 'fdleak')
  const [count, setCount] = useState('5')
  const demo = useMutation<ResourceDemoResult, Error, DemoRequest>({
    mutationFn: ({ resourceType, count: requestedCount }) =>
      resourceType === 'file'
        ? api.openFdleakFiles(requestedCount)
        : api.openFdleakSockets(requestedCount),
  })

  const moduleOff = demo.error instanceof ApiError && demo.error.status === 404

  return (
    <section className="card">
      <div className="page-heading">
        <div>
          <h2>Deskryptory plików i gniazd</h2>
          <p className="muted">
            Porównaj liczbę otwartych zasobów z tymi, które wariant poprawiony zamyka.
          </p>
        </div>
        {fdleak && <VariantBadge variant={fdleak.variant} />}
      </div>

      {modules.isError && <p className="error">{modules.error.message}</p>}
      {fdleak && (
        <div className="info-box">
          <strong>Aktywny wariant: {fdleak.variant}</strong>
          <p className="muted">
            {fdleak.variant === 'secure'
              ? 'Pliki i gniazda są zamykane po zakończeniu każdej operacji.'
              : 'Uchwyty pozostają otwarte w procesie API. Zrestartuj API po demonstracji, aby je zwolnić.'}
          </p>
        </div>
      )}

      <div className="login-form">
        <label>
          Liczba zasobów (1–100)
          <input
            type="number"
            min="1"
            max="100"
            value={count}
            onChange={(event) => setCount(event.target.value)}
          />
        </label>
        <div className="form-actions">
          <button
            type="button"
            disabled={demo.isPending}
            onClick={() => demo.mutate({ resourceType: 'file', count: Number(count) })}
          >
            Otwórz pliki
          </button>
          <button
            type="button"
            className="button-secondary"
            disabled={demo.isPending}
            onClick={() => demo.mutate({ resourceType: 'socket', count: Number(count) })}
          >
            Otwórz gniazda
          </button>
        </div>
      </div>

      {moduleOff && <p className="muted">Moduł fdleak jest wyłączony.</p>}
      {demo.isError && !moduleOff && <p className="error">{demo.error.message}</p>}
      {demo.data && (
        <div className="result-box">
          <strong>
            Wynik dla {demo.data.resource_type === 'file' ? 'plików' : 'gniazd'}
          </strong>
          <p className="muted">
            Otwarto: <code>{demo.data.opened_count}</code>; zamknięto:{' '}
            <code>{demo.data.closed_count}</code>
          </p>
          <p>
            Pozostawione otwarte w tym procesie:{' '}
            <strong>{demo.data.outstanding_count}</strong>
          </p>
        </div>
      )}

      <p className="muted">
        Używaj demonstracji wyłącznie lokalnie. Każde żądanie może otworzyć maksymalnie 100 zasobów.
      </p>
    </section>
  )
}
