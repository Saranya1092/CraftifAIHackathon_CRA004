import React from 'react';
import type { IncidentStatus, MonitoringStatus } from '../types';

interface Props {
  status: IncidentStatus | MonitoringStatus | string;
  size?: 'sm' | 'md';
}

const COLOR_MAP: Record<string, string> = {
  active: 'bg-red-600 text-white',
  acknowledged: 'bg-yellow-500 text-black',
  resolved: 'bg-green-600 text-white',
  running: 'bg-green-500 text-white',
  stopped: 'bg-gray-500 text-white',
  error: 'bg-red-700 text-white',
  high: 'bg-red-600 text-white',
  medium: 'bg-orange-500 text-white',
  low: 'bg-yellow-500 text-black',
};

export function StatusBadge({ status, size = 'sm' }: Props) {
  const color = COLOR_MAP[status] ?? 'bg-gray-600 text-white';
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';
  return (
    <span className={`inline-flex items-center rounded-full font-semibold uppercase tracking-wide ${sizeClass} ${color}`}>
      {status}
    </span>
  );
}
