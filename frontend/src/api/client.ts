const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getInitData(): string {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp.initData
  }
  return ''
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const initData = getInitData()

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Telegram-Init-Data': initData,
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export interface Machine {
  id: number
  code: string
  type: 'washer' | 'dryer'
  block: string
  cycle_duration_minutes: number
  qr_code: string
  current_session: Session | null
}

export interface Session {
  id: number
  user_id: number
  machine_id: number
  started_at: string
  expected_end_at: string
  ended_at: string | null
  message: string | null
  username?: string
}

export interface User {
  id: number
  telegram_id: number
  username: string | null
  block: string
  coins: number
  created_at: string
}

export interface Transaction {
  id: number
  amount: number
  reason: string
  created_at: string
}

export const api = {
  getMachines: () => apiRequest<Machine[]>('/api/machines'),

  getMachine: (id: number) => apiRequest<Machine>(`/api/machines/${id}`),

  claimMachine: (machineId: number, message?: string) =>
    apiRequest<Session>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ machine_id: machineId, message }),
    }),

  releaseMachine: (sessionId: number) =>
    apiRequest<Session>(`/api/sessions/${sessionId}`, {
      method: 'DELETE',
    }),

  getMySessions: () => apiRequest<Session[]>('/api/sessions/mine'),

  getProfile: () => apiRequest<User>('/api/users/me'),

  register: (block: string) =>
    apiRequest<User>('/api/users/register', {
      method: 'POST',
      body: JSON.stringify({ block }),
    }),

  getTransactions: () => apiRequest<Transaction[]>('/api/users/me/transactions'),

  pingMachine: (machineId: number) =>
    apiRequest<{ success: boolean; message: string; new_balance: number }>(
      `/api/ping/${machineId}`,
      { method: 'POST' }
    ),
}
