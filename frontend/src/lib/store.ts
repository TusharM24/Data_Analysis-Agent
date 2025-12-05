import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { DatasetSummary, ChatMessage, DatasetVersion, VersionDisplayNames } from '../types';

type Theme = 'dark' | 'light';

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
  theme: Theme;
  
  // Plot gallery
  selectedPlotIndex: number;
  allPlots: string[];
  
  // Version management
  versions: DatasetVersion[];
  currentVersionId: string | null;
  versionDisplayNames: VersionDisplayNames;  // Frontend-only custom names
  
  // Actions
  setSession: (sessionId: string, summary: DatasetSummary, initialVersion?: DatasetVersion) => void;
  toggleTheme: () => void;
  clearSession: () => void;
  updateSummary: (summary: DatasetSummary) => void;
  
  addMessage: (message: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  clearMessages: () => void;
  
  setLoading: (loading: boolean) => void;
  setUploading: (uploading: boolean) => void;
  setError: (error: string | null) => void;
  
  addPlots: (plots: string[]) => void;
  setSelectedPlot: (index: number) => void;
  
  // Version actions
  setVersions: (versions: DatasetVersion[], currentVersionId: string) => void;
  addVersion: (version: DatasetVersion) => void;
  switchVersion: (versionId: string, newSummary: DatasetSummary) => void;
  renameVersion: (versionId: string, displayName: string) => void;
  getVersionDisplayName: (version: DatasetVersion) => string;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
      sessionId: null,
      summary: null,
      messages: [],
      isLoading: false,
      isUploading: false,
      error: null,
      theme: 'dark',
      selectedPlotIndex: 0,
      allPlots: [],
      versions: [],
      currentVersionId: null,
      versionDisplayNames: {},
      
      // Actions
      setSession: (sessionId, summary, initialVersion) => set({
        sessionId,
        summary,
        messages: [],
        allPlots: [],
        error: null,
        versions: initialVersion ? [initialVersion] : [],
        currentVersionId: initialVersion?.version_id || null,
      }),
      
      clearSession: () => set({
        sessionId: null,
        summary: null,
        messages: [],
        allPlots: [],
        error: null,
        versions: [],
        currentVersionId: null,
        // Note: We don't clear versionDisplayNames to preserve user's custom names
      }),
      
      updateSummary: (summary) => set({ summary }),
      
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
      
      toggleTheme: () => set((state) => ({
        theme: state.theme === 'dark' ? 'light' : 'dark',
      })),
      
      addPlots: (plots) => set((state) => ({
        allPlots: [...state.allPlots, ...plots],
        selectedPlotIndex: state.allPlots.length,
      })),
      
      setSelectedPlot: (selectedPlotIndex) => set({ selectedPlotIndex }),
      
      // Version actions
      setVersions: (versions, currentVersionId) => set({
        versions,
        currentVersionId,
      }),
      
      addVersion: (version) => set((state) => ({
        versions: [...state.versions, version],
        currentVersionId: version.version_id,
        summary: version.summary,
      })),
      
      switchVersion: (versionId, newSummary) => set({
        currentVersionId: versionId,
        summary: newSummary,
      }),
      
      renameVersion: (versionId, displayName) => set((state) => ({
        versionDisplayNames: {
          ...state.versionDisplayNames,
          [versionId]: displayName,
        },
      })),
      
      getVersionDisplayName: (version) => {
        const state = get();
        const customName = state.versionDisplayNames[version.version_id];
        if (customName) return customName;
        
        // Default name based on version number and description
        if (version.version_number === 1) {
          return 'Original';
        }
        return version.change_description || `Version ${version.version_number}`;
      },
    }),
    {
      name: 'eda-agent-storage',
      // Persist user preferences
      partialize: (state) => ({
        versionDisplayNames: state.versionDisplayNames,
        theme: state.theme,
      }),
    }
  )
);
