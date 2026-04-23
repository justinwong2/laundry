import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useTelegram } from './hooks/useTelegram'
import { useProfile } from './hooks/useMachines'
import Home from './pages/Home'
import MyMachines from './pages/MyMachines'
import Profile from './pages/Profile'
import Navigation from './components/Navigation'
import Register from './pages/Register'

function App() {
  const { webApp, user } = useTelegram()
  const { data: profile, isLoading, error } = useProfile()

  if (!webApp || !user) {
    return (
      <div className="loading">
        <p>Loading Telegram Environment...</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="loading">
        <p>Loading Profile...</p>
      </div>
    )
  }

  if (error || !profile) {
    return <Register />
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/my-machines" element={<MyMachines />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
        <Navigation />
      </div>
    </BrowserRouter>
  )
}

export default App
