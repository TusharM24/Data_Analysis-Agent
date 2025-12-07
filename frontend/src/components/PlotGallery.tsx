import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, X, Download, Maximize2, ImageIcon, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../lib/utils';
import { getPlotUrl, downloadImage } from '../lib/api';
import { useAppStore } from '../lib/store';

interface FullscreenModalProps {
  plotUrl: string;
  onClose: () => void;
}

function FullscreenModal({ plotUrl, onClose }: FullscreenModalProps) {
  const handleDownload = () => {
    const filename = `plot-${Date.now()}.png`;
    downloadImage(plotUrl, filename);
  };

  const handleOpenInNewTab = () => {
    window.open(plotUrl, '_blank', 'noopener,noreferrer');
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="relative max-w-[90vw] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <img
          src={plotUrl}
          alt="Plot fullscreen"
          className="max-w-full max-h-[90vh] object-contain rounded-lg"
        />
        
        <button
          onClick={onClose}
          className="absolute -top-2 -right-2 p-2 rounded-full bg-surface-800 border border-surface-700 text-surface-300 hover:text-white hover:bg-surface-700 transition-colors"
          title="Close"
        >
          <X className="w-5 h-5" />
        </button>
        
        {/* Download and Open in New Tab buttons */}
        <div className="absolute -bottom-2 -right-2 flex gap-2">
          <button
            onClick={handleOpenInNewTab}
            className="p-2 rounded-full bg-surface-700 text-white hover:bg-surface-600 transition-colors"
            title="Open in new tab"
          >
            <ExternalLink className="w-5 h-5" />
          </button>
          <button
            onClick={handleDownload}
            className="p-2 rounded-full bg-primary-600 text-white hover:bg-primary-500 transition-colors"
            title="Download image"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export function PlotGallery() {
  const { allPlots, selectedPlotIndex, setSelectedPlot } = useAppStore();
  const [fullscreenPlot, setFullscreenPlot] = useState<string | null>(null);

  if (allPlots.length === 0) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-6">
        <div className="p-4 rounded-2xl bg-surface-800/50 mb-4">
          <ImageIcon className="w-10 h-10 text-surface-500" />
        </div>
        <p className="text-surface-400 text-sm font-medium">
          No visualizations yet
        </p>
        <p className="text-surface-500 text-xs mt-1 max-w-[200px]">
          Ask the agent to create charts, plots, or graphs to see them here
        </p>
      </div>
    );
  }

  const currentPlot = allPlots[selectedPlotIndex];

  const goToPrevious = () => {
    setSelectedPlot(Math.max(0, selectedPlotIndex - 1));
  };

  const goToNext = () => {
    setSelectedPlot(Math.min(allPlots.length - 1, selectedPlotIndex + 1));
  };

  return (
    <div className="h-full flex flex-col">
      {/* Main Plot Display */}
      <div className="flex-1 relative flex items-center justify-center p-4 min-h-0">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPlot}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="relative group w-full h-full flex items-center justify-center"
          >
            <img
              src={getPlotUrl(currentPlot)}
              alt={`Plot ${selectedPlotIndex + 1}`}
              className="max-w-full max-h-full object-contain rounded-lg border border-surface-700/50 cursor-pointer hover:border-primary-500/50 transition-colors"
              onClick={() => setFullscreenPlot(getPlotUrl(currentPlot))}
            />
            
            {/* Hover overlay with actions */}
            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center gap-3 pointer-events-none">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFullscreenPlot(getPlotUrl(currentPlot));
                }}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors pointer-events-auto"
                title="View fullscreen"
              >
                <Maximize2 className="w-5 h-5 text-white" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  window.open(getPlotUrl(currentPlot), '_blank', 'noopener,noreferrer');
                }}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors pointer-events-auto"
                title="Open in new tab"
              >
                <ExternalLink className="w-5 h-5 text-white" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  downloadImage(getPlotUrl(currentPlot), `plot-${selectedPlotIndex + 1}.png`);
                }}
                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors pointer-events-auto"
                title="Download image"
              >
                <Download className="w-5 h-5 text-white" />
              </button>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Navigation Arrows */}
        {allPlots.length > 1 && (
          <>
            <button
              onClick={goToPrevious}
              disabled={selectedPlotIndex === 0}
              className={cn(
                'absolute left-1 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-all',
                'bg-surface-800/80 border border-surface-700/50',
                'hover:bg-surface-700 hover:border-surface-600',
                'disabled:opacity-30 disabled:cursor-not-allowed'
              )}
            >
              <ChevronLeft className="w-4 h-4 text-surface-300" />
            </button>
            
            <button
              onClick={goToNext}
              disabled={selectedPlotIndex === allPlots.length - 1}
              className={cn(
                'absolute right-1 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition-all',
                'bg-surface-800/80 border border-surface-700/50',
                'hover:bg-surface-700 hover:border-surface-600',
                'disabled:opacity-30 disabled:cursor-not-allowed'
              )}
            >
              <ChevronRight className="w-4 h-4 text-surface-300" />
            </button>
          </>
        )}
      </div>

      {/* Thumbnails - Horizontal scroll */}
      {allPlots.length > 1 && (
        <div className="p-3 border-t border-surface-800/50 flex-shrink-0">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {allPlots.map((plot, index) => (
              <button
                key={plot}
                onClick={() => setSelectedPlot(index)}
                className={cn(
                  'flex-shrink-0 w-14 h-10 rounded-lg overflow-hidden border-2 transition-all',
                  index === selectedPlotIndex
                    ? 'border-primary-500 ring-2 ring-primary-500/30'
                    : 'border-surface-700/50 hover:border-surface-600 opacity-60 hover:opacity-100'
                )}
              >
                <img
                  src={getPlotUrl(plot)}
                  alt={`Thumbnail ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>
          
          {/* Counter */}
          <p className="text-xs text-surface-500 text-center mt-2">
            {selectedPlotIndex + 1} / {allPlots.length}
          </p>
        </div>
      )}

      {/* Fullscreen Modal */}
      <AnimatePresence>
        {fullscreenPlot && (
          <FullscreenModal
            plotUrl={fullscreenPlot}
            onClose={() => setFullscreenPlot(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
