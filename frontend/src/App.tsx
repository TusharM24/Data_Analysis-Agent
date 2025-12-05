import { motion, AnimatePresence } from 'framer-motion';
import {
  Database,
  MessageSquare,
  BarChart3,
  Upload,
  RefreshCw,
  Github,
  Sparkles,
} from 'lucide-react';
import { FileUpload, DatasetSummary, ChatInterface, PlotGallery } from './components';
import { useAppStore } from './lib/store';
import { cn } from './lib/utils';

function App() {
  const { sessionId, summary, clearSession, clearMessages } = useAppStore();

  const handleNewSession = () => {
    clearSession();
  };

  const handleClearChat = () => {
    clearMessages();
  };

  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
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

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="border-b border-surface-800/50 backdrop-blur-sm bg-surface-950/80 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 border border-primary-500/20">
                    <Sparkles className="w-6 h-6 text-primary-400" />
                  </div>
                  <div className="absolute -inset-1 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 blur-lg opacity-50" />
                </div>
                <div>
                  <h1 className="text-xl font-display font-bold text-surface-100">
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
                      className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-800/50 transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      <span className="hidden sm:inline">Clear Chat</span>
                    </button>
                    <button
                      onClick={handleNewSession}
                      className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg text-surface-400 hover:text-surface-200 hover:bg-surface-800/50 transition-colors"
                    >
                      <Upload className="w-4 h-4" />
                      <span className="hidden sm:inline">New Dataset</span>
                    </button>
                  </>
                )}
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

        {/* Main Area */}
        <main className="flex-1 flex flex-col">
          <AnimatePresence mode="wait">
            {!sessionId ? (
              // Upload State
              <motion.div
                key="upload"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center p-8"
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
                      title: 'Deep Analysis',
                      description: 'Statistical insights and patterns',
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
              // Analysis State
              <motion.div
                key="analysis"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col lg:flex-row min-h-0"
              >
                {/* Left Panel - Dataset Summary & Plot Gallery */}
                <div className="w-full lg:w-80 xl:w-96 border-b lg:border-b-0 lg:border-r border-surface-800/50 flex flex-col bg-surface-900/50">
                  {/* Dataset Summary */}
                  <div className="p-4 border-b border-surface-800/50 max-h-[40vh] lg:max-h-none overflow-y-auto">
                    {summary && <DatasetSummary summary={summary} />}
                  </div>

                  {/* Plot Gallery */}
                  <div className="flex-1 min-h-[200px] lg:min-h-0">
                    <div className="p-4 border-b border-surface-800/50">
                      <h3 className="text-sm font-medium text-surface-300 flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-primary-400" />
                        Visualizations
                      </h3>
                    </div>
                    <PlotGallery />
                  </div>
                </div>

                {/* Right Panel - Chat */}
                <div className="flex-1 flex flex-col min-h-0 min-w-0">
                  <div className="p-4 border-b border-surface-800/50 bg-surface-900/30">
                    <h3 className="text-sm font-medium text-surface-300 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-primary-400" />
                      Chat with your data
                    </h3>
                  </div>
                  <div className="flex-1 min-h-0">
                    <ChatInterface />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Footer */}
        <footer className="border-t border-surface-800/50 py-3 text-center text-xs text-surface-600">
          Powered by Groq • LangGraph • React
        </footer>
      </div>
    </div>
  );
}

export default App;

