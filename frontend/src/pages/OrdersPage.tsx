import { useQuery } from '@tanstack/react-query'

import { api, ApiError } from '../api/client'
import { VariantBadge } from '../components/VariantBadge'

const priceFormat = new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' })
const dateFormat = new Intl.DateTimeFormat('pl-PL', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function OrdersPage() {
  const orders = useQuery({ queryKey: ['orders'], queryFn: api.orders, retry: false })
  const modules = useQuery({ queryKey: ['modules'], queryFn: api.modules, retry: false })
  const nplusone = modules.data?.find((module) => module.name === 'nplusone')
  const moduleOff = orders.error instanceof ApiError && orders.error.status === 404
  const orderData = orders.data?.orders
  const metrics = orders.data?.metrics
  const expectedQueries =
    nplusone?.variant === 'vulnerable' ? `1 + ${orderData?.length ?? 'N'}` : '2'

  return (
    <section className="card">
      <div className="page-heading">
        <div>
          <h2>Zamówienia</h2>
          <p className="muted">
            Lista zamówień z pozycjami — przykład problemu N+1.
          </p>
        </div>
        {nplusone && <VariantBadge variant={nplusone.variant} />}
      </div>

      {nplusone && (
        <div className="info-box">
          <strong>Aktywny wariant: {nplusone.variant}</strong>
          <p className="muted">
            Oczekiwana liczba zapytań SQL dla tego widoku: <code>{expectedQueries}</code>.
            Szczegóły zobaczysz w logach API przy włączonym logowaniu SQL.
          </p>
          {metrics && metrics.count !== null && metrics.timeMs !== null && (
            <p className="muted">
              Ten request: <code>{metrics.count} zapytań</code> w{' '}
              <code>{metrics.timeMs.toFixed(2)} ms</code>.
            </p>
          )}
        </div>
      )}

      {orders.isPending && <p className="muted">Ładowanie zamówień…</p>}
      {moduleOff && (
        <p className="muted">Moduł N+1 jest wyłączony (BBQ_MODULE_NPLUSONE=off).</p>
      )}
      {orders.isError && !moduleOff && <p className="error">{orders.error.message}</p>}

      {orderData && orderData.length === 0 && (
        <p className="muted">Brak zamówień.</p>
      )}

      <ul className="order-list">
        {orderData?.map((order) => (
          <li key={order.id} className="order">
            <div className="order__header">
              <div>
                <strong>Zamówienie #{order.id}</strong>
                <p className="muted">{order.customer_name}</p>
              </div>
              <time dateTime={order.created_at}>{dateFormat.format(new Date(order.created_at))}</time>
            </div>
            <ul className="order__items">
              {order.items.map((item) => (
                <li key={item.id}>
                  <span>Produkt #{item.product_id}</span>
                  <span>
                    {item.quantity} × {priceFormat.format(Number(item.unit_price))}
                  </span>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </section>
  )
}
