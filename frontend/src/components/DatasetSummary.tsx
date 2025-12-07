import {
  Table2,
  Hash,
  Type,
  AlertTriangle,
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
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div
      className={cn(
        'p-2.5 rounded-lg bg-surface-800/50 border border-surface-700/30',
        'flex items-center gap-2'
      )}
    >
      <div className={cn('p-1.5 rounded-md', color)}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs text-surface-500 truncate">{label}</p>
        <p className="text-sm font-semibold text-surface-200">
          {typeof value === 'number' ? formatNumber(value) : value}
        </p>
      </div>
    </div>
  );
}

export function DatasetSummary({ summary }: Props) {
  const [showColumns, setShowColumns] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const totalMissing = Object.values(summary.missing_values).reduce((a, b) => a + b, 0);
  const missingPercent = ((totalMissing / (summary.shape[0] * summary.shape[1])) * 100).toFixed(1);

  return (
    <div className="space-y-3">
      {/* Header */}
      <div>
        <h2 className="text-sm font-display font-semibold text-surface-100 truncate" title={summary.filename}>
          {summary.filename}
        </h2>
        <p className="text-xs text-surface-500">
          {summary.memory_usage}
        </p>
      </div>

      {/* Stats Grid - 2x2 */}
      <div className="grid grid-cols-2 gap-2">
        <StatCard
          icon={<Table2 className="w-3.5 h-3.5 text-primary-400" />}
          label="Rows"
          value={summary.shape[0]}
          color="bg-primary-500/20"
        />
        <StatCard
          icon={<Hash className="w-3.5 h-3.5 text-accent-400" />}
          label="Columns"
          value={summary.shape[1]}
          color="bg-accent-500/20"
        />
        <StatCard
          icon={<Type className="w-3.5 h-3.5 text-emerald-400" />}
          label="Numerical"
          value={summary.numerical_columns.length}
          color="bg-emerald-500/20"
        />
        <StatCard
          icon={<AlertTriangle className="w-3.5 h-3.5 text-amber-400" />}
          label="Missing"
          value={`${missingPercent}%`}
          color="bg-amber-500/20"
        />
      </div>

      {/* Column Type Tags */}
      <div className="flex flex-wrap gap-1.5">
        {summary.numerical_columns.length > 0 && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            {summary.numerical_columns.length} num
          </span>
        )}
        {summary.categorical_columns.length > 0 && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
            {summary.categorical_columns.length} cat
          </span>
        )}
        {summary.datetime_columns.length > 0 && (
          <span className="px-2 py-0.5 text-xs rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
            {summary.datetime_columns.length} date
          </span>
        )}
      </div>

      {/* Expandable Columns List */}
      <div className="bg-surface-800/30 rounded-lg overflow-hidden border border-surface-700/30">
        <button
          onClick={() => setShowColumns(!showColumns)}
          className="w-full px-3 py-2 flex items-center justify-between hover:bg-surface-700/30 transition-colors text-left"
        >
          <span className="text-xs font-medium text-surface-400">
            Columns ({summary.columns.length})
          </span>
          {showColumns ? (
            <ChevronUp className="w-3.5 h-3.5 text-surface-500" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-surface-500" />
          )}
        </button>
        
        {showColumns && (
          <div className="border-t border-surface-700/30 max-h-48 overflow-y-auto">
            {summary.columns.map((col, i) => (
              <div
                key={col.name}
                className={cn(
                  'px-3 py-1.5 flex items-center justify-between text-xs',
                  i % 2 === 0 ? 'bg-surface-800/20' : ''
                )}
              >
                <div className="flex items-center gap-1.5 min-w-0 flex-1">
                  <span className="font-mono text-surface-300 truncate" title={col.name}>
                    {col.name}
                  </span>
                  <span className="px-1.5 py-0.5 text-[10px] rounded bg-surface-700/50 text-surface-500 flex-shrink-0">
                    {col.dtype}
                  </span>
                </div>
                {col.null_count > 0 && (
                  <span className="text-amber-400 text-[10px] flex-shrink-0 ml-1">
                    {col.null_count} null
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Expandable Data Preview */}
      <div className="bg-surface-800/30 rounded-lg overflow-hidden border border-surface-700/30">
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="w-full px-3 py-2 flex items-center justify-between hover:bg-surface-700/30 transition-colors text-left"
        >
          <span className="text-xs font-medium text-surface-400">
            Preview (first 5 rows)
          </span>
          {showPreview ? (
            <ChevronUp className="w-3.5 h-3.5 text-surface-500" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-surface-500" />
          )}
        </button>
        
        {showPreview && (
          <div className="border-t border-surface-700/30 overflow-x-auto">
            <table className="w-full text-[10px]">
              <thead className="bg-surface-800/50">
                <tr>
                  {summary.columns.slice(0, 5).map((col) => (
                    <th
                      key={col.name}
                      className="px-2 py-1.5 text-left text-surface-400 font-medium whitespace-nowrap"
                    >
                      {col.name}
                    </th>
                  ))}
                  {summary.columns.length > 5 && (
                    <th className="px-2 py-1.5 text-surface-500">
                      +{summary.columns.length - 5}
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {summary.head_preview.slice(0, 5).map((row, i) => (
                  <tr
                    key={i}
                    className={cn(
                      'border-t border-surface-700/30',
                      i % 2 === 0 ? 'bg-surface-800/20' : ''
                    )}
                  >
                    {summary.columns.slice(0, 5).map((col) => (
                      <td
                        key={col.name}
                        className="px-2 py-1 text-surface-300 whitespace-nowrap max-w-[100px] truncate"
                        title={row[col.name]?.toString()}
                      >
                        {row[col.name]?.toString() ?? '-'}
                      </td>
                    ))}
                    {summary.columns.length > 5 && (
                      <td className="px-2 py-1 text-surface-500">...</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
