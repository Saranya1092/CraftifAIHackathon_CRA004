import React, { useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { getSummary, getTrends, getIncidents } from '../services/api';
import { useApi } from '../hooks/useApi';
import { useSSE } from '../hooks/useSSE';
import { StatCard } from '../components/StatCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { StatusBadge } from '../components/StatusBadge';

export function Dashboard() {
  const { data: summary, loading: sl, error: se, refetch: refetchSummary } = useApi(getSummary);
  const { data: trends, loading: tl, refetch: refetchTrends } = useApi(() => getTrends('24h'));
  const { data: recentIncidents, refetch: refetchIncidents } = useApi(
    () => getIncidents({ page: 1, page_size: 5 })
  );

  // Refresh stats on SSE incident events
  useSSE(useCallback((event: unknown) => {
    const e = event as { type?: string };
    if (e?.type === 'incident') {
      refetchSummary();
      refetchIncidents();
    }
  }, [refetchSummary, refetchIncidents]));

  if (sl) return <LoadingSpinner label="Loading dashboard..." />;
  if (se) return <ErrorAlert message={se} />;

  const chartData = trends?.data.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    incidents: p.incidents,
  })) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Dashboard</h1>
        <p className="text-gray-400 text-sm">Real-time workplace safety overview</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard label="People Detected" value={summary?.total_people_detected ?? 0} icon="👤" color="blue" />
        <StatCard label="Total Incidents" value={summary?.total_incidents ?? 0} icon="⚡" color="red" />
        <StatCard label="Active" value={summary?.active_incidents ?? 0} icon="🔴" color="red" />
        <StatCard label="Acknowledged" value={summary?.acknowledged_incidents ?? 0} icon="🟡" color="yellow" />
        <StatCard label="Resolved" value={summary?.resolved_incidents ?? 0} icon="✅" color="green" />
        <StatCard label="Active Zones" value={summary?.active_zones ?? 0} icon="📍" color="blue" />
      </div>

      {/* Monitoring status pill */}
      <div className="flex items-center gap-3">
        <span className="text-gray-400 text-sm">Monitoring:</span>
        <StatusBadge status={summary?.monitoring_status ?? 'stopped'} size="md" />
      </div>

      {/* Trend chart */}
      <div className="bg-navy-800 rounded-xl border border-navy-600 p-4">
        <h2 className="text-white font-semibold mb-4">Incident Trend (last 24h)</h2>
        {tl ? (
          <div className="h-48 flex items-center justify-center text-gray-500">Loading chart…</div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d47" />
              <XAxis dataKey="time" tick={{ fill: '#9ca3af', fontSize: 11 }} interval="preserveStartEnd" />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: '#0d1224', border: '1px solid #1e2d47', borderRadius: 8 }}
                labelStyle={{ color: '#e5e7eb' }}
                itemStyle={{ color: '#f87171' }}
              />
              <Line type="monotone" dataKey="incidents" stroke="#ef4444" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Recent incidents */}
      <div className="bg-navy-800 rounded-xl border border-navy-600 p-4">
        <h2 className="text-white font-semibold mb-4">Recent Incidents</h2>
        {!recentIncidents || recentIncidents.items.length === 0 ? (
          <p className="text-gray-500 text-sm py-4 text-center">No incidents recorded yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-navy-600">
                  <th className="text-left py-2 pr-4">Type</th>
                  <th className="text-left py-2 pr-4">Zone</th>
                  <th className="text-left py-2 pr-4">Severity</th>
                  <th className="text-left py-2 pr-4">Status</th>
                  <th className="text-left py-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {recentIncidents.items.map((inc) => (
                  <tr key={inc.id} className="border-b border-navy-700 hover:bg-navy-700 transition-colors">
                    <td className="py-2 pr-4 text-gray-200">{inc.event_type}</td>
                    <td className="py-2 pr-4 text-gray-400">{inc.zone_name ?? '—'}</td>
                    <td className="py-2 pr-4"><StatusBadge status={inc.severity} /></td>
                    <td className="py-2 pr-4"><StatusBadge status={inc.status} /></td>
                    <td className="py-2 text-gray-500">
                      {new Date(inc.created_at).toLocaleTimeString()}
                    </td>
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
