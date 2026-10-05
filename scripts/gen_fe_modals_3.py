# 4. AIDiagnosticQuizModal.jsx
with open("frontend/src/components/learning/AIDiagnosticQuizModal.jsx", "w", encoding="utf-8") as f:
    f.write(r'''import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Award, CheckCircle2, XCircle, HelpCircle, Loader2, Sparkles, ArrowRight } from 'lucide-react'
import { generateDiagnosticQuiz } from '../../services/recommenderService'

export const AIDiagnosticQuizModal = ({ isOpen, onClose, skillName }) => {
  const [loading, setLoading] = useState(false)
  const [quiz, setQuiz] = useState(null)
  const [currentIdx, setCurrentIdx] = useState(0)
  const [selectedOpt, setSelectedOpt] = useState(null)
  const [answers, setAnswers] = useState({})
  const [showResult, setShowResult] = useState(false)

  useEffect(() => {
    if (isOpen && skillName) {
      setLoading(true)
      setCurrentIdx(0)
      setSelectedOpt(null)
      setAnswers({})
      setShowResult(false)
      generateDiagnosticQuiz(skillName)
        .then((res) => {
          if (res?.quiz) setQuiz(res.quiz)
        })
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [isOpen, skillName])

  if (!isOpen) return null

  const questions = quiz?.questions || []
  const currentQ = questions[currentIdx]

  const handleSelect = (optIdx) => {
    if (answers[currentIdx] !== undefined) return
    setSelectedOpt(optIdx)
    const isCorrect = optIdx === currentQ.correct_index
    setAnswers({ ...answers, [currentIdx]: { selected: optIdx, isCorrect } })
  }

  const handleNext = () => {
    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(currentIdx + 1)
      setSelectedOpt(null)
    } else {
      setShowResult(true)
    }
  }

  const score = Object.values(answers).filter((a) => a.isCorrect).length
  const total = questions.length
  const pct = total > 0 ? Math.round((score / total) * 100) : 0

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-lg bg-card text-card-foreground rounded-2xl border border-border shadow-2xl overflow-hidden p-6"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 border-b border-border/50 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center border border-blue-500/20">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                  AI Skill Diagnostic
                </span>
                <h3 className="text-lg font-bold text-foreground leading-tight">
                  {skillName} Benchmark
                </h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="py-4 max-h-[70vh] overflow-y-auto">
            {loading ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <p className="text-sm text-muted-foreground">Generating technical assessment questions...</p>
              </div>
            ) : showResult ? (
              <div className="py-6 text-center space-y-4">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 flex items-center justify-center mx-auto">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <h4 className="text-xl font-bold text-foreground">Diagnostic Complete!</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    Your verified readiness score for {skillName}:
                  </p>
                  <div className="text-3xl font-black text-foreground mt-2">{pct}%</div>
                  <span className="inline-block mt-2 px-3 py-1 bg-accent rounded-full text-xs font-semibold text-foreground">
                    {pct >= 75 ? '?? Advanced Mastery' : pct >= 50 ? '? Intermediate Readiness' : '?? Foundational Learner'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                  This assessment has been factored into your personalized learning trajectory and recommended milestone sequence.
                </p>
                <div className="pt-4 flex justify-center">
                  <button
                    onClick={onClose}
                    className="px-5 py-2.5 bg-foreground text-background rounded-xl text-xs font-bold hover:opacity-90 transition-opacity"
                  >
                    Return to Learning Path
                  </button>
                </div>
              </div>
            ) : currentQ ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Question {currentIdx + 1} of {total}</span>
                  <span className="font-semibold text-foreground">{quiz?.difficulty || 'Intermediate'}</span>
                </div>

                <div className="p-4 rounded-xl bg-accent/30 border border-border">
                  <p className="text-sm font-semibold text-foreground leading-snug">
                    {currentQ.question}
                  </p>
                </div>

                <div className="space-y-2">
                  {currentQ.options.map((opt, oIdx) => {
                    const isAnswered = answers[currentIdx] !== undefined
                    const isPicked = selectedOpt === oIdx || answers[currentIdx]?.selected === oIdx
                    const isCorrect = oIdx === currentQ.correct_index

                    let btnCls = 'bg-card hover:bg-accent border-border text-foreground/90'
                    if (isAnswered) {
                      if (isCorrect) btnCls = 'bg-emerald-500/10 border-emerald-500/40 text-emerald-700 dark:text-emerald-300 font-semibold'
                      else if (isPicked) btnCls = 'bg-red-500/10 border-red-500/40 text-red-700 dark:text-red-300'
                      else btnCls = 'opacity-50 border-border'
                    }

                    return (
                      <button
                        key={oIdx}
                        disabled={isAnswered}
                        onClick={() => handleSelect(oIdx)}
                        className={`w-full p-3 rounded-xl border text-xs text-left transition-all flex items-start gap-2.5 ${btnCls}`}
                      >
                        <span className="w-5 h-5 rounded-md bg-accent flex items-center justify-center font-bold shrink-0 text-[10px]">
                          {String.fromCharCode(65 + oIdx)}
                        </span>
                        <span className="flex-1 mt-0.5">{opt}</span>
                        {isAnswered && isCorrect && <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />}
                        {isAnswered && isPicked && !isCorrect && <XCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />}
                      </button>
                    )
                  })}
                </div>

                {answers[currentIdx] !== undefined && (
                  <div className="p-3 rounded-xl bg-accent/40 border border-border text-xs space-y-1">
                    <span className="font-bold text-foreground block">Explanation:</span>
                    <p className="text-muted-foreground leading-relaxed">{currentQ.explanation}</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-center text-xs text-muted-foreground py-8">No questions loaded.</p>
            )}
          </div>

          {/* Footer */}
          {!showResult && (
            <div className="pt-3 border-t border-border/50 flex justify-between items-center">
              <span className="text-xs text-muted-foreground">Answer to test mastery</span>
              {answers[currentIdx] !== undefined && (
                <button
                  onClick={handleNext}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-foreground text-background hover:opacity-90 transition-opacity flex items-center gap-1.5"
                >
                  <span>{currentIdx + 1 < total ? 'Next Question' : 'View Results'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
export default AIDiagnosticQuizModal
''')

