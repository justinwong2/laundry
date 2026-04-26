/**
 * React Query hooks for powerup operations.
 *
 * These hooks wrap the API calls and handle:
 * - Caching (so we don't refetch unnecessarily)
 * - Loading/error states (returned by the hooks)
 * - Cache invalidation (refetch related data after mutations)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'

/**
 * Fetch all available powerups for the shop.
 *
 * Returns the "catalog" - what's available to buy.
 * This data rarely changes, so we don't auto-refetch.
 */
export function usePowerups() {
  return useQuery({
    queryKey: ['powerups'],
    queryFn: api.getPowerups,
    staleTime: 5 * 60 * 1000, // Consider fresh for 5 minutes
  })
}

/**
 * Fetch user's powerup inventory.
 *
 * Returns powerups the user owns with quantity > 0.
 * Refetches when user buys or uses a powerup.
 */
export function useInventory() {
  return useQuery({
    queryKey: ['inventory'],
    queryFn: api.getInventory,
  })
}

/**
 * Buy a powerup.
 *
 * After purchase:
 * - Refetch inventory (quantity changed)
 * - Refetch profile (coins changed)
 */
export function useBuyPowerup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (powerupType: string) => api.buyPowerup(powerupType),
    onSuccess: () => {
      // Invalidate = mark as stale, triggers refetch on next access
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

/**
 * Use a spam bomb powerup.
 *
 * After use:
 * - Refetch inventory (quantity decreased)
 * - No need to refetch machines (target user gets messages, UI doesn't change)
 */
export function useSpamBomb() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (machineId: number) => api.useSpamBomb(machineId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
    },
  })
}

/**
 * Use a name and shame powerup.
 *
 * After use:
 * - Refetch inventory (quantity decreased)
 */
export function useNameShame() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (machineId: number) => api.useNameShame(machineId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
    },
  })
}

/**
 * Helper: Check if user has a specific powerup in inventory.
 *
 * Usage:
 *   const { data: inventory } = useInventory()
 *   const hasSpamBomb = hasPowerup(inventory, 'spam_bomb')
 */
export function hasPowerup(
  inventory: ReturnType<typeof useInventory>['data'],
  powerupType: string
): boolean {
  if (!inventory) return false
  return inventory.some((item) => item.powerup_type === powerupType && item.quantity > 0)
}

/**
 * Helper: Get quantity of a specific powerup.
 */
export function getPowerupQuantity(
  inventory: ReturnType<typeof useInventory>['data'],
  powerupType: string
): number {
  if (!inventory) return 0
  const item = inventory.find((i) => i.powerup_type === powerupType)
  return item?.quantity ?? 0
}
