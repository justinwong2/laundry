import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMachines, useForceRelease } from '../hooks/useMachines'

interface ForceReleaseProps {
  qrCode: string
}

function ForceRelease({ qrCode }: ForceReleaseProps) {
  const navigate = useNavigate()
  const { data: machines, isLoading } = useMachines()
  const forceReleaseMutation = useForceRelease()
  const [confirmed, setConfirmed] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    message: string
  } | null>(null)

  const machine = machines?.find((m) => m.qr_code === qrCode)

  const handleForceRelease = async () => {
    try {
      const response = await forceReleaseMutation.mutateAsync(qrCode)
      setResult({
        success: response.success,
        message: response.message,
      })
    } catch (error) {
      setResult({
        success: false,
        message: error instanceof Error ? error.message : 'Failed to force release',
      })
    }
  }

  const handleGoHome = () => {
    navigate('/')
  }

  if (isLoading) {
    return (
      <div className="force-release-page">
        <div className="loading">Loading machine info...</div>
      </div>
    )
  }

  if (!machine) {
    return (
      <div className="force-release-page">
        <div className="error-card">
          <h2>Machine Not Found</h2>
          <p>Could not find machine with code: {qrCode}</p>
          <button className="btn-primary" onClick={handleGoHome}>
            Go to Home
          </button>
        </div>
      </div>
    )
  }

  // Show result after action
  if (result) {
    return (
      <div className="force-release-page">
        <div className={`result-card ${result.success ? 'success' : 'error'}`}>
          <h2>{result.success ? 'Machine Released' : 'Release Failed'}</h2>
          <p>{result.message}</p>
          <button className="btn-primary" onClick={handleGoHome}>
            Go to Home
          </button>
        </div>
      </div>
    )
  }

  const session = machine.current_session
  const machineLabel = `${machine.type === 'washer' ? 'Washer' : 'Dryer'} ${machine.code}`

  // Machine is not in use
  if (!session) {
    return (
      <div className="force-release-page">
        <div className="info-card">
          <h2>{machineLabel}</h2>
          <p className="status available">Available</p>
          <p>This machine is not currently in use. No action needed.</p>
          <button className="btn-primary" onClick={handleGoHome}>
            Go to Home
          </button>
        </div>
      </div>
    )
  }

  // Calculate time remaining
  const endTime = new Date(session.expected_end_at)
  const now = new Date()
  const minutesRemaining = Math.max(0, Math.round((endTime.getTime() - now.getTime()) / 60000))
  const isDone = minutesRemaining === 0

  return (
    <div className="force-release-page">
      <div className="force-release-card">
        <h2>Force Release Machine</h2>

        <div className="machine-info">
          <p className="machine-label">{machineLabel}</p>
          <p className="machine-block">Block {machine.block}</p>
          <p className="claimed-by">
            Claimed by: @{session.username || 'unknown'}
          </p>
          <p className={`status ${isDone ? 'done' : 'in-use'}`}>
            {isDone ? 'Cycle complete' : `${minutesRemaining} min remaining`}
          </p>
        </div>

        <div className="warning-box">
          <p><strong>WARNING</strong></p>
          <p>Only force release if the machine is <strong>EMPTY</strong>.</p>
          <p>This action is irreversible and the original user will be notified.</p>
        </div>

        {!confirmed ? (
          <div className="actions">
            <button className="btn-secondary" onClick={handleGoHome}>
              Cancel
            </button>
            <button className="btn-warning" onClick={() => setConfirmed(true)}>
              I Understand
            </button>
          </div>
        ) : (
          <div className="actions">
            <button className="btn-secondary" onClick={() => setConfirmed(false)}>
              Go Back
            </button>
            <button
              className="btn-danger"
              onClick={handleForceRelease}
              disabled={forceReleaseMutation.isPending}
            >
              {forceReleaseMutation.isPending ? 'Releasing...' : 'Force Release'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default ForceRelease
