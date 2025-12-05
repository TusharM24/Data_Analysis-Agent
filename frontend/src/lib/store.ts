import { create } from 'zustand';
import type { DatasetSummary, ChatMessage } from '../types';

interface AppStore {
  // Session state
  sessionId: string | null;
  summary: DatasetSummary | null;
  
  // Chat state
  messages: ChatMessage[];
  
  // UI state
  isLoading: boolean;
  isUploading: boolean;
  error: string | null;
  
  // Plot gallery
  selectedPlotIndex: number;
  allPlots: string[];
  
  // Actions
  setSession: (sessionId: string, summary: DatasetSummary) => void;
  clearSession: () => void;
  
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  clearMessages: () => void;
  
  setLoading: (loading: boolean) => void;
  setUploading: (uploading: boolean) => void;
  setError: (error: string | null) => void;
  
  addPlots: (plots: string[]) => void;
  setSelectedPlot: (index: number) => void;
}

export const useAppStore = create<AppStore>((set) => ({
  // Initial state
  sessionId: null,
  summary: null,
  messages: [],
  isLoading: false,
  isUploading: false,
  error: null,
  selectedPlotIndex: 0,
  allPlots: [],
  
  // Actions
  setSession: (sessionId, summary) => set({
    sessionId,
    summary,
    messages: [],
    allPlots: [],
    error: null,
  }),
  
  clearSession: () => set({
    sessionId: null,
    summary: null,
    messages: [],
    allPlots: [],
    error: null,
  }),
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map((msg) =>
      msg.id === id ? { ...msg, ...updates } : msg
    ),
  })),
  
  clearMessages: () => set({ messages: [], allPlots: [] }),
  
  setLoading: (isLoading) => set({ isLoading }),
  setUploading: (isUploading) => set({ isUploading }),
  setError: (error) => set({ error }),
  
  addPlots: (plots) => set((state) => ({
    allPlots: [...state.allPlots, ...plots],
    selectedPlotIndex: state.allPlots.length,
  })),
  
  setSelectedPlot: (selectedPlotIndex) => set({ selectedPlotIndex }),
}));

