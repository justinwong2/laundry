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
      'ngrok-skip-browser-warning': 'true',
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

// ─────────────────────────────────────────────────────────────────────────────
// POWERUP TYPES
// ─────────────────────────────────────────────────────────────────────────────

export interface Powerup {
  id: number
  type: string // "spam_bomb" | "name_shame"
  name: string // "Spam Bomb"
  description: string // Shown in shop UI
  cost: number // Price in coins
  icon: string // Emoji: "💣"
}

export interface UserPowerup {
  id: number
  powerup_id: number
  powerup_type: string
  powerup_name: string
  powerup_icon: string
  quantity: number
}

export interface BuyPowerupResponse {
  success: boolean
  message: string
  new_balance: number
  quantity: number
}

export interface UsePowerupResponse {
  success: boolean
  message: string
  job_id?: number // Only for spam bomb
}

export const api = {
  getMachines: () => apiRequest<Machine[]>('/api/machines'),

  getMachine: (id: number) => apiRequest<Machine>(`/api/machines/${id}`),

  claimMachine: (machineId: number, message?: string, cycleDuration?: number) =>
    apiRequest<Session>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ machine_id: machineId, message, cycle_duration_minutes: cycleDuration }),
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

  pingMachine: (machineId: number, message?: string) =>
    apiRequest<{ success: boolean; message: string; new_balance: number }>(
      `/api/ping/${machineId}`,
      { method: 'POST', body: message ? JSON.stringify({ message }) : undefined }
    ),

  forceReleaseMachine: (qrCode: string) =>
    apiRequest<{ success: boolean; message: string; previous_owner_notified: boolean }>(
      `/api/machines/${qrCode}/force-release`,
      { method: 'POST' }
    ),

  // ─────────────────────────────────────────────────────────────────────────
  // POWERUPS
  // ────────────────────────────────────────────────────���────────────────────

  /** Get all available powerups for the shop */
  getPowerups: () => apiRequest<Powerup[]>('/api/powerups'),

  /** Get user's powerup inventory */
  getInventory: () => apiRequest<UserPowerup[]>('/api/powerups/inventory'),

  /** Buy a powerup */
  buyPowerup: (powerupType: string) =>
    apiRequest<BuyPowerupResponse>('/api/powerups/buy', {
      method: 'POST',
      body: JSON.stringify({ powerup_type: powerupType }),
    }),

  /** Use spam bomb on a machine */
  useSpamBomb: (machineId: number) =>
    apiRequest<UsePowerupResponse>('/api/powerups/use/spam-bomb', {
      method: 'POST',
      body: JSON.stringify({ machine_id: machineId }),
    }),

  /** Use name & shame on a machine */
  useNameShame: (machineId: number) =>
    apiRequest<UsePowerupResponse>('/api/powerups/use/name-shame', {
      method: 'POST',
      body: JSON.stringify({ machine_id: machineId }),
    }),
}
