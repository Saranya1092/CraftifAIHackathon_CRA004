import React, { useState, useCallback } from 'react';
import {
  getIncidents, updateIncident, getIncidentsCsvUrl, errorMessage,
} from '../services/api';
import { useApi } from '../hooks/useApi';
import { useSSE } from '../hooks/useSSE';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { EmptyState } from '../components/EmptyState';
import { StatusBadge } from '../components/StatusBadge';
import type { IncidentStatus } from '../types';

export function Incidents() {
  const [filters, setFilters] = useState<{
    status?: string; page: number; page_size: number;
  }>({ page: 1, page_size: 20 });
  const [actionError, setActionError] = useState<string | null>(null);

  const { data, loading, error, refetch } = useApi(
    () => getIncidents(filters),
    [JSON.stringify(filters)],
  );

  useSSE(useCallback((event: unknown) => {
    const e = event as { type?: string };
    if (e?.type === 'incident') refetch();
  }, [refetch]));

  const handleStatusChange = async (id: string, status: IncidentStatus) => {
    try {
      await updateIncident(id, { status });
      refetch();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const csvUrl = getIncidentsCsvUrl({ status: filters.status });

  if (loading) return <LoadingSpinner label="Loading incidents..." />;
  if (error) return <ErrorAlert message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
          <p className="text-gray-400 text-sm">{data?.total ?? 0} total records</p>
        </div>
        <a
          href={csvUrl}
          download="incidents.csv"
          className="px-4 py-2 bg-navy-600 hover:bg-navy-500 text-gray-300 rounded-lg text-sm transition-colors"
        >
          ⬇ Export CSV
        </a>
      </div>

      {actionError && <ErrorAlert message={actionError} onDismiss={() => setActionError(null)} />}

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        {(['', 'active', 'acknowledged', 'resolved'] as const).map((s) => (
          <button
            key={s || 'all'}
            onClick={() => setFilters((f) => ({ ...f, status: s || undefined, page: 1 }))}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              (filters.status ?? '') === s
                ? 'bg-blue-700 text-white'
                : 'bg-navy-700 text-gray-400 hover:text-white hover:bg-navy-600'
            }`}
          >
            {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
          </button>
        ))}
      </div>

      {!data || data.items.length === 0 ? (
        <EmptyState
          icon="✅"
          title="No incidents found"
          description="No incidents match your current filters."
        />
      ) : (
        <>
          <div className="bg-navy-800 rounded-xl border border-navy-600 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-navy-600 text-xs uppercase tracking-wide">
                  <th className="text-left px-4 py-3">ID</th>
                  <th className="text-left px-4 py-3">Type</th>
                  <th className="text-left px-4 py-3">Zone</th>
                  <th className="text-left px-4 py-3">Severity</th>
                  <th className="text-left px-4 py-3">Confidence</th>
                  <th className="text-left px-4 py-3">Source</th>
                  <th className="text-left px-4 py-3">Status</th>
                  <th className="text-left px-4 py-3">Time</th>
                  <th className="text-left px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((inc) => (
                  <tr key={inc.id} className="border-b border-navy-700 hover:bg-navy-700 transition-colors">
                    <td className="px-4 py-2 text-gray-500 font-mono text-xs">{inc.id.slice(0, 8)}…</td>
                    <td className="px-4 py-2 text-gray-200">{inc.event_type}</td>
                    <td className="px-4 py-2 text-gray-400">{inc.zone_name ?? '—'}</td>
                    <td className="px-4 py-2"><StatusBadge status={inc.severity} /></td>
                    <td className="px-4 py-2 text-gray-400">
                      {inc.confidence != null ? `${(inc.confidence * 100).toFixed(0)}%` : '—'}
                    </td>
                    <td className="px-4 py-2">
                      <span className={`font-mono text-xs ${inc.source === 'simulated' ? 'text-yellow-500' : 'text-blue-400'}`}>
                        {inc.source}
                      </span>
                    </td>
                    <td className="px-4 py-2"><StatusBadge status={inc.status} /></td>
                    <td className="px-4 py-2 text-gray-500 text-xs">
                      {new Date(inc.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex gap-1">
                        {inc.status === 'active' && (
                          <button
                            onClick={() => handleStatusChange(inc.id, 'acknowledged')}
                            className="px-2 py-0.5 text-xs rounded bg-yellow-800 hover:bg-yellow-700 text-yellow-200 transition-colors"
                          >
                            Ack
                          </button>
                        )}
                        {inc.status !== 'resolved' && (
                          <button
                            onClick={() => handleStatusChange(inc.id, 'resolved')}
                            className="px-2 py-0.5 text-xs rounded bg-green-800 hover:bg-green-700 text-green-200 transition-colors"
                          >
                            Resolve
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex items-center gap-2 justify-center">
              <button
                disabled={data.page === 1}
                onClick={() => setFilters((f) => ({ ...f, page: f.page - 1 }))}
                className="px-3 py-1.5 rounded bg-navy-700 text-gray-400 disabled:opacity-40 hover:bg-navy-600 text-sm"
              >
                ← Prev
              </button>
              <span className="text-gray-400 text-sm">
                Page {data.page} of {data.total_pages}
              </span>
              <button
                disabled={data.page === data.total_pages}
                onClick={() => setFilters((f) => ({ ...f, page: f.page + 1 }))}
                className="px-3 py-1.5 rounded bg-navy-700 text-gray-400 disabled:opacity-40 hover:bg-navy-600 text-sm"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
