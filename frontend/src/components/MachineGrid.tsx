import { Machine } from '../api/client'
import MachineCard from './MachineCard'

interface MachineGridProps {
  title: string
  machines: Machine[]
  onMachineClick: (machine: Machine) => void
  currentUserId?: number
}

function MachineGrid({ title, machines, onMachineClick, currentUserId }: MachineGridProps) {
  return (
    <div className="machine-grid">
      <h2 className="grid-title">{title}</h2>
      <div className="grid">
        {machines.map((machine) => (
          <MachineCard
            key={machine.id}
            machine={machine}
            onClick={() => onMachineClick(machine)}
            isOwner={machine.current_session?.user_id === currentUserId}
          />
        ))}
      </div>
    </div>
  )
}

export default MachineGrid
