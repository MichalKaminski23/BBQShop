import { useQuery } from '@tanstack/react-query'

import { api } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

export function ModulesPage() {
  const health = useQuery({ queryKey: ['health'], queryFn: api.health, retry: false })
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules })

  return (
    <>
      <section className="card">
        <h2>Stan usług</h2>
        {health.isPending && <p className="muted">Sprawdzanie…</p>}
        {health.isError && <p className="error">API nie odpowiada.</p>}
        {health.data && (
          <ul className="status-list">
            <li>PostgreSQL: {health.data.postgres === 'ok' ? '✅' : '❌'}</li>
            <li>MongoDB: {health.data.mongo === 'ok' ? '✅' : '❌'}</li>
          </ul>
        )}
      </section>

      <section className="card">
        <h2>Moduły podatności</h2>
        <p className="muted">
          Wariant każdego modułu ustawiasz w pliku <code>.env</code> (
          <code>BBQ_MODULE_&lt;NAZWA&gt;</code>).
        </p>
        {modules.isError && <p className="error">{modules.error.message}</p>}
        <ul className="module-list">
          {modules.data?.map((module) => (
            <li key={module.name} className="module">
              <div>
                <strong>{module.title}</strong>
                <p className="muted">{module.description}</p>
              </div>
              <VariantBadge variant={module.variant} />
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}
