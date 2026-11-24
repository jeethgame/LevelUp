import axios from 'axios'
import { auth } from '../firebase'

const getBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL
  if (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    return 'http://localhost:8000'
  }
  return 'https://levelup-new-backend.onrender.com'
}

const client = axios.create({
  baseURL: getBaseUrl(),
})


const withAuth = async () => {
  try {
    const token = await auth.currentUser?.getIdToken()
    if (token) {
      return {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    }
  } catch (e) {
    console.warn('Could not fetch token:', e)
  }
  return { headers: {} }
}

const post = async (path, payload) => {
  const config = await withAuth()
  const { data } = await client.post(path, payload, config)
  return data
}

export const generateSubskills = (payload) => post('/ai/generate-subskills', payload)
export const progressInsights = (payload) => post('/ai/progress-insights', payload)
export const prioritySuggestions = (payload) => post('/ai/priority-suggestions', payload)
export const taskPlan = (payload) => post('/ai/task-plan', payload)
export const skillGap = (payload) => post('/ai/skill-gap', payload)
export const pathOptimize = (payload) => post('/ai/path-optimize', payload)
export const timeEstimate = (payload) => post('/ai/time-estimate', payload)
export const weeklyReport = (payload) => post('/ai/weekly-report', payload)
export const runOnboarding = (payload) => post('/ai/onboard', payload)
export const sendChatMessage = (payload) => post('/ai/chat', payload)
export const autoOrganizeTasks = (payload) => post('/ai/auto-organize-tasks', payload)

export const streamChatMessage = async (payload, { onToken, onToolCall, onDone, onError }) => {
  const baseUrl = getBaseUrl()
  let headers = { 'Content-Type': 'application/json' }
  try {
    const token = await auth.currentUser?.getIdToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  } catch {}

  try {
    const res = await fetch(`${baseUrl}/ai/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const event = JSON.parse(line.slice(6))
          if (event.type === 'token' && onToken) onToken(event.content)
          else if (event.type === 'tool_call' && onToolCall) onToolCall(event.action)
          else if (event.type === 'done' && onDone) onDone(event)
        } catch {}
      }
    }
  } catch (err) {
    if (onError) onError(err)
  }
}
