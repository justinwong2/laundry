import { NavLink } from 'react-router-dom'

function Navigation() {
  return (
    <nav className="navigation">
      <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
        <span className="icon">[=]</span>
        <span className="label">HOME</span>
      </NavLink>
      <NavLink
        to="/my-machines"
        className={({ isActive }) => (isActive ? 'active' : '')}
      >
        <span className="icon">{'{@}'}</span>
        <span className="label">MINE</span>
      </NavLink>
      <NavLink to="/powerups" className={({ isActive }) => (isActive ? 'active' : '')}>
        <span className="icon">[$]</span>
        <span className="label">SHOP</span>
      </NavLink>
      <NavLink to="/profile" className={({ isActive }) => (isActive ? 'active' : '')}>
        <span className="icon">[*]</span>
        <span className="label">STATS</span>
      </NavLink>
    </nav>
  )
}

export default Navigation
