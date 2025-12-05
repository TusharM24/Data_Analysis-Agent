import { motion } from 'framer-motion';
import {
  Table2,
  Hash,
  Type,
  Calendar,
  AlertTriangle,
  HardDrive,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useState } from 'react';
import type { DatasetSummary as DatasetSummaryType } from '../types';
import { formatNumber, cn } from '../lib/utils';

interface Props {
  summary: DatasetSummaryType;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
  delay?: number;
}

function StatCard({ icon, label, value, color, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.3 }}
      className={cn(
        'p-4 rounded-xl glass-light',
        'hover:scale-[1.02] transition-transform duration-200'
      )}
    >
      <div className="flex items-center gap-3">
        <div className={cn('p-2 rounded-lg', color)}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-surface-400">{label}</p>
          <p className="text-xl font-display font-bold text-surface-100">
            {typeof value === 'number' ? formatNumber(value) : value}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

export function DatasetSummary({ summary }: Props) {
  const [showColumns, setShowColumns] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const totalMissing = Object.values(summary.missing_values).reduce((a, b) => a + b, 0);
  const missingPercent = ((totalMissing / (summary.shape[0] * summary.shape[1])) * 100).toFixed(1);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-display font-semibold text-surface-100">
            {summary.filename}
          </h2>
          <p className="text-sm text-surface-400">
            {summary.memory_usage} in memory
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          icon={<Table2 className="w-5 h-5 text-primary-400" />}
          label="Rows"
          value={summary.shape[0]}
          color="bg-primary-500/20"
          delay={0}
        />
        <StatCard
          icon={<Hash className="w-5 h-5 text-accent-400" />}
          label="Columns"
          value={summary.shape[1]}
          color="bg-accent-500/20"
          delay={0.1}
        />
        <StatCard
          icon={<Type className="w-5 h-5 text-emerald-400" />}
          label="Numerical"
          value={summary.numerical_columns.length}
          color="bg-emerald-500/20"
          delay={0.2}
        />
        <StatCard
          icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
          label="Missing"
          value={`${missingPercent}%`}
          color="bg-amber-500/20"
          delay={0.3}
        />
      </div>

      {/* Column Types */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap gap-2"
      >
        {summary.numerical_columns.length > 0 && (
          <span className="px-3 py-1 text-xs rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            {summary.numerical_columns.length} numerical
          </span>
        )}
        {summary.categorical_columns.length > 0 && (
          <span className="px-3 py-1 text-xs rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
            {summary.categorical_columns.length} categorical
          </span>
        )}
        {summary.datetime_columns.length > 0 && (
          <span className="px-3 py-1 text-xs rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
            {summary.datetime_columns.length} datetime
          </span>
        )}
      </motion.div>

      {/* Expandable Columns List */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="glass-light rounded-xl overflow-hidden"
      >
        <button
          onClick={() => setShowColumns(!showColumns)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-surface-700/30 transition-colors"
        >
          <span className="text-sm font-medium text-surface-300">
            Column Details ({summary.columns.length})
          </span>
          {showColumns ? (
            <ChevronUp className="w-4 h-4 text-surface-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-surface-400" />
          )}
        </button>
        
        {showColumns && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            className="border-t border-surface-700/50"
          >
            <div className="max-h-60 overflow-y-auto">
              {summary.columns.map((col, i) => (
                <div
                  key={col.name}
                  className={cn(
                    'px-4 py-2 flex items-center justify-between text-sm',
                    i % 2 === 0 ? 'bg-surface-800/30' : ''
                  )}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-surface-200">{col.name}</span>
                    <span className="px-2 py-0.5 text-xs rounded bg-surface-700/50 text-surface-400">
                      {col.dtype}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-surface-500">
                    <span>{formatNumber(col.unique_count)} unique</span>
                    {col.null_count > 0 && (
                      <span className="text-amber-400">
                        {col.null_count} null
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Expandable Data Preview */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="glass-light rounded-xl overflow-hidden"
      >
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-surface-700/30 transition-colors"
        >
          <span className="text-sm font-medium text-surface-300">
            Data Preview (first 10 rows)
          </span>
          {showPreview ? (
            <ChevronUp className="w-4 h-4 text-surface-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-surface-400" />
          )}
        </button>
        
        {showPreview && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            className="border-t border-surface-700/50 overflow-x-auto"
          >
            <table className="w-full text-xs">
              <thead className="bg-surface-800/50">
                <tr>
                  {summary.columns.slice(0, 8).map((col) => (
                    <th
                      key={col.name}
                      className="px-3 py-2 text-left text-surface-400 font-medium whitespace-nowrap"
                    >
                      {col.name}
                    </th>
                  ))}
                  {summary.columns.length > 8 && (
                    <th className="px-3 py-2 text-surface-500">
                      +{summary.columns.length - 8} more
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {summary.head_preview.map((row, i) => (
                  <tr
                    key={i}
                    className={cn(
                      'border-t border-surface-700/30',
                      i % 2 === 0 ? 'bg-surface-800/20' : ''
                    )}
                  >
                    {summary.columns.slice(0, 8).map((col) => (
                      <td
                        key={col.name}
                        className="px-3 py-2 text-surface-300 whitespace-nowrap max-w-[150px] truncate"
                      >
                        {row[col.name]?.toString() ?? '-'}
                      </td>
                    ))}
                    {summary.columns.length > 8 && (
                      <td className="px-3 py-2 text-surface-500">...</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
}

