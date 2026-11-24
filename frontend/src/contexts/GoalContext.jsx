import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../firebase'
import { listGoals, createGoal, updateGoal, deleteGoal } from '../services/api'

const GoalContext = createContext(null)

export const GoalProvider = ({ children }) => {
  const [userId, setUserId] = useState(null)
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      const uid = user?.uid || localStorage.getItem('levelup_guest_user_id') || 'guest_user'
      setUserId(uid)
      setLoading(true)
      try {
        const items = await listGoals(uid)
        setGoals(items)
      } catch (e) {
        console.warn('Failed to load goals:', e)
      } finally {
        setLoading(false)
      }
    })
    return () => unsubscribe()
  }, [])

  const addGoal = useCallback(async (data) => {
    const uid = userId || auth.currentUser?.uid || 'guest_user'
    const item = await createGoal(data, uid)
    setGoals(prev => [...prev, item])
    return item
  }, [userId])

  const editGoal = useCallback(async (id, data) => {
    const uid = userId || auth.currentUser?.uid || 'guest_user'
    const item = await updateGoal(id, data, uid)
    setGoals(prev => prev.map(g => g.id === id ? { ...g, ...item } : g))
    return item
  }, [userId])

  const removeGoal = useCallback(async (id) => {
    const uid = userId || auth.currentUser?.uid || 'guest_user'
    await deleteGoal(id, uid)
    setGoals(prev => prev.filter(g => g.id !== id))
  }, [userId])

  const stats = useMemo(() => {
    const active = goals.filter(g => g.status === 'ACTIVE').length
    const completed = goals.filter(g => g.status === 'COMPLETED').length
    return { active, completed, total: goals.length }
  }, [goals])

  const value = { goals, loading, stats, addGoal, editGoal, removeGoal }

  return <GoalContext.Provider value={value}>{children}</GoalContext.Provider>
}

export const useGoals = () => {
  const context = useContext(GoalContext)
  if (!context) throw new Error('useGoals must be used within a GoalProvider')
  return context
}
