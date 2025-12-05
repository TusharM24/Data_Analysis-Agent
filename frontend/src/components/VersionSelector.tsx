import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  GitBranch, 
  Check, 
  Pencil, 
  X, 
  ChevronDown, 
  ChevronUp,
  Clock,
  Database
} from 'lucide-react';
import { cn, formatNumber } from '../lib/utils';
import { switchVersion } from '../lib/api';
import { useAppStore } from '../lib/store';
import type { DatasetVersion } from '../types';

interface VersionItemProps {
  version: DatasetVersion;
  isCurrent: boolean;
  onSelect: () => void;
  onRename: (newName: string) => void;
  displayName: string;
}

function VersionItem({ version, isCurrent, onSelect, onRename, displayName }: VersionItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(displayName);

  const handleSave = () => {
    if (editName.trim()) {
      onRename(editName.trim());
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setEditName(displayName);
      setIsEditing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'p-3 rounded-lg cursor-pointer transition-all duration-200',
        'border',
        isCurrent
          ? 'bg-primary-500/10 border-primary-500/30'
          : 'bg-surface-800/30 border-surface-700/30 hover:bg-surface-700/30 hover:border-surface-600/50'
      )}
      onClick={() => !isEditing && !isCurrent && onSelect()}
    >
      <div className="flex items-start gap-3">
        {/* Radio indicator */}
        <div className={cn(
          'mt-0.5 w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0',
          isCurrent
            ? 'border-primary-500 bg-primary-500'
            : 'border-surface-500'
        )}>
          {isCurrent && <Check className="w-2.5 h-2.5 text-white" />}
        </div>

        {/* Version info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {isEditing ? (
              <div className="flex items-center gap-1 flex-1">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onBlur={handleSave}
                  autoFocus
                  className="flex-1 px-2 py-0.5 text-sm bg-surface-700 border border-surface-600 rounded text-surface-200 focus:outline-none focus:border-primary-500"
                  onClick={(e) => e.stopPropagation()}
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSave();
                  }}
                  className="p-1 text-emerald-400 hover:text-emerald-300"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditName(displayName);
                    setIsEditing(false);
                  }}
                  className="p-1 text-surface-400 hover:text-surface-300"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <>
                <span className={cn(
                  'text-sm font-medium truncate',
                  isCurrent ? 'text-primary-300' : 'text-surface-200'
                )}>
                  v{version.version_number} - {displayName}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsEditing(true);
                  }}
                  className="p-1 text-surface-500 hover:text-surface-300 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Pencil className="w-3 h-3" />
                </button>
              </>
            )}
          </div>

          {/* Description */}
          {version.change_description && version.change_description !== displayName && (
            <p className="text-xs text-surface-500 mt-0.5 truncate">
              {version.change_description}
            </p>
          )}

          {/* Stats */}
          <div className="flex items-center gap-3 mt-1.5 text-xs text-surface-500">
            <span className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              {formatNumber(version.summary.shape[0])} × {version.summary.shape[1]}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(version.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export function VersionSelector() {
  const {
    sessionId,
    versions,
    currentVersionId,
    switchVersion: storeSwitch,
    renameVersion,
    getVersionDisplayName,
    setLoading,
    setError,
  } = useAppStore();

  const [isExpanded, setIsExpanded] = useState(true);
  const [isSwitching, setIsSwitching] = useState(false);

  if (versions.length === 0) {
    return null;
  }

  const handleSwitch = async (versionId: string) => {
    if (!sessionId || versionId === currentVersionId || isSwitching) return;

    setIsSwitching(true);
    setError(null);

    try {
      const response = await switchVersion(sessionId, versionId);
      storeSwitch(versionId, response.current_version.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to switch version');
    } finally {
      setIsSwitching(false);
    }
  };

  const currentVersion = versions.find(v => v.version_id === currentVersionId);

  return (
    <div className="glass-light rounded-xl overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-surface-700/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-primary-400" />
          <span className="text-sm font-medium text-surface-300">
            Dataset Versions
          </span>
          <span className="px-1.5 py-0.5 text-xs rounded-full bg-primary-500/20 text-primary-300">
            {versions.length}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-surface-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-surface-400" />
        )}
      </button>

      {/* Current version indicator when collapsed */}
      {!isExpanded && currentVersion && (
        <div className="px-4 pb-3 text-xs text-surface-500">
          Current: v{currentVersion.version_number} - {getVersionDisplayName(currentVersion)}
        </div>
      )}

      {/* Version list */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-surface-700/50 overflow-hidden"
          >
            <div className="p-3 space-y-2 max-h-[300px] overflow-y-auto">
              {versions.map((version) => (
                <div key={version.version_id} className="group">
                  <VersionItem
                    version={version}
                    isCurrent={version.version_id === currentVersionId}
                    displayName={getVersionDisplayName(version)}
                    onSelect={() => handleSwitch(version.version_id)}
                    onRename={(name) => renameVersion(version.version_id, name)}
                  />
                </div>
              ))}
            </div>

            {/* Loading overlay */}
            {isSwitching && (
              <div className="absolute inset-0 bg-surface-900/50 flex items-center justify-center">
                <div className="text-sm text-surface-300">Switching...</div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

