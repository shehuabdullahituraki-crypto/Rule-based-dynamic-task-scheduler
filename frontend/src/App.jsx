import React, { useState, useEffect, useCallback } from 'react'
import { api } from './api'

const CATEGORIES = ['urgent', 'routine', 'maintenance', 'project', 'admin']
const STATUS_PILL = {
  scheduled: 'pill-scheduled',
  pending: 'pill-pending',
  replaced: 'pill-replaced',
  missed: 'pill-missed',
  completed: 'pill-completed',
}

function emptyForm() {
  return {
    id: '', name: '', category: 'urgent', deadline: '',
    value: 0, penalty_if_missed: 0,
    effort_hours: 1, budget_required: 0, risk: 1,
  }
}

function emptyUrgent() {
  return {
    id: '', name: '', category: 'urgent', deadline: '',
    value: 0, penalty_if_missed: 0,
    effort_hours: 1, budget_required: 0, risk: 5,
  }
}

export default function App() {
  const [tasks, setTasks] = useState([])
  const [availableHours, setAvailableHours] = useState(8)
  const [availableBudget, setAvailableBudget] = useState(2000)
  const [form, setForm] = useState(emptyForm())
  const [urgentForm, setUrgentForm] = useState(emptyUrgent())
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)
const [error, setError] = useState(null)
  const [successMsg, setSuccessMsg] = useState(null)
  const [connected, setConnected] = useState(false)

  const refresh = useCallback(function () {
    api.listTasks()
      .then(function (list) {
        setTasks(list)
        setConnected(true)
        setError(null)
      })
      .catch(function () {
        setConnected(false)
        setError('Cannot reach backend API - is uvicorn running on port 8000?')
      })
  }, [])

  useEffect(function () {
    refresh()
  }, [refresh])

 function handleCreateTask(e) {
    e.preventDefault()
    if (!form.id || !form.name || !form.deadline) {
      return
    }
    setLoading(true)
    setError(null)
    setSuccessMsg(null)
    api.createTask(form)
      .then(function () {
        setForm(emptyForm())
        setSuccessMsg('Task "' + form.id + '" added successfully.')
        setTimeout(function () {
          setSuccessMsg(null)
        }, 2500)
        refresh()
      })
      .catch(function (err) {
        setError(err.message)
      })
      .finally(function () {
        setLoading(false)
      })
  }

 function handleDelete(id) {
    const confirmed = window.confirm('Delete task "' + id + '"? This cannot be undone.')
    if (!confirmed) {
      return
    }
    api.deleteTask(id).then(refresh)
  }

  function handleRunSchedule() {
    setLoading(true)
    setReport(null)
    const context = {
      available_hours: Number(availableHours),
      available_budget: Number(availableBudget),
    }
    api.runSchedule(context)
      .then(function () {
        refresh()
      })
      .catch(function (err) {
        setError(err.message)
      })
      .finally(function () {
        setLoading(false)
      })
  }

  function handleDynamicAdd(e) {
    e.preventDefault()
    if (!urgentForm.id || !urgentForm.name || !urgentForm.deadline) {
      return
    }
    setLoading(true)
    const context = {
      available_hours: Number(availableHours),
      available_budget: Number(availableBudget),
    }
    api.dynamicAdd(urgentForm, context)
      .then(function (rep) {
        setReport(rep)
        setUrgentForm(emptyUrgent())
        return refresh()
      })
      .catch(function (err) {
        setError(err.message)
      })
      .finally(function () {
        setLoading(false)
      })
  }

  const ranked = tasks.slice().sort(function (a, b) {
    return (b.score || 0) - (a.score || 0)
  })

  return (
    <div className="console">
      <div className="header">
        <h1>Task Scheduling Engine // Console</h1>
        <div className="status">
          <span
            className="status-dot"
            style={{ background: connected ? '#6FA98A' : '#C4534B' }}
          ></span>
          {connected ? 'API connected' : 'API offline'}
        </div>
      </div>

      <div className="panel">
        <div className="section-title">Register Task</div>
        <form onSubmit={handleCreateTask}>
          <label>Task ID</label>
          <input value={form.id} onChange={function (e) { setForm({ ...form, id: e.target.value }) }} placeholder="T1" />

          <label>Name</label>
          <input value={form.name} onChange={function (e) { setForm({ ...form, name: e.target.value }) }} placeholder="Submit report" />

          <label>Category</label>
          <select value={form.category} onChange={function (e) { setForm({ ...form, category: e.target.value }) }}>
            {CATEGORIES.map(function (c) {
              return <option key={c} value={c}>{c}</option>
            })}
          </select>

          <label>Deadline</label>
          <input type="date" value={form.deadline} onChange={function (e) { setForm({ ...form, deadline: e.target.value }) }} />

          <div className="row-2">
            <div>
              <label>Value gained</label>
              <input type="number" value={form.value} onChange={function (e) { setForm({ ...form, value: e.target.value }) }} />
            </div>
            <div>
              <label>Penalty if missed</label>
              <input type="number" value={form.penalty_if_missed} onChange={function (e) { setForm({ ...form, penalty_if_missed: e.target.value }) }} />
            </div>
          </div>

          <div className="row-2">
            <div>
              <label>Effort (hrs)</label>
              <input type="number" value={form.effort_hours} onChange={function (e) { setForm({ ...form, effort_hours: e.target.value }) }} />
            </div>
            <div>
              <label>Budget required</label>
              <input type="number" value={form.budget_required} onChange={function (e) { setForm({ ...form, budget_required: e.target.value }) }} />
            </div>
          </div>

          <label>Risk (1-5)</label>
          <input type="number" min="1" max="5" value={form.risk} onChange={function (e) { setForm({ ...form, risk: e.target.value }) }} />

          <button type="submit" className="btn-primary" disabled={loading}>+ Add Task</button>
        </form>

        <hr className="divider" />

        <div className="section-title">Resource Capacity</div>
        <label>Available hours</label>
        <input type="number" value={availableHours} onChange={function (e) { setAvailableHours(e.target.value) }} />
        <label>Available budget</label>
        <input type="number" value={availableBudget} onChange={function (e) { setAvailableBudget(e.target.value) }} />
        <button className="btn-secondary" onClick={handleRunSchedule} disabled={loading}>
          Run Scheduling Cycle
        </button>

        <hr className="divider" />

        <div className="section-title" style={{ color: '#C4534B' }}>Simulate Urgent Task</div>
        <form onSubmit={handleDynamicAdd}>
          <label>Task ID</label>
          <input value={urgentForm.id} onChange={function (e) { setUrgentForm({ ...urgentForm, id: e.target.value }) }} placeholder="T-URGENT" />
          <label>Name</label>
          <input value={urgentForm.name} onChange={function (e) { setUrgentForm({ ...urgentForm, name: e.target.value }) }} placeholder="Critical patch" />
          <label>Category</label>
          <select value={urgentForm.category} onChange={function (e) { setUrgentForm({ ...urgentForm, category: e.target.value }) }}>
            {CATEGORIES.map(function (c) {
              return <option key={c} value={c}>{c}</option>
            })}
          </select>
          <label>Deadline</label>
          <input type="date" value={urgentForm.deadline} onChange={function (e) { setUrgentForm({ ...urgentForm, deadline: e.target.value }) }} />
          <label>Penalty if missed</label>
          <input type="number" value={urgentForm.penalty_if_missed} onChange={function (e) { setUrgentForm({ ...urgentForm, penalty_if_missed: e.target.value }) }} />
          <label>Effort (hrs)</label>
          <input type="number" value={urgentForm.effort_hours} onChange={function (e) { setUrgentForm({ ...urgentForm, effort_hours: e.target.value }) }} />
          <label>Risk (1-5)</label>
          <input type="number" min="1" max="5" value={urgentForm.risk} onChange={function (e) { setUrgentForm({ ...urgentForm, risk: e.target.value }) }} />
          <button type="submit" className="btn-danger" style={{ width: '100%' }} disabled={loading}>
            Inject &amp; Reallocate
          </button>
        </form>

        {report && (
          <div className="report-box">
            <div>action: <span className="action">{report.action}</span></div>
            {report.replaced && report.replaced.length > 0 && (
              <div>
                bumped:{' '}
                {report.replaced.map(function (id) {
                  return <span key={id} className="replaced-id">{id} </span>
                })}
              </div>
            )}
          </div>
        )}

{successMsg && (
          <div className="toast">
            {successMsg}
          </div>
        )}
       {error && (
          <div className="report-box" style={{ borderColor: '#C4534B', color: '#C4534B' }}>
            {error}
          </div>
        )}
      </div>

      <div className="panel">
        <div className="section-title">Ranked Task Queue ({ranked.length})</div>
        {ranked.length === 0 && (
          <div className="empty-state">No tasks registered yet. Add one on the left, then run a scheduling cycle.</div>
        )}
        {ranked.map(function (t, i) {
          const scorePercent = Math.min(100, Math.round((t.score || 0) * 100))
          return (
            <div key={t.id}>
              <div className="task-row">
                <div className="rank-badge">#{t.rank || (i + 1)}</div>
                <div>
                  <div className="task-name">{t.name}</div>
                  <div className="task-meta">{t.id} - {t.category} - due {t.deadline}</div>
                </div>
                <div>
                  <span className={'pill ' + (STATUS_PILL[t.status] || 'pill-pending')}>{t.status}</span>
                </div>
                <div>
                  <div className="score-bar-track">
                    <div className="score-bar-fill" style={{ width: scorePercent + '%' }}></div>
                  </div>
                  <div className="score-label">{scorePercent}%</div>
                </div>
                <div className="task-meta">
                  {t.effort_hours}h - {t.budget_required > 0 ? ('$' + t.budget_required) : '-'}
                </div>
                <button className="icon-btn" onClick={function () { handleDelete(t.id) }} title="Delete task">X</button>
              </div>
              {t.rule_log && t.rule_log.length > 0 && (
                <div className="rule-log">
                  {t.rule_log.map(function (log, idx) {
                    return <div key={idx}>{log}</div>
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}