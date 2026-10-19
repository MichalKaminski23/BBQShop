import type { Variant } from '../api/client'

const LABELS: Record<Variant, string> = {
  vulnerable: 'podatny',
  secure: 'bezpieczny',
  off: 'wyłączony',
}

export function VariantBadge({ variant }: { variant: Variant }) {
  return <span className={`badge badge--${variant}`}>{LABELS[variant]}</span>
}
