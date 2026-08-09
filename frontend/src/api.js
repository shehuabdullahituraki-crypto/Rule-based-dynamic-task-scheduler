const BASE_URL = 'http://127.0.0.1:8000'

async function request(path, options, token) {
  if (!options) {
    options = {}
  }
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = 'Bearer ' + token
  }
  const res = await fetch(BASE_URL + path, {
    headers: headers,
    method: options.method,
    body: options.body,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(res.status + ': ' + body)
  }
  return res.json()
}

export const api = {
  register: function (username, password) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username: username, password: password }),
    })
  },
  login: function (username, password) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: username, password: password }),
    })
  },
  listTasks: function (token) {
    return request('/tasks', {}, token)
  },
  createTask: function (task, token) {
    return request('/tasks', { method: 'POST', body: JSON.stringify(task) }, token)
  },
  deleteTask: function (id, token) {
    return request('/tasks/' + id, { method: 'DELETE' }, token)
  },
  runSchedule: function (context, token) {
    return request('/schedule/run', { method: 'POST', body: JSON.stringify(context) }, token)
  },
  dynamicAdd: function (newTask, context, token) {
    return request('/schedule/dynamic-add', {
      method: 'POST',
      body: JSON.stringify({ new_task: newTask, context: context }),
    }, token)
  },
  adminListTasks: function (token) {
    return request('/admin/tasks', {}, token)
  },
  adminListUsers: function (token) {
    return request('/admin/users', {}, token)
  },
}