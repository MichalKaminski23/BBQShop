import { useQuery } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { api, ApiError } from '../api/client'

const priceFormat = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' })

export function ShopPage() {
  const [input, setInput] = useState('')
  const [query, setQuery] = useState('')
  const products = useQuery({
    queryKey: ['products', query],
    queryFn: () => api.searchProducts(query),
    retry: false,
  })

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setQuery(input)
  }

  const moduleOff = products.error instanceof ApiError && products.error.status === 404

  return (
    <section className="card">
      <h2>Sklep</h2>
      <form className="search" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Szukaj produktu, np. grill"
          aria-label="Szukaj produktu"
        />
        <button type="submit">Szukaj</button>
      </form>

      {products.isPending && <p className="muted">Ładowanie…</p>}
      {moduleOff && <p className="muted">Moduł SQLi jest wyłączony (BBQ_MODULE_SQLI=off).</p>}
      {products.isError && !moduleOff && <p className="error">{products.error.message}</p>}
      {products.data?.length === 0 && <p className="muted">Brak wyników.</p>}

      <ul className="product-grid">
        {products.data?.map((product) => (
          <li key={`${product.id}-${product.name}`} className="product">
            <span className="product__category">{product.category}</span>
            <strong>{product.name}</strong>
            <p className="muted">{product.description}</p>
            <span className="product__price">{priceFormat.format(Number(product.price))}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
