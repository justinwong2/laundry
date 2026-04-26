/**
 * PingModal - Modal for pinging a machine's user.
 *
 * Now also includes powerup options!
 * If user has spam bombs or name & shame in inventory,
 * they can use them here instead of a regular ping.
 */

import { useState } from 'react'
import { Machine } from '../api/client'
import { usePingMachine } from '../hooks/useMachines'
import { useInventory, useSpamBomb, useNameShame, hasPowerup } from '../hooks/usePowerups'

interface PingModalProps {
  machine: Machine
  userCoins: number
  onClose: () => void
}

function PingModal({ machine, userCoins, onClose }: PingModalProps) {
  const [message, setMessage] = useState('')

  // Regular ping mutation
  const pingMutation = usePingMachine()

  // Powerup data and mutations
  const { data: inventory } = useInventory()
  const spamBombMutation = useSpamBomb()
  const nameShameMutation = useNameShame()

  const session = machine.current_session

  // Check what powerups the user has
  const hasSpamBomb = hasPowerup(inventory, 'spam_bomb')
  const hasNameShame = hasPowerup(inventory, 'name_shame')
  const hasPowerups = hasSpamBomb || hasNameShame

  // Regular ping handler
  const handlePing = async () => {
    if (userCoins < 2) {
      alert('You need at least 2 coins to ping someone')
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

  // Spam bomb handler
  const handleSpamBomb = async () => {
    const confirmed = window.confirm(
      `Use SPAM BOMB on @${session?.username || 'user'}?\n\n` +
      `They will receive 20 notifications over the next minute!`
    )
    if (!confirmed) return

    try {
      const result = await spamBombMutation.mutateAsync(machine.id)
      alert(result.message)
      onClose()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to use spam bomb')
    }
  }

  // Name & shame handler
  const handleNameShame = async () => {
    const confirmed = window.confirm(
      `Use NAME & SHAME on @${session?.username || 'user'}?\n\n` +
      `A message will be posted to the group chat calling them out!`
    )
    if (!confirmed) return

    try {
      const result = await nameShameMutation.mutateAsync(machine.id)
      alert(result.message)
      onClose()
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to use name & shame')
    }
  }

  // Check if any mutation is in progress
  const isAnyPending = pingMutation.isPending || spamBombMutation.isPending || nameShameMutation.isPending

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

        {/* Regular ping section */}
        <div className="ping-section">
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
            COST: <strong>2 COINS</strong> (YOU HAVE {userCoins})
          </p>

          <button
            className="btn-primary"
            onClick={handlePing}
            disabled={isAnyPending || userCoins < 2}
            style={{ width: '100%', marginBottom: '8px' }}
          >
            {pingMutation.isPending ? 'SENDING...' : 'SEND PING (2 COINS)'}
          </button>
        </div>

        {/* Powerup section - only shown if user has powerups */}
        {hasPowerups && (
          <div className="powerup-section">
            <div className="powerup-divider">
              <span>OR USE A POWERUP</span>
            </div>

            <div className="powerup-buttons">
              {hasSpamBomb && (
                <button
                  className="btn-powerup spam-bomb"
                  onClick={handleSpamBomb}
                  disabled={isAnyPending}
                >
                  {spamBombMutation.isPending ? 'SENDING...' : '💣 SPAM BOMB'}
                </button>
              )}

              {hasNameShame && (
                <button
                  className="btn-powerup name-shame"
                  onClick={handleNameShame}
                  disabled={isAnyPending}
                >
                  {nameShameMutation.isPending ? 'POSTING...' : '📢 NAME & SHAME'}
                </button>
              )}
            </div>

            <p className="powerup-hint">
              Powerups are FREE to use (already purchased)
            </p>
          </div>
        )}

        {/* Cancel button */}
        <button
          className="btn-secondary"
          onClick={onClose}
          style={{ width: '100%', marginTop: '16px' }}
        >
          CANCEL
        </button>
      </div>
    </div>
  )
}

export default PingModal
