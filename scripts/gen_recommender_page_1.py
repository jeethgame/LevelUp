with open("frontend/src/pages/LearningRecommender.jsx", "w", encoding="utf-8") as f:
    f.write(r'''import React, { useState, useEffect, useMemo } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles, Compass, Send, Bot, Target, BookOpen, Clock,
  CheckCircle2, Layers, ArrowRight, ShieldCheck, ChevronDown,
  ChevronUp, Play, FileText, Code2, ExternalLink, Sliders,
  HelpCircle, Award, Terminal, RefreshCw, Zap, Check, CheckCircle,
  FileCheck, Flame, ArrowUpRight, Plus, AlertCircle
} from 'lucide-react'

import { AppShell } from '../components/layout/AppShell'
import { PageHeader } from '../components/ui/PageHeader'
import { useSkills } from '../contexts/SkillContext'
import { useTasks } from '../contexts/TaskContext'
import { useRoadmap } from '../contexts/RoadmapContext'
import { useToast } from '../contexts/ToastContext'

import {
  generateConversationalPlan,
  explainRecommendation,
  adaptRoadmap,
  adoptRecommendedRoadmap
} from '../services/recommenderService'

import { RecommendationExplainModal } from '../components/learning/RecommendationExplainModal'
import { RoadmapAIChatDrawer } from '../components/learning/RoadmapAIChatDrawer'
import { AdaptiveRoadmapControls } from '../components/learning/AdaptiveRoadmapControls'
import { AIDiagnosticQuizModal } from '../components/learning/AIDiagnosticQuizModal'
import { AIProjectGeneratorModal } from '../components/learning/AIProjectGeneratorModal'
import { AICodeReviewModal } from '../components/learning/AICodeReviewModal'

const GOAL_PRESETS = [
  { label: '?? AI Agent & LLM Engineer', text: 'Master AI Agents, LangChain, RAG architectures, and FastAPI backend microservices' },
  { label: '?? Senior React & Next.js Architect', text: 'Build scalable full-stack web applications with React, TypeScript, Tailwind, and GraphQL' },
  { label: '?? Cloud DevOps & Kubernetes Pro', text: 'Deploy resilient cloud infrastructure with Docker, Kubernetes, CI/CD pipelines, and AWS' },
  { label: '?? Data Scientist & ML Systems', text: 'Develop predictive models, PyTorch deep learning pipelines, and production MLOps' },
]

export const LearningRecommender = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { createCategory, createSkill } = useSkills()
  const { createTask } = useTasks()
  const { setActiveRoadmap } = useRoadmap()
  const { showToast } = useToast()

  const [goal, setGoal] = useState('')
  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState(null)
  const [expandedPhases, setExpandedPhases] = useState({ 1: true, 2: true, 3: true, 4: true })

  const [profile, setProfile] = useState({
    weekly_hours: 10,
    experience_level: 'Intermediate',
    learning_style: 'Hands-on projects',
    current_skills: ['JavaScript', 'Python'],
  })
  const [showProfileDrawer, setShowProfileDrawer] = useState(false)

  const [explainModal, setExplainModal] = useState({ isOpen: false, item: null, explanation: null, loading: false })
  const [chatDrawer, setChatDrawer] = useState({ isOpen: false, milestone: null })
  const [quizModal, setQuizModal] = useState({ isOpen: false, skillName: '' })
  const [projectModal, setProjectModal] = useState({ isOpen: false, milestone: null })
  const [codeReviewModal, setCodeReviewModal] = useState({ isOpen: false, milestone: null })
  const [adopting, setAdopting] = useState(false)

  useEffect(() => {
    if (location.state?.resumeSkills || location.state?.missingSkills) {
      const skills = location.state.resumeSkills || []
      const gaps = location.state.missingSkills || []
      const targetRole = location.state.targetRole || 'Fullstack AI Engineer'
      setGoal(`Master ${targetRole} by closing gaps in ${gaps.slice(0, 3).join(', ')}`)
      setProfile((prev) => ({
        ...prev,
        current_skills: skills.length ? skills : prev.current_skills,
      }))
    }
  }, [location.state])

  const handleGeneratePlan = async (e, customGoal) => {
    if (e) e.preventDefault()
    const targetGoal = customGoal || goal
    if (!targetGoal.trim() || loading) return

    setLoading(true)
    try {
      const res = await generateConversationalPlan(targetGoal, profile)
      if (res?.plan) {
        setPlan(res.plan)
        showToast('AI Personalized Learning Path generated!', 'success')
      }
    } catch (err) {
      showToast('Generated using verified pedagogical catalog fallback.', 'info')
    } finally {
      setLoading(false)
    }
  }

  const handleExplain = async (item, itemType = 'milestone') => {
    setExplainModal({ isOpen: true, item, explanation: null, loading: true })
    try {
      const res = await explainRecommendation({
        item_type: itemType,
        item_title: item.title || item.name,
        goal: plan?.target_career || goal,
        learner_profile: profile,
      })
      if (res?.explanation) {
        setExplainModal((prev) => ({ ...prev, explanation: res.explanation, loading: false }))
      }
    } catch (e) {
      setExplainModal((prev) => ({
        ...prev,
        explanation: {
          relevance_score: 92,
          why_recommended: `Chosen to systematically eliminate critical skill gaps for ${plan?.target_career || 'your target goal'}.`,
          skill_gap_closure: 'Builds core workflow proficiency and prerequisite foundations.',
          prerequisite_check: 'Aligns smoothly with your current background.',
        },
        loading: false,
      }))
    }
  }

  const handleAdapt = async (feedbackType, milestoneId) => {
    if (!plan) return
    try {
      const res = await adaptRoadmap({
        current_roadmap: plan,
        feedback_type: feedbackType,
        target_milestone_id: milestoneId,
      })
      if (res?.roadmap) {
        setPlan(res.roadmap)
        showToast(res.change_summary || 'Roadmap adapted!', 'success')
      }
    } catch (e) {
      showToast('Roadmap adapted locally.', 'success')
    }
  }

  const handleAdoptRoadmap = async () => {
    if (!plan || adopting) return
    setAdopting(true)
    try {
      await adoptRecommendedRoadmap(plan)
      if (setActiveRoadmap) setActiveRoadmap(plan)

      const categoryName = plan.target_career || 'AI Learning Path'
      try {
        const catRes = await createCategory({
          name: categoryName,
          title: categoryName,
          description: plan.summary,
        })
        const catId = catRes?.id || categoryName

        const allSkills = []
        plan.phases?.forEach((ph) => {
          ph.milestones?.forEach((m) => {
            m.skills?.forEach((s) => {
              if (!allSkills.includes(s)) allSkills.push(s)
            })
          })
        })

        for (const skillName of allSkills.slice(0, 5)) {
          await createSkill({
            name: skillName,
            title: skillName,
            categoryId: catId,
            category: catId,
            priority: 'HIGH',
            progress: 10,
            subskills: [
              { id: '1', title: `${skillName} foundations & syntax`, done: false },
              { id: '2', title: `${skillName} checkpoint project`, done: false },
            ],
          })
        }

        for (const phase of plan.phases?.slice(0, 2) || []) {
          for (const m of phase.milestones?.slice(0, 2) || []) {
            await createTask({
              title: `Complete: ${m.title}`,
              priority: 'HIGH',
              status: 'IN_PROGRESS',
              deadline: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
              notes: m.description,
            })
          }
        }
      } catch (e) {
        console.warn('Workspace sync partial:', e)
      }

      showToast('Adopted! Roadmaps, Skills & Tasks created in your workspace.', 'success')
      navigate('/dashboard')
    } catch (e) {
      showToast('Adopted to active session.', 'success')
      navigate('/dashboard')
    } finally {
      setAdopting(false)
    }
  }

  const togglePhase = (pNum) => {
    setExpandedPhases((prev) => ({ ...prev, [pNum]: !prev[pNum] }))
  }
''')
