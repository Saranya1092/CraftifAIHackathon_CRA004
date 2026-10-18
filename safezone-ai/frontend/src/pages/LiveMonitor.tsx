import React, { useState, useCallback } from 'react';
import {
  getMonitoringStatus, startMonitoring, stopMonitoring, errorMessage,
} from '../services/api';
import { useApi } from '../hooks/useApi';
import { useSSE } from '../hooks/useSSE';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { StatusBadge } from '../components/StatusBadge';
import type { MonitoringState } from '../types';

export function LiveMonitor() {
  const { data: status, loading, error, refetch } = useApi(getMonitoringStatus);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [recentEvents, setRecentEvents] = useState<string[]>([]);

  useSSE(useCallback((event: unknown) => {
    const e = event as { type?: string; incident_id?: string };
    if (e?.type === 'incident') {
      setRecentEvents((prev) => [`Incident ${e.incident_id?.slice(0, 8)}…`, ...prev].slice(0, 10));
      refetch();
    }
  }, [refetch]));

  const handleStart = async () => {
    setActionLoading(true);
    setActionError(null);
    try {
      await startMonitoring();
      refetch();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setActionLoading(false);
    }
  };

  const handleStop = async () => {
    setActionLoading(true);
    setActionError(null);
    try {
      await stopMonitoring();
      refetch();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading monitoring status..." />;
  if (error) return <ErrorAlert message={error} />;

  const isRunning = status?.status === 'running';
  const isError = status?.status === 'error';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Live Monitor</h1>
        <p className="text-gray-400 text-sm">Control and observe the perception pipeline</p>
      </div>

      {actionError && <ErrorAlert message={actionError} onDismiss={() => setActionError(null)} />}

      {/* Status + controls */}
      <div className="bg-navy-800 rounded-xl border border-navy-600 p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4 justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <StatusBadge status={status?.status ?? 'stopped'} size="md" />
            {isRunning && (
              <span className="flex items-center gap-1 text-green-400 text-xs">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse inline-block" />
                Live
              </span>
            )}
          </div>
          <p className="text-gray-400 text-sm">
            Adapter: <span className="text-gray-200 font-mono">{status?.adapter}</span>
            {status?.adapter === 'simulated' && (
              <span className="ml-2 text-yellow-500 text-xs">(⚠ Simulated — not real inference)</span>
            )}
          </p>
          {status?.start_time && (
            <p className="text-gray-500 text-xs">
              Started: {new Date(status.start_time).toLocaleString()}
            </p>
          )}
          <p className="text-gray-500 text-xs">
            Total detections: <span className="text-gray-300">{status?.total_detections ?? 0}</span>
          </p>
          {isError && status?.error_message && (
            <p className="text-red-400 text-xs mt-1">Error: {status.error_message}</p>
          )}
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleStart}
            disabled={isRunning || actionLoading}
            className="px-5 py-2 rounded-lg bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white font-semibold text-sm transition-colors"
          >
            {actionLoading && !isRunning ? '…' : '▶ Start'}
          </button>
          <button
            onClick={handleStop}
            disabled={!isRunning || actionLoading}
            className="px-5 py-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:opacity-40 text-white font-semibold text-sm transition-colors"
          >
            {actionLoading && isRunning ? '…' : '■ Stop'}
          </button>
        </div>
      </div>

      {/* Video placeholder */}
      <div className="bg-navy-800 rounded-xl border border-navy-600 overflow-hidden">
        <div className="relative bg-black aspect-video flex items-center justify-center min-h-[300px]">
          {isRunning ? (
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-green-400 font-semibold">Pipeline Running</p>
              <p className="text-gray-500 text-sm max-w-sm">
                {status?.adapter === 'pipegen'
                  ? 'Live video from DeepStream pipeline'
                  : 'Simulated detections active. Connect a real PipeGen pipeline for live video.'}
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 text-center">
              <span className="text-6xl opacity-30">📷</span>
              <p className="text-gray-500">
                {isError ? 'Pipeline error – check logs' : 'Press Start to begin monitoring'}
              </p>
              {status?.adapter === 'simulated' && (
                <p className="text-yellow-500/70 text-xs max-w-xs">
                  Running in simulated mode. Set PERCEPTION_ADAPTER=pipegen for real inference.
                </p>
              )}
            </div>
          )}

          {/* LIVE badge */}
          {isRunning && (
            <div className="absolute top-3 left-3 flex items-center gap-1 bg-red-600 rounded px-2 py-0.5">
              <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
              <span className="text-white text-xs font-bold">LIVE</span>
            </div>
          )}

          {/* SIMULATED badge */}
          {status?.adapter === 'simulated' && isRunning && (
            <div className="absolute top-3 right-3 bg-yellow-600/80 rounded px-2 py-0.5">
              <span className="text-white text-xs font-bold">SIMULATED</span>
            </div>
          )}
        </div>
      </div>

      {/* Recent events feed */}
      <div className="bg-navy-800 rounded-xl border border-navy-600 p-4">
        <h2 className="text-white font-semibold mb-3">Recent Events</h2>
        {recentEvents.length === 0 ? (
          <p className="text-gray-500 text-sm">No events received in this session.</p>
        ) : (
          <ul className="space-y-1">
            {recentEvents.map((evt, i) => (
              <li key={i} className="text-gray-300 text-sm font-mono border-b border-navy-700 py-1">
                <span className="text-red-400">⚡</span> {evt}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
