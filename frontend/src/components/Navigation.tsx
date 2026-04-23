import { NavLink } from 'react-router-dom'

function Navigation() {
  return (
    <nav className="navigation">
      <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
        <span className="icon">🏠</span>
        <span className="label">Home</span>
      </NavLink>
      <NavLink
        to="/my-machines"
        className={({ isActive }) => (isActive ? 'active' : '')}
      >
        <span className="icon">🧺</span>
        <span className="label">My Machines</span>
      </NavLink>
      <NavLink to="/profile" className={({ isActive }) => (isActive ? 'active' : '')}>
        <span className="icon">👤</span>
        <span className="label">Profile</span>
      </NavLink>
    </nav>
  )
}

export default Navigation
