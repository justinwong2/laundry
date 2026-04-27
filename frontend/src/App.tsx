import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useTelegram } from './hooks/useTelegram'
import { useProfile } from './hooks/useMachines'
import Home from './pages/Home'
import MyMachines from './pages/MyMachines'
import Profile from './pages/Profile'
import Powerups from './pages/Powerups'
import ForceRelease from './pages/ForceRelease'
import Navigation from './components/Navigation'
import Register from './pages/Register'
//
function App() {
  const { webApp, user, startParam } = useTelegram()
  const { data: profile, isLoading, error } = useProfile()

  // Use state so we can clear it when user navigates home
  const [forceReleaseQrCode, setForceReleaseQrCode] = useState<string | null>(null)

  // Sync state when startParam becomes available (after Telegram SDK initializes)
  useEffect(() => {
    if (startParam?.startsWith('force_')) {
      setForceReleaseQrCode(startParam.substring(6))
    }
  }, [startParam])

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

  // If opened via force release QR code, show force release page
  if (forceReleaseQrCode) {
    return (
      <BrowserRouter>
        <div className="app">
          <ForceRelease
            qrCode={forceReleaseQrCode}
            onGoHome={() => setForceReleaseQrCode(null)}
          />
        </div>
      </BrowserRouter>
    )
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/my-machines" element={<MyMachines />} />
          <Route path="/powerups" element={<Powerups />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
        <Navigation />
      </div>
    </BrowserRouter>
  )
}

export default App
