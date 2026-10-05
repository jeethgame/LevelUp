with open("frontend/src/pages/LearningRecommender.jsx", "a", encoding="utf-8") as f:
    f.write(r'''
  return (
    <AppShell>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        <PageHeader
          title="AI-Powered Personalized Learning Path Recommender"
          subtitle="Synthesize hyper-personalized learning trajectories calibrated to your skills, available hours, and career aspirations."
          action={
            <button
              onClick={() => setShowProfileDrawer(!showProfileDrawer)}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-card border border-border text-foreground hover:bg-accent transition-colors shadow-sm"
            >
              <Sliders className="w-4 h-4 text-purple-500" />
              <span>Learner Profile & Preferences</span>
            </button>
          }
        />

        <AnimatePresence>
          {showProfileDrawer && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="p-5 rounded-2xl bg-card border border-border shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-border/50 pb-3">
                  <div className="flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-purple-500" />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
                      Active Learner Profile Calibration
                    </h3>
                  </div>
                  <button
                    onClick={() => setShowProfileDrawer(false)}
                    className="text-xs text-muted-foreground hover:text-foreground"
                  >
                    Done
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                  <div className="space-y-1.5">
                    <label className="font-semibold text-foreground flex items-center justify-between">
                      <span>Weekly Hour Budget</span>
                      <span className="font-bold text-purple-600 dark:text-purple-400">{profile.weekly_hours} hrs/wk</span>
                    </label>
                    <input
                      type="range"
                      min={3}
                      max={40}
                      step={1}
                      value={profile.weekly_hours}
                      onChange={(e) => setProfile({ ...profile, weekly_hours: parseInt(e.target.value) })}
                      className="w-full accent-purple-600"
                    />
                    <div className="flex justify-between text-[10px] text-muted-foreground">
                      <span>3h (Casual)</span>
                      <span>15h (Balanced)</span>
                      <span>40h (Intensive)</span>
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-foreground">Current Baseline Level</label>
                    <select
                      value={profile.experience_level}
                      onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                      className="w-full bg-accent/40 border border-border rounded-xl px-3 py-2 text-xs font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-purple-500"
                    >
                      <option value="Beginner">Beginner (New to domain)</option>
                      <option value="Intermediate">Intermediate (Building apps)</option>
                      <option value="Advanced">Advanced (Senior mastery)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="font-semibold text-foreground">Preferred Modality</label>
                    <select
                      value={profile.learning_style}
                      onChange={(e) => setProfile({ ...profile, learning_style: e.target.value })}
                      className="w-full bg-accent/40 border border-border rounded-xl px-3 py-2 text-xs font-medium text-foreground focus:outline-none focus:ring-1 focus:ring-purple-500"
                    >
                      <option value="Hands-on projects">Hands-on projects & Code repos</option>
                      <option value="Video masterclasses">Video masterclasses & Tutorials</option>
                      <option value="Official documentation">Official documentation & Deep dives</option>
                      <option value="Balanced mix">Balanced mix of all formats</option>
                    </select>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="p-6 rounded-3xl bg-gradient-to-br from-purple-500/10 via-card to-background border border-purple-500/20 shadow-lg space-y-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-wider">
            <Sparkles className="w-4 h-4" />
            <span>Conversational Goal Intake</span>
          </div>

          <form onSubmit={(e) => handleGeneratePlan(e)} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <input
                type="text"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="Describe your learning objective in plain English (e.g., 'Become an AI Agent Engineer in 8 weeks')..."
                className="w-full bg-card/80 backdrop-blur-sm border border-border/80 rounded-2xl px-4 py-3.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-purple-500/40 shadow-inner"
              />
            </div>
            <button
              type="submit"
              disabled={!goal.trim() || loading}
              className="px-6 py-3.5 rounded-2xl bg-foreground text-background font-bold text-xs hover:opacity-90 disabled:opacity-40 transition-all flex items-center justify-center gap-2 shadow-md shrink-0"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Compass className="w-4 h-4" />}
              <span>{loading ? 'Synthesizing Path...' : 'Generate AI Roadmap'}</span>
            </button>
          </form>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-medium text-muted-foreground">Quick Presets:</span>
            {GOAL_PRESETS.map((p, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setGoal(p.text)
                  handleGeneratePlan(null, p.text)
                }}
                className="text-[11px] bg-card hover:bg-accent border border-border/80 px-3 py-1.5 rounded-full text-foreground/90 hover:text-foreground font-medium transition-all"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {!plan && !loading && (
          <div className="py-16 text-center space-y-4 rounded-3xl border border-dashed border-border bg-card/40 p-8">
            <div className="w-16 h-16 rounded-2xl bg-purple-500/10 text-purple-600 flex items-center justify-center mx-auto border border-purple-500/20">
              <Bot className="w-8 h-8" />
            </div>
            <div className="max-w-md mx-auto space-y-1.5">
              <h3 className="text-base font-bold text-foreground">Your Intelligent Learning Assistant Awaits</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Describe any technical milestone, target career role, or skill gap above to generate an adaptive, milestone-based learning roadmap with prerequisites, curated resources, and AI mentoring.
              </p>
            </div>
          </div>
        )}

        {loading && (
          <div className="py-20 text-center space-y-4">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-purple-500 border-t-transparent mx-auto" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-foreground">AI Architecting Personalized Roadmap...</h4>
              <p className="text-xs text-muted-foreground">Scoring prerequisite graphs, selecting verified resources, and calibrating timelines.</p>
            </div>
          </div>
        )}
''')
