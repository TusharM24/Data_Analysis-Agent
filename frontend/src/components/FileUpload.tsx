import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileSpreadsheet, AlertCircle, Loader2 } from 'lucide-react';
import { cn } from '../lib/utils';
import { uploadFile } from '../lib/api';
import { useAppStore } from '../lib/store';

export function FileUpload() {
  const { setSession, setUploading, setError, isUploading, error } = useAppStore();
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      try {
        const response = await uploadFile(file, (percent) => {
          setUploadProgress(percent);
        });
        setSession(response.session_id, response.summary, response.version);
      } catch (err) {
        let message = 'Failed to upload file';
        if (err instanceof Error) {
          // Check for timeout errors
          if (err.message.includes('timeout') || err.message.includes('ECONNABORTED')) {
            message = 'Upload timed out. Please try a smaller file or check your connection.';
          } else if (err.message.includes('Network Error')) {
            message = 'Network error. Please check your connection and try again.';
          } else {
            message = err.message;
          }
        }
        setError(message);
      } finally {
        setUploading(false);
        setUploadProgress(0);
      }
    },
    [setSession, setUploading, setError]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div
        {...getRootProps()}
        className={cn(
          'relative overflow-hidden rounded-2xl transition-all duration-300 cursor-pointer group',
          'border-2 border-dashed',
          isDragActive && !isDragReject && 'border-primary-400 bg-primary-500/10 scale-[1.02]',
          isDragReject && 'border-red-500 bg-red-500/10',
          !isDragActive && 'border-surface-600 hover:border-primary-500/50 hover:bg-surface-800/50',
          isUploading && 'pointer-events-none opacity-70'
        )}
      >
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        {/* Grid pattern background */}
        <div className="absolute inset-0 bg-grid-pattern opacity-30" />
        
        <input {...getInputProps()} />
        
        <div className="relative z-10 p-12 flex flex-col items-center justify-center text-center">
          <AnimatePresence mode="wait">
            {isUploading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex flex-col items-center gap-4"
              >
                <div className="relative">
                  <Loader2 className="w-16 h-16 text-primary-400 animate-spin" />
                  <div className="absolute inset-0 blur-xl bg-primary-400/30 animate-pulse" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-medium text-surface-300">
                    {uploadProgress < 100 ? 'Uploading...' : 'Analyzing your dataset...'}
                  </p>
                  {uploadProgress > 0 && uploadProgress < 100 && (
                    <div className="mt-3 w-48">
                      <div className="flex justify-between text-xs text-surface-400 mb-1">
                        <span>Progress</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <div className="w-full h-2 bg-surface-700 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-primary-500 to-accent-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${uploadProgress}%` }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : isDragActive ? (
              <motion.div
                key="drag"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="flex flex-col items-center gap-4"
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                >
                  <FileSpreadsheet className="w-16 h-16 text-primary-400" />
                </motion.div>
                <p className="text-lg font-medium text-primary-300">
                  {isDragReject ? 'This file type is not supported' : 'Drop your file here!'}
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="default"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-6"
              >
                <div className="relative">
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 group-hover:from-primary-500/30 group-hover:to-accent-500/30 transition-all duration-300">
                    <Upload className="w-12 h-12 text-primary-300 group-hover:text-primary-200 transition-colors" />
                  </div>
                  <div className="absolute -inset-1 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                </div>
                
                <div className="space-y-2">
                  <p className="text-xl font-display font-semibold text-surface-100">
                    Upload your dataset
                  </p>
                  <p className="text-surface-400 max-w-sm">
                    Drag and drop your CSV or Excel file here, or click to browse
                  </p>
                </div>
                
                <div className="flex items-center gap-3 text-sm text-surface-500">
                  <span className="px-3 py-1 rounded-full bg-surface-800/80 border border-surface-700">
                    .csv
                  </span>
                  <span className="px-3 py-1 rounded-full bg-surface-800/80 border border-surface-700">
                    .xlsx
                  </span>
                  <span className="px-3 py-1 rounded-full bg-surface-800/80 border border-surface-700">
                    .xls
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4 flex items-center gap-2 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

