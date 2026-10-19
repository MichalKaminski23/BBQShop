export type Variant = 'vulnerable' | 'secure' | 'off'

export interface ModuleInfo {
  name: string
  title: string
  description: string
  variant: Variant
}

export interface Health {
  postgres: 'ok' | 'error'
  mongo: 'ok' | 'error'
}

export interface Product {
  id: number
  name: string
  category: string
  price: string
  description: string
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`/api${path}`)
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, describeError(body) ?? response.statusText)
  }
  return body as T
}

function describeError(body: unknown): string | null {
  if (body && typeof body === 'object' && 'detail' in body) {
    const { detail } = body
    return typeof detail === 'string' ? detail : JSON.stringify(detail)
  }
  return null
}

export const api = {
  health: () => request<Health>('/health'),
  modules: () => request<ModuleInfo[]>('/modules'),
  searchProducts: (q: string) =>
    request<Product[]>(`/products/search?${new URLSearchParams({ q })}`),
}
