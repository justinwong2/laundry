import { useState } from 'react'
import { Machine } from '../api/client'
import { useMachines, useProfile, groupMachinesByType } from '../hooks/useMachines'
import MachineGrid from '../components/MachineGrid'
import ClaimModal from '../components/ClaimModal'
import PingModal from '../components/PingModal'

function Home() {
  const { data: machines, isLoading, error } = useMachines()
  const { data: profile } = useProfile()
  const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null)
  const [modalType, setModalType] = useState<'claim' | 'ping' | null>(null)

  const handleMachineClick = (machine: Machine) => {
    setSelectedMachine(machine)
    if (!machine.current_session) {
      setModalType('claim')
    } else if (machine.current_session.user_id !== profile?.id) {
      setModalType('ping')
    }
  }

  const closeModal = () => {
    setSelectedMachine(null)
    setModalType(null)
  }

  if (isLoading) {
    return <div className="loading">Loading machines...</div>
  }

  if (error) {
    return <div className="error">Failed to load machines</div>
  }

  const { washers, dryers } = groupMachinesByType(machines || [])

  // Get messages from machines with active sessions
  const messages = (machines || [])
    .filter((m) => m.current_session?.message)
    .map((m) => ({
      machineCode: m.code,
      machineType: m.type,
      username: m.current_session?.username,
      message: m.current_session?.message,
    }))

  return (
    <div className="home">
      <header className="header">
        <h1>🧺 Block E Laundry</h1>
        <div className="coins">💰 {profile?.coins ?? 0} coins</div>
      </header>

      <main className="content">
        <MachineGrid
          title="WASHERS"
          machines={washers}
          onMachineClick={handleMachineClick}
          currentUserId={profile?.id}
        />

        <MachineGrid
          title="DRYERS"
          machines={dryers}
          onMachineClick={handleMachineClick}
          currentUserId={profile?.id}
        />

        {messages.length > 0 && (
          <div className="messages-section">
            <h3>📝 Messages</h3>
            <ul>
              {messages.map((m, i) => (
                <li key={i}>
                  {m.machineCode} {m.machineType} (@{m.username}): "{m.message}"
                </li>
              ))}
            </ul>
          </div>
        )}
      </main>

      {selectedMachine && modalType === 'claim' && (
        <ClaimModal machine={selectedMachine} onClose={closeModal} />
      )}

      {selectedMachine && modalType === 'ping' && profile && (
        <PingModal
          machine={selectedMachine}
          userCoins={profile.coins}
          onClose={closeModal}
        />
      )}
    </div>
  )
}

export default Home
