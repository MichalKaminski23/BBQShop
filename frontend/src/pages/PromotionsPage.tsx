import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '../api/client'
import './PromotionsPage.css'

type Variant = 'vulnerable' | 'secure' | 'off' | 'unknown'

export function PromotionsPage() {
  const [code, setCode] = useState('GRILL10')
  const [message, setMessage] = useState('')
  const queryClient = useQueryClient()
  const promotion = useQuery({
    queryKey: ['race-coupon'],
    queryFn: async () => {
      const modules = await api.modules()
      const variant = modules.find((module) => module.name === 'race')?.variant ?? 'off'
      if (variant === 'off') return { coupon: null, variant }
      return { coupon: await api.coupon('GRILL10'), variant }
    },
    retry: false,
  })
  const variant: Variant = promotion.data?.variant ?? 'unknown'
  const coupon = promotion.data?.coupon
  const redemption = useMutation({
    mutationFn: api.redeemCoupon,
    onSuccess: async (result) => {
      setMessage(`Kupon wykorzystany! Rabat ${result.discount_percent}%.`)
      await queryClient.invalidateQueries({ queryKey: ['race-coupon'] })
    },
    onError: async () => {
      await queryClient.invalidateQueries({ queryKey: ['race-coupon'] })
    },
  })
  const reset = useMutation({
    mutationFn: api.resetCoupon,
    onMutate: () => {
      redemption.reset()
      setMessage('')
    },
    onSuccess: async () => {
      setMessage('Kupon GRILL10 został przywrócony do 1 użycia.')
      await queryClient.invalidateQueries({ queryKey: ['race-coupon'] })
    },
  })

  const redeem = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    reset.reset()
    setMessage('')
    redemption.mutate(code.trim())
  }

  return (
    <section className="promotions">
      <div className="promotions__intro">
        <p className="promotions__eyebrow">Dla miłośników grillowania</p>
        <h1>Grillowe promocje</h1>
        <p className="muted">Wykorzystaj kupon i przygotuj się na dobry sezon przy grillu.</p>
      </div>
      <article className="card promotion-card">
        <div className="promotion-card__offer">
          <span className="promotion-card__discount">{coupon?.discount_percent ?? 10}%</span>
          <div>
            <p className="promotions__eyebrow">Kupon rabatowy</p>
            <h2>GRILL10</h2>
            <p className="muted">Rabat na Twoje grillowe zakupy</p>
          </div>
        </div>
        <div className="promotion-card__availability">
          <p>
            Dostępne wykorzystania: <strong>{coupon?.uses_left ?? (variant === 'off' ? '—' : '…')}</strong>
          </p>
          {(variant === 'secure' || variant === 'vulnerable') && (
            <button
              className="promotion-reset"
              type="button"
              onClick={() => reset.mutate()}
              disabled={reset.isPending || redemption.isPending}
              aria-label="Przywróć kupon GRILL10 do jednego użycia"
            >
              {reset.isPending ? 'Resetuję…' : 'Resetuj kupon'}
            </button>
          )}
        </div>
        {variant === 'off' ? (
          <p className="promotion-notice" role="status">Moduł promocji jest wyłączony. Ustaw BBQ_MODULE_RACE na vulnerable lub secure.</p>
        ) : (
          <form className="promotion-form" onSubmit={redeem}>
            <label htmlFor="coupon-code">Kod rabatowy</label>
            <div className="promotion-form__row">
              <input id="coupon-code" value={code} onChange={(event) => setCode(event.target.value)} required maxLength={32} />
              <button type="submit" disabled={redemption.isPending || reset.isPending}>
                {redemption.isPending ? 'Przetwarzanie…' : 'Wykorzystaj kupon'}
              </button>
            </div>
            {message && <p className="ok" role="status">{message}</p>}
            {redemption.error && <p className="error" role="alert">{redemption.error.message}</p>}
            {reset.error && <p className="error" role="alert">{reset.error.message}</p>}
            {promotion.isError && <p className="error" role="alert">Nie udało się pobrać informacji o kuponie.</p>}
          </form>
        )}
        <p className="promotion-card__variant">Wariant modułu: <strong>{variant}</strong></p>
      </article>
    </section>
  )
}
