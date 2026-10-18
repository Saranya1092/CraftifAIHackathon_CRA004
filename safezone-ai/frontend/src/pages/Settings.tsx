import React from 'react';
import { getHealth } from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';

function SettingRow({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-navy-700 last:border-0">
      <span className="text-gray-400 text-sm">{label}</span>
      <span className={`font-mono text-sm ${highlight ? 'text-green-400' : 'text-gray-200'}`}>{value}</span>
    </div>
  );
}

function StatusIndicator({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`w-3 h-3 rounded-full ${ok ? 'bg-green-400' : 'bg-red-500'}`} aria-hidden />
      <span className={`text-sm font-medium ${ok ? 'text-green-400' : 'text-red-400'}`}>{label}</span>
    </div>
  );
}

export function Settings() {
  const { data: health, loading, error, refetch } = useApi(getHealth);

  if (loading) return <LoadingSpinner label="Checking system status..." />;
  if (error) return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white">Settings</h1>
      <ErrorAlert message={`Cannot reach backend: ${error}`} />
      <button onClick={refetch} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 text-sm">System status and configuration overview</p>
      </div>

      {/* System health */}
      <div className="bg-navy-800 border border-navy-600 rounded-xl p-5 space-y-3">
        <h2 className="text-white font-semibold">System Health</h2>
        <StatusIndicator ok={health?.status === 'ok'} label={`Backend: ${health?.status}`} />
        <StatusIndicator ok={!!health?.mqtt.connected} label={`MQTT: ${health?.mqtt.connected ? 'Connected' : 'Disconnected'}`} />
        {health?.mqtt.error && (
          <p className="text-red-400 text-xs ml-5">Error: {health.mqtt.error}</p>
        )}
        <StatusIndicator
          ok={health?.monitoring.status === 'running'}
          label={`Monitoring: ${health?.monitoring.status}`}
        />
      </div>

      {/* Backend info */}
      <div className="bg-navy-800 border border-navy-600 rounded-xl p-5">
        <h2 className="text-white font-semibold mb-3">Backend</h2>
        <SettingRow label="API Version" value={health?.version ?? '—'} />
        <SettingRow label="Perception Adapter" value={health?.monitoring.adapter ?? '—'} highlight={health?.monitoring.adapter === 'pipegen'} />
        <SettingRow label="Total Detections" value={String(health?.monitoring.total_detections ?? 0)} />
      </div>

      {/* MQTT info */}
      <div className="bg-navy-800 border border-navy-600 rounded-xl p-5">
        <h2 className="text-white font-semibold mb-3">MQTT</h2>
        <SettingRow label="Broker" value={health?.mqtt.broker ?? '—'} />
        <SettingRow label="Incidents Topic" value={health?.mqtt.topic_incidents ?? '—'} />
        <SettingRow label="Status" value={health?.mqtt.connected ? 'Connected' : 'Disconnected'} />
        <p className="text-gray-500 text-xs mt-3">
          Configure MQTT settings via environment variables (see .env.example). Credentials are never shown here.
        </p>
      </div>

      {/* PipeGen notice */}
      <div className="bg-navy-800 border border-yellow-700/40 rounded-xl p-5">
        <h2 className="text-white font-semibold mb-2">Perception Engine</h2>
        {health?.monitoring.adapter === 'simulated' ? (
          <>
            <div className="flex items-center gap-2 text-yellow-400 mb-2">
              <span>⚠</span>
              <span className="text-sm font-medium">Running in simulated mode</span>
            </div>
            <p className="text-gray-400 text-sm">
              The perception engine is in simulated mode. No real AI inference is occurring.
              To use the actual PipeGen/DeepStream pipeline, set{' '}
              <code className="bg-navy-700 px-1 rounded text-xs">PERCEPTION_ADAPTER=pipegen</code>{' '}
              and follow the instructions in <code className="bg-navy-700 px-1 rounded text-xs">pipegen/README.md</code>.
            </p>
          </>
        ) : (
          <>
            <div className="flex items-center gap-2 text-green-400 mb-2">
              <span>✓</span>
              <span className="text-sm font-medium">PipeGen adapter active</span>
            </div>
            <p className="text-gray-400 text-sm">
              Connected to PipeGen/DeepStream output. Ensure the pipeline is running and writing to the
              configured output directory.
            </p>
          </>
        )}
      </div>

      <button
        onClick={refetch}
        className="px-4 py-2 bg-navy-700 hover:bg-navy-600 text-gray-300 rounded-lg text-sm transition-colors"
      >
        Refresh Status
      </button>
    </div>
  );
}
