# -*- coding: utf-8 -*-
with open("frontend/src/pages/LearningRecommender.jsx", "a", encoding="utf-8") as f:
    f.write(r'''
        {plan && !loading && (
          <div className="space-y-8">
            <div className="p-6 rounded-3xl bg-card border border-border shadow-md space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/60 pb-6">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="px-3 py-1 rounded-full bg-purple-500/10 text-purple-600 dark:text-purple-400 text-xs font-bold border border-purple-500/20">
                      Target Career: {plan.target_career}
                    </span>
                    <span className="text-xs font-medium text-muted-foreground">
                      Calibrated at {plan.weekly_hours || profile.weekly_hours} hrs/week
                    </span>
                  </div>
                  <h2 className="text-2xl font-black text-foreground tracking-tight">{plan.title}</h2>
                  <p className="text-xs text-muted-foreground mt-1 max-w-2xl leading-relaxed">{plan.summary}</p>
                </div>

                <button
                  onClick={handleAdoptRoadmap}
                  disabled={adopting}
                  className="px-5 py-3 rounded-2xl bg-foreground text-background font-bold text-xs hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2 shadow-lg shrink-0"
                >
                  {adopting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                  <span>{adopting ? 'Adopting to Workspace...' : 'Adopt to My Skills & Tasks'}</span>
                </button>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-4 rounded-2xl bg-accent/30 border border-border/60">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase">Relevance Match</span>
                  <div className="text-2xl font-black text-foreground mt-0.5">{plan.match_score || 88}%</div>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Optimal alignment</span>
                </div>

                <div className="p-4 rounded-2xl bg-accent/30 border border-border/60">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase">Readiness Level</span>
                  <div className="text-2xl font-black text-foreground mt-0.5">{plan.readiness_score || 65}%</div>
                  <span className="text-[10px] text-muted-foreground">Baseline score</span>
                </div>

                <div className="p-4 rounded-2xl bg-accent/30 border border-border/60">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase">Total Study Hours</span>
                  <div className="text-2xl font-black text-foreground mt-0.5">{plan.total_estimated_hours || 64}h</div>
                  <span className="text-[10px] text-muted-foreground">Estimated effort</span>
                </div>

                <div className="p-4 rounded-2xl bg-accent/30 border border-border/60">
                  <span className="text-[11px] font-semibold text-muted-foreground uppercase">Time to Readiness</span>
                  <div className="text-2xl font-black text-purple-600 dark:text-purple-400 mt-0.5">{plan.weeks_to_readiness || 6} wks</div>
                  <span className="text-[10px] text-muted-foreground">At {plan.weekly_hours || profile.weekly_hours}h / week</span>
                </div>
              </div>

              {plan.explainability && (
                <div className="p-4 rounded-2xl bg-purple-500/5 border border-purple-500/20 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-foreground flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                      AI Strategic Rationale:
                    </span>
                    <button
                      onClick={() => handleExplain({ title: plan.title, name: plan.title }, 'roadmap')}
                      className="text-purple-600 dark:text-purple-400 font-semibold hover:underline flex items-center gap-1"
                    >
                      <span>Deep Explainability Rationale</span>
                      <ArrowUpRight className="w-3 h-3" />
                    </button>
                  </div>
                  <p className="text-muted-foreground leading-relaxed">{plan.explainability.why_this_path}</p>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                  <Layers className="w-5 h-5 text-purple-500" />
                  Structured Milestone Roadmap
                </h3>
                <span className="text-xs text-muted-foreground font-medium">
                  {plan.phases?.length || 0} Progressive Phases
                </span>
              </div>

              <div className="space-y-4">
                {plan.phases?.map((phase, pIdx) => {
                  const isExp = expandedPhases[phase.phase_number ?? (pIdx + 1)]

                  return (
                    <div
                      key={pIdx}
                      className="rounded-3xl bg-card border border-border shadow-sm overflow-hidden transition-all"
                    >
                      <button
                        onClick={() => togglePhase(phase.phase_number ?? (pIdx + 1))}
                        className="w-full p-5 flex items-center justify-between gap-4 text-left hover:bg-accent/30 transition-colors border-b border-border/40"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-black text-xs flex items-center justify-center border border-purple-500/20">
                            {phase.phase_number || (pIdx + 1)}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-bold text-foreground">{phase.phase_name}</h4>
                              <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent text-muted-foreground font-semibold">
                                {phase.timeline}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground mt-0.5">
                              {phase.milestones?.length || 0} Milestones - Est. {phase.estimated_hours || 15} Hours
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground hidden sm:inline">
                            {isExp ? 'Collapse' : 'Expand'}
                          </span>
                          {isExp ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                        </div>
                      </button>

                      <AnimatePresence>
                        {isExp && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="p-5 space-y-6"
                          >
                            {phase.prerequisites?.length > 0 && (
                              <div className="p-2.5 px-3.5 rounded-xl bg-accent/30 border border-border/50 text-xs flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4 text-blue-500 shrink-0" />
                                <span className="font-semibold text-foreground">Phase Prerequisites:</span>
                                <span className="text-muted-foreground">{phase.prerequisites.join(', ')}</span>
                              </div>
                            )}

                            <div className="space-y-4">
                              {phase.milestones?.map((milestone, mIdx) => (
                                <div
                                  key={milestone.id || mIdx}
                                  className="p-5 rounded-2xl bg-accent/20 border border-border/70 space-y-4 hover:border-purple-500/40 transition-colors"
                                >
                                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                                    <div className="space-y-1">
                                      <div className="flex items-center gap-2">
                                        <h5 className="text-sm font-bold text-foreground">{milestone.title}</h5>
                                        {milestone.completed && (
                                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 font-bold border border-emerald-500/20">
                                            Mastered
                                          </span>
                                        )}
                                      </div>
                                      <p className="text-xs text-muted-foreground leading-relaxed">{milestone.description}</p>
                                    </div>

                                    <div className="flex items-center gap-1.5 shrink-0">
                                      <button
                                        onClick={() => handleExplain(milestone, 'milestone')}
                                        className="px-2.5 py-1.5 rounded-xl bg-card hover:bg-accent border border-border text-[11px] font-semibold text-foreground flex items-center gap-1.5 transition-colors"
                                        title="Explain why AI recommended this milestone"
                                      >
                                        <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                                        <span>Why This?</span>
                                      </button>

                                      <button
                                        onClick={() => setChatDrawer({ isOpen: true, milestone })}
                                        className="px-2.5 py-1.5 rounded-xl bg-card hover:bg-accent border border-border text-[11px] font-semibold text-foreground flex items-center gap-1.5 transition-colors"
                                        title="Chat with in-context AI mentor for this milestone"
                                      >
                                        <Bot className="w-3.5 h-3.5 text-blue-500" />
                                        <span>AI Mentor</span>
                                      </button>
                                    </div>
                                  </div>

                                  {milestone.skills?.length > 0 && (
                                    <div className="flex flex-wrap items-center gap-1.5">
                                      <span className="text-[11px] text-muted-foreground font-medium">Core Skills:</span>
                                      {milestone.skills.map((s, sIdx) => (
                                        <button
                                          key={sIdx}
                                          onClick={() => setQuizModal({ isOpen: true, skillName: s })}
                                          className="text-[11px] bg-card hover:bg-accent px-2 py-0.5 rounded-lg border border-border text-foreground font-medium transition-colors flex items-center gap-1"
                                          title={`Take AI Diagnostic Quiz for ${s}`}
                                        >
                                          <span>{s}</span>
                                          <Award className="w-3 h-3 text-blue-500" />
                                        </button>
                                      ))}
                                    </div>
                                  )}

                                  {milestone.resources?.length > 0 && (
                                    <div className="space-y-2">
                                      <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground block">
                                        Verified Learning Resources:
                                      </span>
                                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                                        {milestone.resources.map((res, rIdx) => (
                                          <div
                                            key={rIdx}
                                            className="p-3 rounded-xl bg-card border border-border flex flex-col justify-between gap-2 text-xs"
                                          >
                                            <div className="space-y-1">
                                              <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                                                <span className="font-semibold uppercase tracking-wider text-purple-600 dark:text-purple-400">
                                                  {res.type || 'Course'} - {res.provider || 'Verified Lab'}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                  <Clock className="w-3 h-3" />
                                                  {res.duration || '4 hours'}
                                                </span>
                                              </div>
                                              <p className="font-bold text-foreground leading-snug line-clamp-2">
                                                {res.title}
                                              </p>
                                            </div>

                                            <div className="flex items-center justify-between pt-1 border-t border-border/40">
                                              <a
                                                href={res.url}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="text-[11px] font-semibold text-foreground hover:text-purple-600 flex items-center gap-1"
                                              >
                                                <span>Open Resource</span>
                                                <ExternalLink className="w-3 h-3" />
                                              </a>

                                              <button
                                                onClick={() => handleExplain(res, res.type || 'resource')}
                                                className="text-[10px] text-muted-foreground hover:text-foreground flex items-center gap-1"
                                              >
                                                <Sparkles className="w-2.5 h-2.5 text-purple-500" />
                                                <span>Why chosen?</span>
                                              </button>
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  <div className="p-3.5 rounded-xl bg-orange-500/5 border border-orange-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                                    <div className="space-y-0.5">
                                      <span className="font-bold text-orange-800 dark:text-orange-300 flex items-center gap-1">
                                        <Code2 className="w-3.5 h-3.5" />
                                        Checkpoint Project:
                                      </span>
                                      <p className="text-muted-foreground">
                                        {milestone.checkpoint_project || 'Build and document a functional project prototype.'}
                                      </p>
                                    </div>

                                    <div className="flex items-center gap-1.5 shrink-0">
                                      <button
                                        onClick={() => setProjectModal({ isOpen: true, milestone })}
                                        className="px-2.5 py-1.5 rounded-xl bg-card hover:bg-accent border border-border font-bold text-[11px] text-foreground flex items-center gap-1 transition-colors"
                                      >
                                        <Terminal className="w-3 h-3 text-orange-500" />
                                        <span>AI Architect Spec</span>
                                      </button>

                                      <button
                                        onClick={() => setCodeReviewModal({ isOpen: true, milestone })}
                                        className="px-2.5 py-1.5 rounded-xl bg-card hover:bg-accent border border-border font-bold text-[11px] text-foreground flex items-center gap-1 transition-colors"
                                      >
                                        <FileCheck className="w-3 h-3 text-emerald-500" />
                                        <span>AI Code Review</span>
                                      </button>
                                    </div>
                                  </div>

                                  <AdaptiveRoadmapControls
                                    milestone={milestone}
                                    onAdapt={handleAdapt}
                                    isCompleted={milestone.completed}
                                  />
                                </div>
                              ))}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <RecommendationExplainModal
        isOpen={explainModal.isOpen}
        onClose={() => setExplainModal({ isOpen: false, item: null, explanation: null, loading: false })}
        item={explainModal.item}
        explanation={explainModal.explanation}
        loading={explainModal.loading}
      />

      <RoadmapAIChatDrawer
        isOpen={chatDrawer.isOpen}
        onClose={() => setChatDrawer({ isOpen: false, milestone: null })}
        milestone={chatDrawer.milestone}
      />

      <AIDiagnosticQuizModal
        isOpen={quizModal.isOpen}
        onClose={() => setQuizModal({ isOpen: false, skillName: '' })}
        skillName={quizModal.skillName}
      />

      <AIProjectGeneratorModal
        isOpen={projectModal.isOpen}
        onClose={() => setProjectModal({ isOpen: false, milestone: null })}
        milestone={projectModal.milestone}
        domain={plan?.target_career}
      />

      <AICodeReviewModal
        isOpen={codeReviewModal.isOpen}
        onClose={() => setCodeReviewModal({ isOpen: false, milestone: null })}
        milestone={codeReviewModal.milestone}
      />
    </AppShell>
  )
}

export default LearningRecommender
''')

print("LearningRecommender.jsx completed successfully")
