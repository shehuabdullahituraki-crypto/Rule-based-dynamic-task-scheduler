import React, { useState } from 'react'
import { api } from './api'

export default function Login({ onLoginSuccess }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [resetCode, setResetCode] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState(null)
  const [infoMsg, setInfoMsg] = useState(null)
  const [loading, setLoading] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setInfoMsg(null)

    if (mode === 'login') {
      if (!username || !password) {
        setError('Please fill in both fields.')
        return
      }
      setLoading(true)
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
    } else if (mode === 'register') {
      if (!username || !email || !password) {
        setError('Please fill in all fields.')
        return
      }
      setLoading(true)
      api.register(username, email, password)
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
    } else if (mode === 'forgot') {
      if (!email) {
        setError('Please enter your email.')
        return
      }
      setLoading(true)
      api.forgotPassword(email)
        .then(function () {
          setInfoMsg('If that email is registered, a reset code has been sent. Check your inbox.')
          setMode('reset')
        })
        .catch(function (err) {
          setError('Request failed: ' + err.message)
        })
        .finally(function () {
          setLoading(false)
        })
    } else if (mode === 'reset') {
      if (!email || !resetCode || !newPassword) {
        setError('Please fill in the code and new password.')
        return
      }
      setLoading(true)
      api.resetPassword(email, resetCode, newPassword)
        .then(function () {
          setInfoMsg('Password reset successful. You can now sign in.')
          setMode('login')
          setPassword('')
          setResetCode('')
          setNewPassword('')
        })
        .catch(function (err) {
          setError('Reset failed: ' + err.message)
        })
        .finally(function () {
          setLoading(false)
        })
    }
  }

  function switchMode(newMode) {
    setMode(newMode)
    setError(null)
    setInfoMsg(null)
  }

  return (
    <div className="login-screen">
      <div className="login-box">
        <h1>Task Scheduling Engine</h1>
        <p className="login-subtitle">
          {mode === 'login' && 'Sign in to your console'}
          {mode === 'register' && 'Create a new account'}
          {mode === 'forgot' && 'Reset your password'}
          {mode === 'reset' && 'Enter the code sent to your email'}
        </p>

        <form onSubmit={handleSubmit}>
          {mode === 'login' && (
            <React.Fragment>
              <label>Username</label>
              <input value={username} onChange={function (e) { setUsername(e.target.value) }} placeholder="username" />
              <label>Password</label>
              <input type="password" value={password} onChange={function (e) { setPassword(e.target.value) }} placeholder="password" />
            </React.Fragment>
          )}

          {mode === 'register' && (
            <React.Fragment>
              <label>Username</label>
              <input value={username} onChange={function (e) { setUsername(e.target.value) }} placeholder="username" />
              <label>Email</label>
              <input type="email" value={email} onChange={function (e) { setEmail(e.target.value) }} placeholder="you@example.com" />
              <label>Password</label>
              <input type="password" value={password} onChange={function (e) { setPassword(e.target.value) }} placeholder="password" />
            </React.Fragment>
          )}

          {mode === 'forgot' && (
            <React.Fragment>
              <label>Email</label>
              <input type="email" value={email} onChange={function (e) { setEmail(e.target.value) }} placeholder="you@example.com" />
            </React.Fragment>
          )}

          {mode === 'reset' && (
            <React.Fragment>
              <label>Email</label>
              <input type="email" value={email} onChange={function (e) { setEmail(e.target.value) }} placeholder="you@example.com" />
              <label>6-Digit Code</label>
              <input value={resetCode} onChange={function (e) { setResetCode(e.target.value) }} placeholder="123456" />
              <label>New Password</label>
              <input type="password" value={newPassword} onChange={function (e) { setNewPassword(e.target.value) }} placeholder="new password" />
            </React.Fragment>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {mode === 'login' && 'Sign In'}
            {mode === 'register' && 'Create Account'}
            {mode === 'forgot' && 'Send Reset Code'}
            {mode === 'reset' && 'Reset Password'}
          </button>
        </form>

        {infoMsg && (
          <div className="report-box" style={{ borderColor: '#6FA98A', color: '#6FA98A', marginTop: '16px' }}>
            {infoMsg}
          </div>
        )}
        {error && (
          <div className="report-box" style={{ borderColor: '#C4534B', color: '#C4534B', marginTop: '16px' }}>
            {error}
          </div>
        )}

        <div className="login-switch">
          {mode === 'login' && (
            <span>
              No account yet? <a onClick={function () { switchMode('register') }}>Register</a>
              {' '}|{' '}
              <a onClick={function () { switchMode('forgot') }}>Forgot password?</a>
            </span>
          )}
          {mode === 'register' && (
            <span>Already have an account? <a onClick={function () { switchMode('login') }}>Sign In</a></span>
          )}
          {(mode === 'forgot' || mode === 'reset') && (
            <span>Remembered your password? <a onClick={function () { switchMode('login') }}>Sign In</a></span>
          )}
        </div>
      </div>
    </div>
  )
}