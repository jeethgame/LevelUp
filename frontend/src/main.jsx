import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import { ToastProvider } from './contexts/ToastContext.jsx'
import { SkillProvider } from './contexts/SkillContext.jsx'
import { TaskProvider } from './contexts/TaskContext.jsx'
import { RoadmapProvider } from './contexts/RoadmapContext.jsx'
import { GoalProvider } from './contexts/GoalContext.jsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <ToastProvider>
        <SkillProvider>
          <TaskProvider>
            <RoadmapProvider>
              <GoalProvider>
                <BrowserRouter>
                  <App />
                </BrowserRouter>
              </GoalProvider>
            </RoadmapProvider>
          </TaskProvider>
        </SkillProvider>
      </ToastProvider>
    </ThemeProvider>
  </React.StrictMode>,
)

// rebuild trigger
