import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useTelegram } from './hooks/useTelegram'
import Home from './pages/Home'
import MyMachines from './pages/MyMachines'
import Profile from './pages/Profile'
import Navigation from './components/Navigation'

function App() {
  const { webApp, user } = useTelegram()

  if (!webApp || !user) {
    return (
      <div className="loading">
        <p>Loading...</p>
      </div>
    )
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
