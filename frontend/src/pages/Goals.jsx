import React, { useState } from 'react'
import { AppShell } from '../components/layout/AppShell'
import { PageHeader } from '../components/ui/PageHeader'
import {
  Target, Zap, Briefcase, Map, ArrowRight, Plus, Trash2,
  CheckCircle2, Clock, Edit3, X, ChevronDown, ChevronUp
} from 'lucide-react'
import { skillGap, pathOptimize } from '../services/aiService'
import { useSkills } from '../contexts/SkillContext'
import { useGoals } from '../contexts/GoalContext'
import { useNavigate } from 'react-router-dom'

const Goals = () => {
  const { skills } = useSkills()
  const { goals, loading, addGoal, editGoal, removeGoal } = useGoals()
  const navigate = useNavigate()

  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({ title: '', targetRole: '', deadline: '', notes: '' })
  const [expandedGoal, setExpandedGoal] = useState(null)
  const [analyzing, setAnalyzing] = useState(null)
  const [analysisResults, setAnalysisResults] = useState({})

  const resetForm = () => {
    setForm({ title: '', targetRole: '', deadline: '', notes: '' })
    setEditingId(null)
    setShowForm(false)
  }

  const handleSave = async () => {
    if (!form.title.trim()) return
    if (editingId) {
      await editGoal(editingId, form)
    } else {
      await addGoal(form)
    }
    resetForm()
  }

  const startEdit = (goal) => {
    setForm({ title: goal.title, targetRole: goal.targetRole, deadline: goal.deadline, notes: goal.notes })
    setEditingId(goal.id)
    setShowForm(true)
  }

  const toggleComplete = async (goal) => {
    await editGoal(goal.id, { ...goal, status: goal.status === 'COMPLETED' ? 'ACTIVE' : 'COMPLETED' })
  }

  const runAnalysis = async (goal) => {
    setAnalyzing(goal.id)
    setExpandedGoal(goal.id)
    try {
      const data = await skillGap({ targetRole: goal.targetRole || goal.title, skills })
      setAnalysisResults(prev => ({ ...prev, [goal.id]: data }))
    } finally {
      setAnalyzing(null)
    }
  }

  const activeGoals = goals.filter(g => g.status === 'ACTIVE')
  const completedGoals = goals.filter(g => g.status === 'COMPLETED')

  return (
    <AppShell>
      <div className="page-container animate-fade-slide-in">
        <PageHeader
          title="Goals & Career Path"
          subtitle={`${activeGoals.length} active goal${activeGoals.length !== 1 ? 's' : ''} — define your target roles, track progress, and let AI map the gap.`}
        />

        <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
          {/* Left: Goal List + Add */}
          <div className="space-y-4">
            {/* Add Goal Button / Form */}
            {showForm ? (
              <div className="card-surface p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-foreground">{editingId ? 'Edit Goal' : 'New Goal'}</h3>
                  <button onClick={resetForm} className="p-1.5 rounded-xl hover:bg-secondary text-muted-foreground"><X className="w-4 h-4" /></button>
                </div>
                <div>
                  <label className="label-base">Goal Title</label>
                  <input className="input-base rounded-2xl" placeholder="e.g. Land a Senior Frontend role at a FAANG company" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
                </div>
                <div>
                  <label className="label-base">Target Role</label>
                  <div className="relative">
                    <Briefcase className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                    <input className="input-base pl-9 rounded-2xl" placeholder="e.g. Senior Frontend Engineer" value={form.targetRole} onChange={e => setForm(f => ({ ...f, targetRole: e.target.value }))} />
                  </div>
                </div>
                <div>
                  <label className="label-base">Target Date (optional)</label>
                  <input type="date" className="input-base rounded-2xl" value={form.deadline} onChange={e => setForm(f => ({ ...f, deadline: e.target.value }))} />
                </div>
                <div>
                  <label className="label-base">Notes (optional)</label>
                  <textarea className="input-base rounded-2xl" rows={2} placeholder="Why this goal matters to you..." value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} />
                </div>
                <button onClick={handleSave} disabled={!form.title.trim()} className="w-full py-2.5 rounded-2xl bg-orange-600 hover:bg-orange-700 text-white font-bold text-sm transition-all disabled:opacity-40">
                  {editingId ? 'Save Changes' : 'Add Goal'}
                </button>
              </div>
            ) : (
              <button onClick={() => setShowForm(true)} className="w-full py-3 rounded-2xl border-2 border-dashed border-border hover:border-orange-500/50 text-muted-foreground hover:text-orange-600 font-semibold text-sm flex items-center justify-center gap-2 transition-all">
                <Plus className="w-4 h-4" /> Add Career Goal
              </button>
            )}

            {/* Active Goals */}
            {loading ? (
              <div className="card-surface p-8 flex items-center justify-center">
                <div className="w-6 h-6 rounded-full border-2 border-orange-600 border-t-transparent animate-spin" />
              </div>
            ) : activeGoals.length === 0 && completedGoals.length === 0 ? (
              <div className="card-surface p-8 text-center">
                <Target className="w-10 h-10 text-orange-500/40 mx-auto mb-3" />
                <p className="text-sm font-medium text-foreground mb-1">No goals yet</p>
                <p className="text-xs text-muted-foreground">Add your first career goal to get started with AI-powered gap analysis.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activeGoals.map(goal => (
                  <div key={goal.id} className="card-surface overflow-hidden">
                    <div className="p-4">
                      <div className="flex items-start gap-3">
                        <button onClick={() => toggleComplete(goal)} className="check-box shrink-0 mt-0.5" role="checkbox" aria-checked="false">
                        </button>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-foreground truncate">{goal.title}</p>
                          {goal.targetRole && <p className="text-xs text-muted-foreground mt-0.5">{goal.targetRole}</p>}
                          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                            {goal.deadline && (
                              <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{goal.deadline}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <button onClick={() => runAnalysis(goal)} disabled={analyzing === goal.id} className="p-1.5 rounded-xl hover:bg-orange-500/10 text-orange-600 dark:text-orange-400 transition-colors" title="Analyze skill gap">
                            {analyzing === goal.id ? <div className="w-4 h-4 rounded-full border-2 border-orange-600 border-t-transparent animate-spin" /> : <Zap className="w-4 h-4" />}
                          </button>
                          <button onClick={() => startEdit(goal)} className="p-1.5 rounded-xl hover:bg-secondary text-muted-foreground"><Edit3 className="w-3.5 h-3.5" /></button>
                          <button onClick={() => removeGoal(goal.id)} className="p-1.5 rounded-xl hover:bg-red-500/10 text-red-500"><Trash2 className="w-3.5 h-3.5" /></button>
                          <button onClick={() => setExpandedGoal(expandedGoal === goal.id ? null : goal.id)} className="p-1.5 rounded-xl hover:bg-secondary text-muted-foreground">
                            {expandedGoal === goal.id ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      </div>
                    </div>

                    {expandedGoal === goal.id && (
                      <div className="px-4 pb-4 pt-0 border-t border-border mt-0">
                        {goal.notes && <p className="text-xs text-muted-foreground mt-3 mb-2">{goal.notes}</p>}
                        {analysisResults[goal.id] && (
                          <div className="mt-3 p-3 rounded-xl bg-secondary/50 space-y-2">
                            <p className="text-xs font-bold text-foreground">AI Skill Gap Analysis</p>
                            {analysisResults[goal.id].missingSkills?.length > 0 && (
                              <div>
                                <p className="text-[11px] font-semibold text-muted-foreground mb-1">Missing Skills:</p>
                                <div className="flex flex-wrap gap-1.5">
                                  {analysisResults[goal.id].missingSkills.map((s, i) => (
                                    <span key={i} className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">{s}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {analysisResults[goal.id].learningOrder?.length > 0 && (
                              <div>
                                <p className="text-[11px] font-semibold text-muted-foreground mb-1">Recommended Order:</p>
                                <ol className="text-xs text-foreground space-y-0.5 list-decimal list-inside">
                                  {analysisResults[goal.id].learningOrder.map((s, i) => <li key={i}>{s}</li>)}
                                </ol>
                              </div>
                            )}
                          </div>
                        )}
                        {!analysisResults[goal.id] && (
                          <button onClick={() => runAnalysis(goal)} disabled={analyzing === goal.id} className="mt-3 text-xs font-semibold text-orange-600 dark:text-orange-400 hover:underline flex items-center gap-1">
                            <Zap className="w-3.5 h-3.5" /> Run AI Skill Gap Analysis
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {completedGoals.length > 0 && (
                  <>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider pt-3">Completed</p>
                    {completedGoals.map(goal => (
                      <div key={goal.id} className="card-surface p-4 opacity-60">
                        <div className="flex items-center gap-3">
                          <button onClick={() => toggleComplete(goal)} className="check-box checked shrink-0" role="checkbox" aria-checked="true">
                            <CheckCircle2 className="w-3 h-3 text-white" />
                          </button>
                          <p className="text-sm font-medium text-foreground line-through truncate">{goal.title}</p>
                          <button onClick={() => removeGoal(goal.id)} className="ml-auto p-1.5 rounded-xl hover:bg-red-500/10 text-red-500 shrink-0"><Trash2 className="w-3.5 h-3.5" /></button>
                        </div>
                      </div>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>

          {/* Right: Quick Actions + Upsell */}
          <div className="space-y-6">
            <div className="card-surface p-6">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/10 flex items-center justify-center mb-5 border border-amber-500/20">
                <Map className="w-6 h-6 text-amber-600 dark:text-amber-400" />
              </div>
              <h2 className="text-xl font-bold text-foreground mb-2 font-serif italic">Optimize Path</h2>
              <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                AI analyzes your {skills.filter(s => s.status !== 'COMPLETED').length} active skills and suggests the most efficient learning order.
              </p>
              <button
                onClick={async () => {
                  const data = await pathOptimize({ selectedSkills: skills.filter(s => s.status !== 'COMPLETED') })
                  setAnalysisResults(prev => ({ ...prev, _pathOptimize: data }))
                }}
                disabled={skills.length === 0}
                className="w-full py-3 rounded-2xl bg-secondary hover:bg-secondary/80 text-foreground font-bold text-sm border border-border transition-all disabled:opacity-40"
              >
                Optimize Learning Path
              </button>

              {analysisResults._pathOptimize?.recommendedOrder && (
                <div className="mt-4 p-3 rounded-xl bg-secondary/50">
                  <p className="text-xs font-bold text-foreground mb-2">Recommended Order</p>
                  <ol className="text-xs text-foreground space-y-1 list-decimal list-inside">
                    {analysisResults._pathOptimize.recommendedOrder.map((s, i) => <li key={i}>{s}</li>)}
                  </ol>
                </div>
              )}
            </div>

            <div className="relative overflow-hidden rounded-xl p-6 bg-zinc-950 border border-zinc-800">
              <div className="relative z-10">
                <div className="flex items-center gap-2 mb-2 text-white">
                  <Zap className="w-5 h-5 text-orange-400" />
                  <h3 className="font-bold">Deep Resume Analysis</h3>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  Upload your resume and a specific Job Description for a highly tailored skill gap report.
                </p>
                <button
                  onClick={() => navigate('/skill-gap')}
                  className="text-xs font-bold text-orange-600 dark:text-orange-400 hover:underline flex items-center gap-1 transition-colors"
                >
                  Go to Analyzer <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  )
}

export default Goals
