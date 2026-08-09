const BASE_URL = 'http://127.0.0.1:8000'

async function request(path, options) {
  if (!options) {
    options = {}
  }
  const headers = { 'Content-Type': 'application/json' }
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
  listTasks: function () {
    return request('/tasks')
  },
  createTask: function (task) {
    return request('/tasks', { method: 'POST', body: JSON.stringify(task) })
  },
  deleteTask: function (id) {
    return request('/tasks/' + id, { method: 'DELETE' })
  },
  runSchedule: function (context) {
    return request('/schedule/run', { method: 'POST', body: JSON.stringify(context) })
  },
  dynamicAdd: function (newTask, context) {
    return request('/schedule/dynamic-add', {
      method: 'POST',
      body: JSON.stringify({ new_task: newTask, context: context }),
    })
  },
}