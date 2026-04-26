import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, Machine } from '../api/client'

export function useMachines() {
  return useQuery({
    queryKey: ['machines'],
    queryFn: api.getMachines,
    refetchInterval: 30000, // Refresh every 30 seconds
  })
}

export function useMachine(id: number) {
  return useQuery({
    queryKey: ['machines', id],
    queryFn: () => api.getMachine(id),
    enabled: !!id,
  })
}

export function useMySessions() {
  return useQuery({
    queryKey: ['sessions', 'mine'],
    queryFn: api.getMySessions,
  })
}

export function useClaimMachine() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ machineId, message, cycleDuration }: { machineId: number; message?: string; cycleDuration?: number }) =>
      api.claimMachine(machineId, message, cycleDuration),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

export function useReleaseMachine() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (sessionId: number) => api.releaseMachine(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

export function usePingMachine() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ machineId, message }: { machineId: number; message?: string }) =>
      api.pingMachine(machineId, message),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
  })
}

export function useForceRelease() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (qrCode: string) => api.forceReleaseMachine(qrCode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] })
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })
}

export function useProfile() {
  return useQuery({
    queryKey: ['profile'],
    queryFn: api.getProfile,
  })
}

export function useTransactions() {
  return useQuery({
    queryKey: ['transactions'],
    queryFn: api.getTransactions,
  })
}

export function groupMachinesByType(machines: Machine[]) {
  const washers = machines.filter((m) => m.type === 'washer')
  const dryers = machines.filter((m) => m.type === 'dryer')
  return { washers, dryers }
}
