import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Code2, Image, Loader2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { ChatMessage } from '../types';
import { cn, generateId } from '../lib/utils';
import { sendMessage, getPlotUrl } from '../lib/api';
import { useAppStore } from '../lib/store';

// Sample prompts for empty state
const SAMPLE_PROMPTS = [
  "Show me a summary of the dataset",
  "What are the correlations between numerical columns?",
  "Create a histogram of the a numerical column you think is most interesting",
  "Show me the distribution of missing values",
  "What are the top 10 most frequent values in a categorical column with the most unique values?",
];

interface MessageBubbleProps {
  message: ChatMessage;
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const [showCode, setShowCode] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center',
          isUser
            ? 'bg-gradient-to-br from-primary-500 to-accent-500'
            : 'bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-emerald-400" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          'flex-1 max-w-[85%]',
          isUser ? 'text-right' : 'text-left'
        )}
      >
        <div
          className={cn(
            'inline-block p-4 rounded-2xl',
            isUser
              ? 'bg-gradient-to-br from-primary-600/80 to-primary-700/80 text-white rounded-tr-sm'
              : 'glass-light text-surface-200 rounded-tl-sm'
          )}
        >
          {message.isLoading ? (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Analyzing...</span>
            </div>
          ) : (
            <div className="chat-markdown text-sm">
              <ReactMarkdown
                components={{
                  code({ className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const isInline = !match;
                    
                    return isInline ? (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    ) : (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        customStyle={{
                          margin: 0,
                          borderRadius: '8px',
                          fontSize: '0.8rem',
                        }}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    );
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Code Block (if present) */}
        {message.code && !isUser && (
          <div className="mt-2">
            <button
              onClick={() => setShowCode(!showCode)}
              className="flex items-center gap-1.5 text-xs text-surface-400 hover:text-primary-400 transition-colors"
            >
              <Code2 className="w-3.5 h-3.5" />
              {showCode ? 'Hide code' : 'Show code'}
            </button>
            
            <AnimatePresence>
              {showCode && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2 overflow-hidden"
                >
                  <SyntaxHighlighter
                    style={oneDark}
                    language="python"
                    customStyle={{
                      borderRadius: '8px',
                      fontSize: '0.75rem',
                      maxHeight: '300px',
                    }}
                  >
                    {message.code}
                  </SyntaxHighlighter>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Plots (if present) */}
        {message.plots && message.plots.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.plots.map((plot, i) => (
              <motion.a
                key={i}
                href={getPlotUrl(plot)}
                target="_blank"
                rel="noopener noreferrer"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="block relative group"
              >
                <img
                  src={getPlotUrl(plot)}
                  alt={`Plot ${i + 1}`}
                  className="max-w-xs rounded-lg border border-surface-700/50 hover:border-primary-500/50 transition-colors"
                />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                  <Image className="w-6 h-6 text-white" />
                </div>
              </motion.a>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="mt-1 text-xs text-surface-500">
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </motion.div>
  );
}

export function ChatInterface() {
  const {
    sessionId,
    messages,
    isLoading,
    addMessage,
    updateMessage,
    setLoading,
    addPlots,
    addVersion,
  } = useAppStore();

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 150)}px`;
    }
  }, [input]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    const assistantId = generateId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    };

    addMessage(userMessage);
    addMessage(assistantMessage);
    setInput('');
    setLoading(true);

    try {
      const response = await sendMessage(sessionId, userMessage.content);

      updateMessage(assistantId, {
        content: response.response,
        code: response.code,
        plots: response.plots,
        isLoading: false,
      });

      if (response.plots?.length) {
        addPlots(response.plots);
      }

      // Handle new dataset version if created
      if (response.new_version) {
        addVersion(response.new_version);
      }
    } catch (err) {
      updateMessage(assistantId, {
        content: `Sorry, I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}`,
        isLoading: false,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSamplePrompt = (prompt: string) => {
    setInput(prompt);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="h-full flex flex-col items-center justify-center text-center p-8"
          >
            <div className="relative mb-6">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20">
                <Sparkles className="w-10 h-10 text-primary-400" />
              </div>
              <div className="absolute -inset-2 rounded-2xl bg-gradient-to-br from-primary-500/10 to-accent-500/10 blur-xl" />
            </div>
            
            <h3 className="text-xl font-display font-semibold text-surface-100 mb-2">
              Ask me anything about your data
            </h3>
            <p className="text-surface-400 mb-6 max-w-md">
              I can help you explore, visualize, and understand your dataset.
              Try one of these prompts to get started:
            </p>
            
            <div className="flex flex-wrap gap-2 justify-center max-w-lg">
              {SAMPLE_PROMPTS.map((prompt, i) => (
                <motion.button
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  onClick={() => handleSamplePrompt(prompt)}
                  className="px-3 py-1.5 text-xs rounded-full bg-surface-800/80 border border-surface-700 text-surface-300 hover:border-primary-500/50 hover:text-primary-300 transition-colors"
                >
                  {prompt}
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-surface-800">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your data..."
              disabled={isLoading}
              rows={1}
              className={cn(
                'w-full px-4 py-3 rounded-xl resize-none',
                'bg-surface-800/50 border border-surface-700/50',
                'text-surface-200 placeholder:text-surface-500',
                'focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'transition-all duration-200'
              )}
            />
          </div>
          
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={cn(
              'p-3 rounded-xl transition-all duration-200',
              'bg-gradient-to-r from-primary-500 to-accent-500',
              'hover:from-primary-400 hover:to-accent-400',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-primary-500 disabled:hover:to-accent-500',
              'focus:outline-none focus:ring-2 focus:ring-primary-500/50'
            )}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            ) : (
              <Send className="w-5 h-5 text-white" />
            )}
          </button>
        </div>
        
        <p className="mt-2 text-xs text-surface-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

