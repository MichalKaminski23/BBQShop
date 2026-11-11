import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { api, ApiError, type CreateOrderResult } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

function newIdempotencyKey(): string {
  return crypto.randomUUID()
}

export function ConcurrencyPage() {
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules, retry: false })
  const concurrency = modules.data?.find((module) => module.name === 'concurrency')
  const [customerName, setCustomerName] = useState('Test frontend')
  const [productId, setProductId] = useState('1')
  const [quantity, setQuantity] = useState('1')
  const [idempotencyKey, setIdempotencyKey] = useState(newIdempotencyKey)
  const [result, setResult] = useState<CreateOrderResult | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setResult(null)
    setIsSubmitting(true)

    try {
      const order = await api.createOrder(
        {
          customer_name: customerName,
          items: [{ product_id: Number(productId), quantity: Number(quantity) }],
        },
        idempotencyKey,
      )
      setResult(order)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError
          : new Error('Nie udało się złożyć zamówienia.'),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const moduleOff = error instanceof ApiError && error.status === 404

  return (
    <section className="card">
      <div className="page-heading">
        <div>
          <h2>Wielokrotne wykonanie</h2>
          <p className="muted">
            Wyślij to samo zamówienie ponownie i zobacz działanie Idempotency-Key.
          </p>
        </div>
        {concurrency && <VariantBadge variant={concurrency.variant} />}
      </div>

      {concurrency && (
        <div className="info-box">
          <strong>Aktywny wariant: {concurrency.variant}</strong>
          <p className="muted">
            {concurrency.variant === 'secure'
              ? 'Ten sam klucz zwróci istniejące zamówienie zamiast tworzyć kolejne.'
              : 'Ten sam klucz jest ignorowany, więc każde żądanie utworzy nowe zamówienie.'}
          </p>
        </div>
      )}

      <form className="login-form" onSubmit={handleSubmit}>
        <label>
          Klient
          <input
            value={customerName}
            onChange={(event) => setCustomerName(event.target.value)}
            required
          />
        </label>
        <label>
          ID produktu
          <input
            type="number"
            min="1"
            value={productId}
            onChange={(event) => setProductId(event.target.value)}
            required
          />
        </label>
        <label>
          Ilość
          <input
            type="number"
            min="1"
            max="100"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            required
          />
        </label>
        <label>
          Idempotency-Key
          <input
            value={idempotencyKey}
            onChange={(event) => setIdempotencyKey(event.target.value)}
            maxLength={64}
            required
          />
        </label>
        <div className="form-actions">
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Wysyłanie…' : 'Złóż zamówienie'}
          </button>
          <button type="button" className="button-secondary" onClick={() => setIdempotencyKey(newIdempotencyKey())}>
            Nowy klucz
          </button>
        </div>
      </form>

      {moduleOff && <p className="muted">Moduł jest wyłączony.</p>}
      {error && !moduleOff && <p className="error">{error.message}</p>}
      {result && (
        <div className={`result-box ${result.created ? 'result-box--created' : 'result-box--reused'}`}>
          <strong>{result.created ? 'Utworzono nowe zamówienie' : 'Zwrócono istniejące zamówienie'}</strong>
          <p className="muted">
            ID zamówienia: <code>#{result.order.id}</code>
          </p>
          <p className="muted">
            Pole <code>created</code>: <code>{String(result.created)}</code>
          </p>
        </div>
      )}
    </section>
  )
}