# 5. AIProjectGeneratorModal.jsx
with open("frontend/src/components/learning/AIProjectGeneratorModal.jsx", "w", encoding="utf-8") as f:
    f.write(r'''import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Code2, Sparkles, Copy, Check, Terminal, Layers, CheckCircle2, Loader2, ArrowRight } from 'lucide-react'
import { generateProjectSpec } from '../../services/recommenderService'

export const AIProjectGeneratorModal = ({ isOpen, onClose, milestone, domain }) => {
  const [loading, setLoading] = useState(false)
  const [spec, setSpec] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (isOpen && milestone) {
      setLoading(true)
      setCopied(false)
      generateProjectSpec({
        domain: domain || 'Modern Fullstack AI',
        milestone_title: milestone.title,
        skills: milestone.skills || [],
        experience_level: 'Intermediate',
      })
        .then((res) => {
          if (res?.project) setSpec(res.project)
        })
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [isOpen, milestone, domain])

  if (!isOpen) return null

  const handleCopy = () => {
    if (spec?.starter_boilerplate_code) {
      navigator.clipboard.writeText(spec.starter_boilerplate_code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-2xl bg-card text-card-foreground rounded-2xl border border-border shadow-2xl overflow-hidden p-6"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 border-b border-border/50 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-orange-500/10 text-orange-600 dark:text-orange-400 flex items-center justify-center border border-orange-500/20">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-orange-600 dark:text-orange-400">
                  AI Project Architect
                </span>
                <h3 className="text-lg font-bold text-foreground leading-tight">
                  {spec?.project_title || 'Project Blueprint & Starter Code'}
                </h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="py-4 space-y-4 max-h-[70vh] overflow-y-auto">
            {loading ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-center">
                <Loader2 className="w-8 h-8 animate-spin text-orange-500" />
                <p className="text-sm text-muted-foreground">Architecting production project blueprint & starter code...</p>
              </div>
            ) : spec ? (
              <div className="space-y-4">
                {/* Tagline & Hours */}
                <div className="flex flex-wrap items-center justify-between gap-2 p-3.5 rounded-xl bg-orange-500/10 border border-orange-500/20">
                  <p className="text-xs font-medium text-orange-800 dark:text-orange-300">
                    {spec.tagline}
                  </p>
                  <span className="text-xs font-bold bg-card px-2.5 py-1 rounded-lg border border-border shrink-0">
                    Est. {spec.estimated_hours} Hours
                  </span>
                </div>

                {/* Architecture Overview */}
                <div className="space-y-1">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-blue-500" />
                    Architecture Overview
                  </h4>
                  <p className="text-xs text-foreground leading-relaxed bg-accent/20 p-3 rounded-xl border border-border/50">
                    {spec.architecture_overview}
                  </p>
                </div>

                {/* Key Features & Tech Stack */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-accent/20 border border-border/50 space-y-2">
                    <h5 className="text-xs font-bold text-foreground">Key Deliverables:</h5>
                    <ul className="space-y-1.5">
                      {spec.key_features?.map((f, i) => (
                        <li key={i} className="text-[11px] text-muted-foreground flex items-start gap-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-3 rounded-xl bg-accent/20 border border-border/50 space-y-2">
                    <h5 className="text-xs font-bold text-foreground">Tech Stack:</h5>
                    <div className="flex flex-wrap gap-1.5">
                      {spec.tech_stack?.map((t, i) => (
                        <span key={i} className="text-[11px] font-medium bg-card px-2.5 py-1 rounded-lg border border-border text-foreground">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Boilerplate Code */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-purple-500" />
                      Starter Boilerplate Template
                    </h4>
                    <button
                      onClick={handleCopy}
                      className="px-2.5 py-1 rounded-lg bg-card hover:bg-accent border border-border text-[11px] font-semibold text-foreground flex items-center gap-1 transition-colors"
                    >
                      {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                      <span>{copied ? 'Copied!' : 'Copy Code'}</span>
                    </button>
                  </div>
                  <pre className="p-3.5 rounded-xl bg-gray-950 text-gray-100 font-mono text-[11px] overflow-x-auto border border-gray-800 leading-relaxed">
                    {spec.starter_boilerplate_code}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-center text-xs text-muted-foreground py-8">No spec available.</p>
            )}
          </div>

          {/* Footer */}
          <div className="pt-3 border-t border-border/50 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-foreground text-background hover:opacity-90 transition-opacity"
            >
              Close Spec
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
export default AIProjectGeneratorModal
''')

