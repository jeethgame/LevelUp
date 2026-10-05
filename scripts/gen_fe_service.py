import os

os.makedirs("frontend/src/services", exist_ok=True)
os.makedirs("frontend/src/components/learning", exist_ok=True)
os.makedirs("frontend/src/pages", exist_ok=True)

# 1. recommenderService.js
recommender_service_js = """import axios from 'axios'
import { auth } from '../firebase'

const API_URL = import.meta.env.VITE_API_URL || ''

const client = axios.create({
  baseURL: API_URL,
})

const withAuth = async () => {
  try {
    const token = await auth.currentUser?.getIdToken()
    if (token) {
      return { headers: { Authorization: `Bearer ${token}` } }
    }
  } catch (e) {
    console.warn('Auth token retrieval failed:', e)
  }
  return {}
}

export const generateConversationalPlan = async (goal, profile = {}) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/conversational-plan', { goal, profile }, config)
  return data
}

export const explainRecommendation = async (payload) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/explain', payload, config)
  return data
}

export const adaptRoadmap = async (payload) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/adapt', payload, config)
  return data
}

export const sendMilestoneChatMessage = async (payload) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/chat', payload, config)
  return data
}

export const generateDiagnosticQuiz = async (skillName, difficulty = 'intermediate') => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/diagnostic-quiz', { skill_name: skillName, difficulty }, config)
  return data
}

export const generateProjectSpec = async (payload) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/generate-project', payload, config)
  return data
}

export const validateCheckpoint = async (payload) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/validate-checkpoint', payload, config)
  return data
}

export const adoptRecommendedRoadmap = async (roadmap) => {
  const config = await withAuth()
  const { data } = await client.post('/api/v1/recommend/adopt', { roadmap }, config)
  return data
}
"""

with open("frontend/src/services/recommenderService.js", "w", encoding="utf-8") as f:
    f.write(recommender_service_js)
print("recommenderService.js created")
