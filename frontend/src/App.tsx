import { motion, AnimatePresence } from 'framer-motion';
import {
  Database,
  MessageSquare,
  BarChart3,
  Upload,
  RefreshCw,
  Github,
  Sparkles,
  PanelLeftClose,
  PanelRightClose,
  PanelLeftOpen,
  PanelRightOpen,
  Moon,
  Sun,
} from 'lucide-react';
import { useState } from 'react';
import { FileUpload, DatasetSummary, ChatInterface, PlotGallery, VersionSelector } from './components';
import { useAppStore } from './lib/store';
import { cn } from './lib/utils';

function App() {
  const { sessionId, summary, clearSession, clearMessages, theme, toggleTheme } = useAppStore();
  const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);
  const [rightPanelCollapsed, setRightPanelCollapsed] = useState(false);

  const handleNewSession = () => {
    clearSession();
  };

  const handleClearChat = () => {
    clearMessages();
  };

  return (
    <div className={cn("h-screen bg-surface-950 relative overflow-hidden flex flex-col", theme)}>
      {/* Background Effects */}
      <div className="fixed inset-0 pointer-events-none">
        {/* Gradient orbs */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary-500/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-accent-500/10 rounded-full blur-[100px] animate-pulse-slow animation-delay-500" />
        
        {/* Grid pattern */}
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
                             linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px)`,
            backgroundSize: '50px 50px',
          }}
        />
      </div>

      {/* Header */}
      <header className="relative z-20 border-b border-surface-800/50 backdrop-blur-sm bg-surface-950/80 flex-shrink-0">
        <div className="px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 border border-primary-500/20">
                  <Sparkles className="w-5 h-5 text-primary-400" />
                </div>
              </div>
              <div>
                <h1 className="text-lg font-display font-bold text-surface-100">
                  EDA Agent
                </h1>
                <p className="text-xs text-surface-500">
                  AI-Powered Data Analysis
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {sessionId && (
                <>
                  <button
                    onClick={handleClearChat}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-800/50 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span className="hidden sm:inline">Clear Chat</span>
                  </button>
                  <button
                    onClick={handleNewSession}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-800/50 transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    <span className="hidden sm:inline">New Dataset</span>
                  </button>
                </>
              )}
              
              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg text-surface-500 hover:text-surface-300 hover:bg-surface-800/50 transition-colors"
                title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </button>
              
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg text-surface-500 hover:text-surface-300 hover:bg-surface-800/50 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 flex overflow-hidden">
        <AnimatePresence mode="wait">
          {!sessionId ? (
            // Upload State - Centered
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex flex-col items-center justify-center p-8 overflow-y-auto"
            >
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center mb-8"
              >
                <h2 className="text-3xl md:text-4xl font-display font-bold mb-3">
                  <span className="gradient-text">Explore Your Data</span>
                </h2>
                <p className="text-surface-400 max-w-md mx-auto">
                  Upload a dataset and let AI help you discover insights,
                  create visualizations, and understand your data better.
                </p>
              </motion.div>

              <FileUpload />

              {/* Features */}
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl"
              >
                {[
                  {
                    icon: <MessageSquare className="w-5 h-5" />,
                    title: 'Natural Language',
                    description: 'Ask questions in plain English',
                  },
                  {
                    icon: <BarChart3 className="w-5 h-5" />,
                    title: 'Auto Visualizations',
                    description: 'Generate charts and plots instantly',
                  },
                  {
                    icon: <Database className="w-5 h-5" />,
                    title: 'Data Wrangling',
                    description: 'Clean, transform & version your data',
                  },
                ].map((feature, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-4 rounded-xl glass-light"
                  >
                    <div className="p-2 rounded-lg bg-primary-500/20 text-primary-400">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="font-medium text-surface-200">
                        {feature.title}
                      </h3>
                      <p className="text-sm text-surface-500">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            // Analysis State - 3 Column Layout
            <motion.div
              key="analysis"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex min-h-0"
            >
              {/* LEFT PANEL - Dataset Info & Versions */}
              <motion.div
                initial={false}
                animate={{ 
                  width: leftPanelCollapsed ? '48px' : '320px',
                  minWidth: leftPanelCollapsed ? '48px' : '280px',
                }}
                transition={{ duration: 0.2 }}
                className="border-r border-surface-800/50 bg-surface-900/50 flex flex-col overflow-hidden flex-shrink-0"
              >
                {/* Panel Header with Toggle */}
                <div className="p-3 border-b border-surface-800/50 flex items-center justify-between flex-shrink-0">
                  {!leftPanelCollapsed && (
                    <h3 className="text-sm font-medium text-surface-300 flex items-center gap-2">
                      <Database className="w-4 h-4 text-primary-400" />
                      Dataset Info
                    </h3>
                  )}
                  <button
                    onClick={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-700/50 transition-colors"
                    title={leftPanelCollapsed ? "Expand panel" : "Collapse panel"}
                  >
                    {leftPanelCollapsed ? (
                      <PanelLeftOpen className="w-4 h-4" />
                    ) : (
                      <PanelLeftClose className="w-4 h-4" />
                    )}
                  </button>
                </div>

                {/* Panel Content */}
                {!leftPanelCollapsed && (
                  <div className="flex-1 overflow-y-auto">
                    {/* Dataset Summary */}
                    <div className="p-4 border-b border-surface-800/50">
                      {summary && <DatasetSummary summary={summary} />}
                    </div>

                    {/* Version Selector */}
                    <div className="p-4">
                      <VersionSelector />
                    </div>
                  </div>
                )}

                {/* Collapsed state icons */}
                {leftPanelCollapsed && (
                  <div className="flex flex-col items-center gap-4 py-4">
                    <div className="p-2 rounded-lg bg-primary-500/20" title="Dataset Info">
                      <Database className="w-4 h-4 text-primary-400" />
                    </div>
                  </div>
                )}
              </motion.div>

              {/* CENTER PANEL - Chat Interface */}
              <div className="flex-1 flex flex-col min-w-0 bg-surface-950/30">
                {/* Chat Header */}
                <div className="px-4 py-3 border-b border-surface-800/50 bg-surface-900/30 flex-shrink-0">
                  <h3 className="text-sm font-medium text-surface-300 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-primary-400" />
                    Chat with your data
                    <span className="text-xs text-surface-500 ml-2">
                      Ask questions, request visualizations, or transform your data
                    </span>
                  </h3>
                </div>
                
                {/* Chat Content */}
                <div className="flex-1 min-h-0">
                  <ChatInterface />
                </div>
              </div>

              {/* RIGHT PANEL - Visualizations */}
              <motion.div
                initial={false}
                animate={{ 
                  width: rightPanelCollapsed ? '48px' : '380px',
                  minWidth: rightPanelCollapsed ? '48px' : '300px',
                }}
                transition={{ duration: 0.2 }}
                className="border-l border-surface-800/50 bg-surface-900/50 flex flex-col overflow-hidden flex-shrink-0"
              >
                {/* Panel Header with Toggle */}
                <div className="p-3 border-b border-surface-800/50 flex items-center justify-between flex-shrink-0">
                  <button
                    onClick={() => setRightPanelCollapsed(!rightPanelCollapsed)}
                    className="p-1.5 rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-700/50 transition-colors"
                    title={rightPanelCollapsed ? "Expand panel" : "Collapse panel"}
                  >
                    {rightPanelCollapsed ? (
                      <PanelRightOpen className="w-4 h-4" />
                    ) : (
                      <PanelRightClose className="w-4 h-4" />
                    )}
                  </button>
                  {!rightPanelCollapsed && (
                    <h3 className="text-sm font-medium text-surface-300 flex items-center gap-2">
                      <BarChart3 className="w-4 h-4 text-primary-400" />
                      Visualizations
                    </h3>
                  )}
                </div>

                {/* Panel Content */}
                {!rightPanelCollapsed && (
                  <div className="flex-1 min-h-0">
                    <PlotGallery />
                  </div>
                )}

                {/* Collapsed state icons */}
                {rightPanelCollapsed && (
                  <div className="flex flex-col items-center gap-4 py-4">
                    <div className="p-2 rounded-lg bg-primary-500/20" title="Visualizations">
                      <BarChart3 className="w-4 h-4 text-primary-400" />
                    </div>
                  </div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
