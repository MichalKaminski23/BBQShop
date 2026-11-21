import { useQuery } from '@tanstack/react-query'
import { useState, type ChangeEvent, type FormEvent } from 'react'

import { api } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

function manualName(productId: number): string {
  return `manual-${productId}.txt`
}

function looksLikeEscape(name: string): boolean {
  return name.includes('..') || name.includes('/') || name.includes('\\')
}

type Status = { kind: 'ok' | 'error' | 'leak'; text: string }

export function FilesPage() {
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules, retry: false })
  const fileio = modules.data?.find((module) => module.name === 'fileio')
  const products = useQuery({
    queryKey: ['products', ''],
    queryFn: () => api.searchProducts(''),
    retry: false,
  })

  const [fileName, setFileName] = useState('manual-1.txt')
  const [content, setContent] = useState('')
  const [status, setStatus] = useState<Status | null>(null)

  async function read(name: string): Promise<void> {
    setStatus(null)
    try {
      const file = await api.readFile(name)
      setContent(file.content)
      if (file.content.includes('FLAG{') || looksLikeEscape(name)) {
        setStatus({ kind: 'leak', text: `Odczytano plik spoza instrukcji: ${name}` })
      } else {
        setStatus({ kind: 'ok', text: `Wczytano instrukcję: ${file.name}` })
      }
    } catch (error) {
      setStatus({ kind: 'error', text: error instanceof Error ? error.message : 'Błąd odczytu.' })
    }
  }

  async function save(): Promise<void> {
    setStatus(null)
    try {
      const result = await api.writeFile(fileName, content)
      const kind = looksLikeEscape(fileName) ? 'leak' : 'ok'
      const text = looksLikeEscape(fileName)
        ? `Zapisano plik poza katalogiem instrukcji: ${result.name}`
        : `Zapisano instrukcję: ${result.name} (${result.written} znaków)`
      setStatus({ kind, text })
    } catch (error) {
      setStatus({ kind: 'error', text: error instanceof Error ? error.message : 'Błąd zapisu.' })
    }
  }

  function handleSelect(event: ChangeEvent<HTMLSelectElement>): void {
    const id = Number(event.target.value)
    if (id > 0) {
      const name = manualName(id)
      setFileName(name)
      void read(name)
    }
  }

  function handleRead(event: FormEvent): void {
    event.preventDefault()
    void read(fileName)
  }

  return (
    <section className="card files">
      <div className="page-heading">
        <div>
          <h2>Instrukcje produktów</h2>
          <p className="muted">
            Wybierz produkt, aby wczytać jego instrukcję, albo wpisz nazwę pliku ręcznie.
          </p>
        </div>
        {fileio && <VariantBadge variant={fileio.variant} />}
      </div>

      {fileio && (
        <div className="info-box">
          <strong>Aktywny wariant: {fileio.variant}</strong>
          <p className="muted">
            {fileio.variant === 'secure'
              ? 'Nazwa jest zawężona do katalogu instrukcji – ucieczka poza niego jest odrzucana.'
              : 'Nazwa pliku trafia wprost do ścieżki – spróbuj ../secret.txt albo /etc/hostname.'}
          </p>
        </div>
      )}

      <form className="files__controls" onSubmit={handleRead}>
        <label className="files__field">
          Produkt
          <select onChange={handleSelect} defaultValue="">
            <option value="" disabled>
              — wybierz produkt —
            </option>
            {products.data?.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
        </label>
        <label className="files__field">
          Plik instrukcji
          <input
            value={fileName}
            onChange={(event) => setFileName(event.target.value)}
            spellCheck={false}
            required
          />
        </label>
        <button type="submit">Wczytaj</button>
      </form>

      <textarea
        className="files__editor"
        value={content}
        onChange={(event) => setContent(event.target.value)}
        rows={8}
        placeholder="Treść instrukcji pojawi się tutaj po wczytaniu."
        spellCheck={false}
      />
      <div className="form-actions">
        <button type="button" onClick={() => void save()}>
          Zapisz instrukcję
        </button>
      </div>

      {status && (
        <p className={status.kind === 'leak' ? 'files__leak' : status.kind === 'error' ? 'error' : 'ok'}>
          {status.kind === 'leak' && '⚠ '}
          {status.text}
        </p>
      )}
    </section>
  )
}
