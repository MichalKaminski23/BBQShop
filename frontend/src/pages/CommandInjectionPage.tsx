import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { api, type PingResult } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

export function CommandInjectionPage() {
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules, retry: false })
  const cmdi = modules.data?.find((module) => module.name === 'cmdi')
  const [host, setHost] = useState('127.0.0.1')
  const [pending, setPending] = useState(false)
  const [result, setResult] = useState<PingResult | null>(null)
  const [error, setError] = useState('')

  async function runDiagnostic(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPending(true)
    setError('')
    setResult(null)
    try {
      setResult(await api.ping(host))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Diagnostyka nie powiodła się.')
    } finally {
      setPending(false)
    }
  }

  return (
    <section className="card">
      <div className="page-heading">
        <div>
          <h2>Diagnostyka połączenia</h2>
          <p className="muted">Sprawdź dostępność serwera po nazwie lub adresie IP.</p>
        </div>
        {cmdi && <VariantBadge variant={cmdi.variant} />}
      </div>

      {cmdi && (
        <div className="info-box">
          <strong>Aktywny wariant: {cmdi.variant}</strong>
          <p className="muted">
            {cmdi.variant === 'secure'
              ? 'Nazwa hosta jest walidowana i przekazywana jako osobny argument procesu.'
              : 'Nazwa hosta trafia do polecenia powłoki. Spróbuj np. 127.0.0.1; echo CMDI_WORKED'}
          </p>
        </div>
      )}

      <form className="cmdi__form" onSubmit={runDiagnostic}>
        <input
          value={host}
          onChange={(event) => setHost(event.target.value)}
          placeholder="np. 127.0.0.1"
          aria-label="Adres hosta"
          maxLength={512}
          required
          spellCheck={false}
        />
        <button type="submit" disabled={pending}>
          {pending ? 'Diagnostykowanie…' : 'Sprawdź'}
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}
      {result && (
        <div>
          <p className="muted">Polecenie wykonane przez serwer:</p>
          <pre className="cmdi__command">{result.command}</pre>
          <p className="muted">Kod wyjścia: <strong>{result.exit_code}</strong></p>
          <pre className="cmdi__output">{result.output || '(brak danych)'}</pre>
        </div>
      )}
    </section>
  )
}
