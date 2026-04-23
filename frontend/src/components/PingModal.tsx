import { Machine } from '../api/client'
import { usePingMachine } from '../hooks/useMachines'

interface PingModalProps {
  machine: Machine
  userCoins: number
  onClose: () => void
}

function PingModal({ machine, userCoins, onClose }: PingModalProps) {
  const pingMutation = usePingMachine()
  const session = machine.current_session

  const handlePing = async () => {
    if (userCoins < 3) {
      alert('You need at least 3 coins to ping someone')
      return
    }

    try {
      await pingMutation.mutateAsync(machine.id)
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

        <p className="ping-cost">
          Cost: <strong>3 🪙</strong> (you have {userCoins} 🪙)
        </p>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handlePing}
            disabled={pingMutation.isPending || userCoins < 3}
          >
            {pingMutation.isPending ? 'Sending...' : 'Send Ping'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PingModal
