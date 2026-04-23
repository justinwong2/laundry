import { useState } from 'react'
import { Machine } from '../api/client'
import { usePingMachine } from '../hooks/useMachines'

interface PingModalProps {
  machine: Machine
  userCoins: number
  onClose: () => void
}

function PingModal({ machine, userCoins, onClose }: PingModalProps) {
  const [message, setMessage] = useState('')
  const pingMutation = usePingMachine()
  const session = machine.current_session

  const handlePing = async () => {
    if (userCoins < 3) {
      alert('You need at least 3 coins to ping someone')
      return
    }

    try {
      await pingMutation.mutateAsync({ machineId: machine.id, message: message || undefined })
      alert('Ping sent! The user has been notified.')
      onClose()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to ping')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>
          Ping {machine.type === 'washer' ? 'Washer' : 'Dryer'} {machine.code}
        </h2>

        {session && (
          <div className="machine-info">
            <p>
              Currently used by: <strong>@{session.username || 'user'}</strong>
            </p>
            {session.message && (
              <p className="user-message">"{session.message}"</p>
            )}
          </div>
        )}

        <div className="form-group" style={{ marginTop: '16px', marginBottom: '16px' }}>
          <label>Add a custom message (optional)</label>
          <input
            type="text"
            placeholder="e.g., I'm waiting with wet clothes!"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            maxLength={100}
          />
        </div>

        <p className="ping-cost">
          COST: <strong>3 COINS</strong> (YOU HAVE {userCoins})
        </p>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>
            CANCEL
          </button>
          <button
            className="btn-primary"
            onClick={handlePing}
            disabled={pingMutation.isPending || userCoins < 3}
          >
            {pingMutation.isPending ? 'SENDING...' : 'SEND PING'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PingModal
