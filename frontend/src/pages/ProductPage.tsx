import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router'

import { api, ApiError, productImages } from '../api/client'

const priceFormat = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' })

export function ProductPage() {
  const { productId } = useParams()
  const id = Number(productId)
  const product = useQuery({
    queryKey: ['product', id],
    queryFn: async () => {
      const products = await api.searchProducts('')
      return products.find((item) => item.id === id) ?? null
    },
    enabled: Number.isInteger(id) && id > 0,
    retry: false,
  })

  const moduleOff = product.error instanceof ApiError && product.error.status === 404

  if (!Number.isInteger(id) || id < 1) {
    return <p className="error">Nieprawidłowy identyfikator produktu.</p>
  }

  return (
    <section className="card">
      <Link to="/shop" className="back-link">
        ← Wróć do sklepu
      </Link>
      {product.isPending && <p className="muted">Ładowanie produktu…</p>}
      {moduleOff && <p className="muted">Moduł SQLi jest wyłączony.</p>}
      {product.isError && !moduleOff && <p className="error">{product.error.message}</p>}
      {product.data === null && <p className="error">Nie znaleziono produktu.</p>}
      {product.data && (
        <article className="product-detail">
          <img
            className="product-detail__image"
            src={`/api/files?path=${productImages[product.data.id]}`}
            alt={product.data.name}
          />
          <div>
            <span className="product__category">{product.data.category}</span>
            <h2>{product.data.name}</h2>
            <p>{product.data.description}</p>
            <strong className="product-detail__price">
              {priceFormat.format(Number(product.data.price))}
            </strong>
          </div>
        </article>
      )}
    </section>
  )
}
