import React from 'react';

interface Props {
  label?: string;
}

export function LoadingSpinner({ label = 'Loading...' }: Props) {
  return (
    <div className="flex flex-col items-center justify-center p-8 gap-3" role="status" aria-label={label}>
      <div className="w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin" />
      <span className="text-gray-400 text-sm">{label}</span>
    </div>
  );
}
