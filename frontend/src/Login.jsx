import React, { useState } from 'react'
import { api } from './api'

export default function Login({ onLoginSuccess }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!username || !password) {
      setError('Please fill in both fields.')
      return
    }
    setLoading(true)

    if (mode === 'login') {
      api.login(username, password)
        .then(function (result) {
          onLoginSuccess(result.access_token, result.user)
        })
        .catch(function (err) {
          setError('Login failed: ' + err.message)
        })
        .finally(function () {
          setLoading(false)
        })
    } else {
      api.register(username, password)
        .then(function () {
          return api.login(username, password)
        })
        .then(function (result) {
          onLoginSuccess(result.access_token, result.user)
        })
        .catch(function (err) {
          setError('Registration failed: ' + err.message)
        })
        .finally(function () {
          setLoading(false)
        })
    }
  }

  return (
    <div className="login-screen">
      <div className="login-box">
        <h1>Task Scheduling Engine</h1>
        <p className="login-subtitle">
          {mode === 'login' ? 'Sign in to your console' : 'Create a new account'}
        </p>

        <form onSubmit={handleSubmit}>
          <label>Username</label>
          <input value={username} onChange={function (e) { setUsername(e.target.value) }} placeholder="username" />

          <label>Password</label>
          <input type="password" value={password} onChange={function (e) { setPassword(e.target.value) }} placeholder="password" />

          <button type="submit" className="btn-primary" disabled={loading}>
            {mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        {error && (
          <div className="report-box" style={{ borderColor: '#C4534B', color: '#C4534B', marginTop: '16px' }}>
            {error}
          </div>
        )}

        <div className="login-switch">
          {mode === 'login' ? (
            <span>
              No account yet?{' '}
              <a onClick={function () { setMode('register'); setError(null) }}>Register</a>
            </span>
          ) : (
            <span>
              Already have an account?{' '}
              <a onClick={function () { setMode('login'); setError(null) }}>Sign In</a>
            </span>
          )}
        </div>
      </div>
    </div>
  )
}