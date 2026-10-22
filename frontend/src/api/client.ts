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

export interface LoginResult {
  username: string
  role: 'customer' | 'admin'
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

async function post<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, describeError(body) ?? response.statusText)
  }
  return body as T
}

function describeError(body: unknown): string | null {
  if (!body || typeof body !== 'object' || !('detail' in body)) {
    return null
  }
  const { detail } = body
  if (typeof detail === 'string') {
    return detail
  }
  // Błędy walidacji (422) przychodzą jako tablica obiektów – pokaż czytelny komunikat.
  if (Array.isArray(detail)) {
    return 'Nieprawidłowe dane wejściowe.'
  }
  return null
}

export const api = {
  health: () => request<Health>('/health'),
  modules: () => request<ModuleInfo[]>('/modules'),
  searchProducts: (q: string) =>
    request<Product[]>(`/products/search?${new URLSearchParams({ q })}`),
  login: (username: string, password: string) =>
    post<LoginResult>('/login', { username, password }),
}
