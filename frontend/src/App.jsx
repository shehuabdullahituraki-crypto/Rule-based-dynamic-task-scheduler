import React, { useState } from 'react'
import Login from './Login'
import Dashboard from './Dashboard'

export default function App() {
  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)

  function handleLoginSuccess(newToken, newUser) {
    setToken(newToken)
    setUser(newUser)
  }

  function handleLogout() {
    setToken(null)
    setUser(null)
  }

  if (!token || !user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return <Dashboard token={token} user={user} onLogout={handleLogout} />
}