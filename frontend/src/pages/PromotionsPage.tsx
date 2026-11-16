import { useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { ApiError, api } from '../api/client'
import './PromotionsPage.css'

type Variant = 'vulnerable' | 'secure' | 'off' | 'unknown'

export function PromotionsPage() {
  const [code, setCode] = useState('GRILL10')
  const [message, setMessage] = useState('')
  const [acceptedUses, setAcceptedUses] = useState(0)
  const [simulationMessage, setSimulationMessage] = useState('')
  const [simulationPending, setSimulationPending] = useState(false)
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
      setAcceptedUses((uses) => uses + 1)
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
      setAcceptedUses(0)
      setSimulationMessage('')
    },
    onSuccess: async () => {
      setAcceptedUses(0)
      setSimulationMessage('')
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

  const simulateRace = async () => {
    reset.reset()
    redemption.reset()
    setMessage('')
    setSimulationMessage('Uruchamiam 20 równoczesnych żądań…')
    setAcceptedUses(0)
    setSimulationPending(true)
    try {
      await api.resetCoupon()
      const results = await Promise.allSettled(
        Array.from({ length: 20 }, () => api.redeemCoupon('GRILL10')),
      )
      const accepted = results.filter((result) => result.status === 'fulfilled').length
      const unexpected = results.filter(
        (result) =>
          result.status === 'rejected' &&
          (!(result.reason instanceof ApiError) || result.reason.status !== 409),
      ).length
      setAcceptedUses(accepted)
      setSimulationMessage(
        unexpected > 0
          ? `Symulacja niepełna: ${accepted} sukcesów, ${unexpected} błędów żądań.`
          : `Symulacja zakończona: ${accepted} z 20 żądań zaakceptowano.`,
      )
      await queryClient.invalidateQueries({ queryKey: ['race-coupon'] })
    } catch (error) {
      setSimulationMessage(
        `Nie udało się przygotować symulacji: ${error instanceof Error ? error.message : 'błąd API'}`,
      )
    } finally {
      setSimulationPending(false)
    }
  }

  const basePrice = 100
  const discountPercent = coupon?.discount_percent ?? 10
  const totalDiscount = Math.min(basePrice, acceptedUses * (basePrice * discountPercent / 100))
  const finalPrice = basePrice - totalDiscount

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
              disabled={reset.isPending || redemption.isPending || simulationPending}
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
              <button
                type="submit"
                disabled={redemption.isPending || reset.isPending || simulationPending}
              >
                {redemption.isPending ? 'Przetwarzanie…' : 'Wykorzystaj kupon'}
              </button>
            </div>
            {message && <p className="ok" role="status">{message}</p>}
            {redemption.error && <p className="error" role="alert">{redemption.error.message}</p>}
            {reset.error && <p className="error" role="alert">{reset.error.message}</p>}
            {promotion.isError && <p className="error" role="alert">Nie udało się pobrać informacji o kuponie.</p>}
          </form>
        )}
        {variant !== 'off' && (
          <section className="promotion-demo" aria-label="Demonstracja naliczania rabatu">
            <div>
              <p className="promotions__eyebrow">Symulowany koszyk</p>
              <p className="promotion-demo__price">
                <span>Cena bazowa</span><strong>{basePrice.toFixed(2)} zł</strong>
              </p>
              <p className="promotion-demo__price promotion-demo__price--discount">
                <span>Łączny rabat ({acceptedUses} × {discountPercent}%)</span>
                <strong>−{totalDiscount.toFixed(2)} zł</strong>
              </p>
              <p className="promotion-demo__total">
                <span>Do zapłaty</span><strong>{finalPrice.toFixed(2)} zł</strong>
              </p>
            </div>
            <button
              className="promotion-simulate promotion-simulate--hidden"
              type="button"
              onClick={() => void simulateRace()}
              disabled={redemption.isPending || reset.isPending || simulationPending}
            >
              Symuluj 20 równoczesnych użyć
            </button>
            {simulationMessage && <p className="promotion-demo__message" role="status">{simulationMessage}</p>}
            <p className="muted promotion-demo__hint">
              Każde zaakceptowane żądanie nalicza demonstracyjne {discountPercent}% od ceny 100 zł; kwota nie spada poniżej 0 zł.
            </p>
          </section>
        )}
        <p className="promotion-card__variant">Wariant modułu: <strong>{variant}</strong></p>
      </article>
    </section>
  )
}
