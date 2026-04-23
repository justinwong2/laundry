import { useMySessions, useReleaseMachine, useMachines } from '../hooks/useMachines'

function MyMachines() {
  const { data: sessions, isLoading: sessionsLoading } = useMySessions()
  const { data: machines } = useMachines()
  const releaseMutation = useReleaseMachine()

  const handleRelease = async (sessionId: number) => {
    if (!confirm('Release this machine?')) return

    try {
      await releaseMutation.mutateAsync(sessionId)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to release')
    }
  }

  const getMachineDetails = (machineId: number) => {
    return machines?.find((m) => m.id === machineId)
  }

  const getTimeInfo = (session: { expected_end_at: string }) => {
    const endStr = session.expected_end_at;
    const endTime = new Date(endStr.endsWith('Z') ? endStr : endStr + 'Z');
    const now = new Date()
    const diff = endTime.getTime() - now.getTime()

    if (diff <= 0) {
      return { text: 'Done!', isDone: true }
    }

    const minutes = Math.ceil(diff / (1000 * 60))
    return { text: `${minutes} min remaining`, isDone: false }
  }

  if (sessionsLoading) {
    return <div className="loading">Loading sessions...</div>
  }

  return (
    <div className="my-machines">
      <header className="header">
        <h1>MY MACHINES</h1>
      </header>

      <main className="content">
        {!sessions || sessions.length === 0 ? (
          <div className="empty-state">
            <p>NO ACTIVE SESSIONS</p>
            <p>CLAIM A MACHINE FROM HOME</p>
          </div>
        ) : (
          <ul className="session-list">
            {sessions.map((session) => {
              const machine = getMachineDetails(session.machine_id)
              const timeInfo = getTimeInfo(session)

              return (
                <li
                  key={session.id}
                  className={`session-card ${timeInfo.isDone ? 'done' : ''}`}
                >
                  <div className="session-info">
                    <div className="machine-name">
                      {machine?.type === 'washer' ? 'Washer' : 'Dryer'}{' '}
                      {machine?.code}
                    </div>
                    <div className="time-remaining">{timeInfo.text}</div>
                  </div>
                  <button
                    className="btn-release"
                    onClick={() => handleRelease(session.id)}
                    disabled={releaseMutation.isPending || !timeInfo.isDone}
                  >
                    {releaseMutation.isPending ? 'RELEASING...' : 'RELEASE [+2]'}
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </main>
    </div>
  )
}

export default MyMachines
