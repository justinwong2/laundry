import { Machine } from '../api/client'

interface MachineCardProps {
  machine: Machine
  onClick: () => void
  isOwner: boolean
}

function MachineCard({ machine, onClick, isOwner }: MachineCardProps) {
  const session = machine.current_session
  const isAvailable = !session
  const getUtcDate = (dateString: string) => {
    return new Date(dateString.endsWith('Z') ? dateString : dateString + 'Z')
  }

  const isDone = session && getUtcDate(session.expected_end_at) < new Date()

  const getTimeRemaining = () => {
    if (!session) return null
    const endTime = getUtcDate(session.expected_end_at)
    const now = new Date()
    const diff = endTime.getTime() - now.getTime()

    if (diff <= 0) return 'DONE'

    const minutes = Math.ceil(diff / (1000 * 60))
    return `${minutes}m`
  }

  const getStatusEmoji = () => {
    if (isAvailable) return '🟢'
    if (isDone) return '⚠️'
    return '🔴'
  }

  const getStatusClass = () => {
    if (isAvailable) return 'available'
    if (isDone) return 'done'
    return 'in-use'
  }

  return (
    <div className={`machine-card ${getStatusClass()}`} onClick={onClick}>
      <div className="machine-code">{machine.code}</div>
      <div className="machine-status">{getStatusEmoji()}</div>
      {session && (
        <>
          <div className="machine-user">@{session.username || 'user'}</div>
          <div className="machine-time">{getTimeRemaining()}</div>
          {session.message && (
            <div className="machine-message" style={{ fontSize: '0.8em', fontStyle: 'italic', marginTop: '4px', opacity: 0.8 }}>
              "{session.message}"
            </div>
          )}
        </>
      )}
      {isOwner && <div className="owner-badge">You</div>}
    </div>
  )
}

export default MachineCard
