import { useState } from 'react'
import { Machine } from '../api/client'
import { useClaimMachine } from '../hooks/useMachines'

interface ClaimModalProps {
  machine: Machine
  onClose: () => void
}

function ClaimModal({ machine, onClose }: ClaimModalProps) {
  const [message, setMessage] = useState('')
  const [cycleDuration, setCycleDuration] = useState(machine.cycle_duration_minutes)
  const claimMutation = useClaimMachine()

  const handleClaim = async () => {
    try {
      await claimMutation.mutateAsync({
        machineId: machine.id,
        message: message || undefined,
        cycleDuration: cycleDuration,
      })
      onClose()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to claim machine')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>
          Claim {machine.type === 'washer' ? 'Washer' : 'Dryer'} {machine.code}
        </h2>
        <div className="form-group">
          <label>Cycle Duration (minutes)</label>
          <input
            type="number"
            min="1"
            max="180"
            value={cycleDuration}
            onChange={(e) => setCycleDuration(Number(e.target.value))}
          />
        </div>

        <div className="form-group">
          <label>Message (optional)</label>
          <input
            type="text"
            placeholder="e.g., Please move to dryer when done"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={200}
          />
        </div>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleClaim}
            disabled={claimMutation.isPending}
          >
            {claimMutation.isPending ? 'Claiming...' : 'Claim Machine (+1 🪙)'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ClaimModal
