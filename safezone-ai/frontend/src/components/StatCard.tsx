import React from 'react';

interface Props {
  label: string;
  value: number | string;
  icon?: string;
  color?: 'red' | 'yellow' | 'green' | 'blue' | 'gray';
  description?: string;
}

const colorMap = {
  red: 'border-red-600 text-red-400',
  yellow: 'border-yellow-500 text-yellow-400',
  green: 'border-green-500 text-green-400',
  blue: 'border-blue-500 text-blue-400',
  gray: 'border-gray-600 text-gray-400',
};

export function StatCard({ label, value, icon, color = 'blue', description }: Props) {
  const colorClass = colorMap[color];
  return (
    <div
      className={`bg-navy-800 border-l-4 ${colorClass} rounded-lg p-4 flex flex-col gap-1`}
      role="region"
      aria-label={label}
    >
      <div className="flex items-center justify-between">
        <span className="text-gray-400 text-xs font-medium uppercase tracking-wider">{label}</span>
        {icon && <span className="text-xl" aria-hidden>{icon}</span>}
      </div>
      <span className={`text-3xl font-bold ${colorClass.split(' ')[1]}`}>{value}</span>
      {description && <span className="text-gray-500 text-xs">{description}</span>}
    </div>
  );
}
