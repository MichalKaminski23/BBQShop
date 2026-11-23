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

export const productImages: Record<number, string> = {
  1: 'grill.svg',
  2: 'grill.svg',
  3: 'fuel.svg',
  4: 'fuel.svg',
  5: 'accessories.svg',
  6: 'accessories.svg',
  7: 'sauce.svg',
}

export interface LoginResult {
  username: string
  role: 'customer' | 'admin'
}

export interface FileContent {
  name: string
  content: string
}

export interface WriteResult {
  name: string
  written: number
}

export interface PingResult {
  host: string
  command: string
  exit_code: number
  output: string
}

export interface OrderItem {
  id: number
  product_id: number
  quantity: number
  unit_price: string
}

export interface Order {
  id: number
  customer_name: string
  created_at: string
  items: OrderItem[]
}

export interface QueryMetrics {
  count: number | null
  timeMs: number | null
}

export interface OrdersResult {
  orders: Order[]
  metrics: QueryMetrics
}

export interface OrderRequest {
  customer_name: string
  items: Array<{ product_id: number; quantity: number }>
}

export interface CreateOrderResult {
  order: Order
  created: boolean
}

export interface ResourceDemoResult {
  resource_type: 'file' | 'socket'
  opened_count: number
  closed_count: number
  outstanding_count: number
}

export interface Coupon {
  code: string
  discount_percent: number
  uses_left: number
}

export interface Redemption extends Coupon {
  message: string
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
  orders: async (customerName?: string): Promise<OrdersResult> => {
    const query = customerName
      ? `?${new URLSearchParams({ customer_name: customerName })}`
      : ''
    const response = await fetch(`/api/orders${query}`)
    const body: unknown = await response.json().catch(() => null)
    if (!response.ok) {
      throw new ApiError(response.status, describeError(body) ?? response.statusText)
    }

    const queryCount = response.headers.get('X-SQL-Query-Count')
    const queryTime = response.headers.get('X-SQL-Query-Time-Ms')
    return {
      orders: body as Order[],
      metrics: {
        count: queryCount === null ? null : Number(queryCount),
        timeMs: queryTime === null ? null : Number(queryTime),
      },
    }
  },
  createOrder: async (payload: OrderRequest, idempotencyKey: string): Promise<CreateOrderResult> => {
    const response = await fetch('/api/orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
      },
      body: JSON.stringify(payload),
    })
    const body: unknown = await response.json().catch(() => null)
    if (!response.ok) {
      throw new ApiError(response.status, describeError(body) ?? response.statusText)
    }
    return body as CreateOrderResult
  },
  login: (username: string, password: string) =>
    post<LoginResult>('/login', { username, password }),
  openFdleakFiles: (count: number) =>
    request<ResourceDemoResult>(`/fdleak/file?${new URLSearchParams({ count: String(count) })}`),
  openFdleakSockets: (count: number) =>
    request<ResourceDemoResult>(`/fdleak/socket?${new URLSearchParams({ count: String(count) })}`),
  readFile: (name: string) => request<FileContent>(`/storage?${new URLSearchParams({ name })}`),
  writeFile: (name: string, content: string) =>
    post<WriteResult>(`/storage?${new URLSearchParams({ name })}`, { content }),
  ping: (host: string) =>
    request<PingResult>(`/cmdi/ping?${new URLSearchParams({ host })}`),
  coupon: (code: string) => request<Coupon>(`/race/coupons/${encodeURIComponent(code)}`),
  redeemCoupon: (code: string) => post<Redemption>('/race/coupons/redeem', { code }),
  resetCoupon: () => post<Coupon>('/race/coupons/reset', {}),
}