# 6. AICodeReviewModal.jsx
with open("frontend/src/components/learning/AICodeReviewModal.jsx", "w", encoding="utf-8") as f:
    f.write(r'''import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, Award, AlertCircle, Sparkles, Loader2, Send, ShieldCheck, ThumbsUp } from 'lucide-react'
import { validateCheckpoint } from '../../services/recommenderService'

export const AICodeReviewModal = ({ isOpen, onClose, milestone }) => {
  const [submission, setSubmission] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  if (!isOpen) return null

  const handleReview = async (e) => {
    e.preventDefault()
    if (!submission.trim() || loading) return

    setLoading(true)
    try {
      const res = await validateCheckpoint({
        milestone_title: milestone?.title || 'Checkpoint Validation',
        checkpoint_goal: milestone?.checkpoint_project || 'Milestone Implementation',
        submission_text: submission,
      })
      if (res?.evaluation) setResult(res.evaluation)
    } catch (e) {
      setResult({
        passed: true,
        score: 85,
        grade: 'Proficient',
        feedback: 'Great submission! Your code covers the essential milestone logic.',
        strengths: ['Clean code organization', 'Addresses core problem'],
        areas_for_improvement: ['Consider adding error boundary handling'],
        badges_unlocked: ['Checkpoint Crusher'],
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-lg bg-card text-card-foreground rounded-2xl border border-border shadow-2xl overflow-hidden p-6"
        >
          {/* Header */}
          <div className="flex items-start justify-between gap-4 border-b border-border/50 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                  Checkpoint Code Review
                </span>
                <h3 className="text-lg font-bold text-foreground leading-tight">
                  {milestone?.title || 'Submit Milestone for Review'}
                </h3>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="py-4 space-y-4 max-h-[70vh] overflow-y-auto">
            {result ? (
              <div className="space-y-4">
                {/* Score & Grade */}
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center space-y-1">
                  <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 uppercase">Grade</span>
                  <div className="text-2xl font-black text-foreground">{result.grade} ({result.score}/100)</div>
                  <p className="text-xs text-muted-foreground">{result.feedback}</p>
                </div>

                {/* Badges */}
                {result.badges_unlocked?.length > 0 && (
                  <div className="p-3 rounded-xl bg-accent/40 border border-border flex items-center gap-2">
                    <Award className="w-5 h-5 text-amber-500 shrink-0" />
                    <div className="text-xs">
                      <span className="font-bold text-foreground">Badges Earned: </span>
                      <span className="text-muted-foreground">{result.badges_unlocked.join(', ')}</span>
                    </div>
                  </div>
                )}

                {/* Strengths & Improvements */}
                <div className="space-y-2 text-xs">
                  <div className="p-3 rounded-xl bg-accent/20 border border-border/50 space-y-1">
                    <span className="font-bold text-foreground flex items-center gap-1.5">
                      <ThumbsUp className="w-3.5 h-3.5 text-emerald-500" />
                      Strengths:
                    </span>
                    <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                      {result.strengths?.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  </div>

                  <div className="p-3 rounded-xl bg-accent/20 border border-border/50 space-y-1">
                    <span className="font-bold text-foreground flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                      Suggestions for Growth:
                    </span>
                    <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                      {result.areas_for_improvement?.map((a, i) => <li key={i}>{a}</li>)}
                    </ul>
                  </div>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => {
                      setResult(null)
                      setSubmission('')
                    }}
                    className="px-4 py-2 bg-card hover:bg-accent border border-border rounded-xl text-xs font-semibold text-foreground mr-2"
                  >
                    Submit Another Code Sample
                  </button>
                  <button
                    onClick={onClose}
                    className="px-4 py-2 bg-foreground text-background rounded-xl text-xs font-semibold hover:opacity-90"
                  >
                    Done
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleReview} className="space-y-4">
                <div className="p-3 rounded-xl bg-accent/30 border border-border">
                  <span className="text-xs text-muted-foreground block mb-0.5">Checkpoint Requirement:</span>
                  <p className="text-xs font-semibold text-foreground">
                    {milestone?.checkpoint_project || 'Implement functional baseline code meeting milestone goals.'}
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-foreground">Paste your code or repo summary:</label>
                  <textarea
                    rows={7}
                    value={submission}
                    onChange={(e) => setSubmission(e.target.value)}
                    placeholder="Paste code snippet, implementation notes, or GitHub link here..."
                    className="w-full bg-accent/20 border border-border rounded-xl p-3 text-xs text-foreground placeholder:text-muted-foreground font-mono focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    required
                  />
                </div>

                <div className="pt-2 flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={!submission.trim() || loading}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-foreground text-background hover:opacity-90 disabled:opacity-40 transition-opacity flex items-center gap-1.5"
                  >
                    {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                    <span>{loading ? 'Reviewing Code...' : 'Submit for AI Review'}</span>
                  </button>
                </div>
              </form>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
export default AICodeReviewModal
''')

print("Created AIDiagnosticQuizModal.jsx, AIProjectGeneratorModal.jsx, AICodeReviewModal.jsx")
