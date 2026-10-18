import React from 'react';

interface Props {
  message: string;
  onDismiss?: () => void;
}

export function ErrorAlert({ message, onDismiss }: Props) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 bg-red-900/40 border border-red-700 rounded-lg p-4"
    >
      <span className="text-red-400 text-xl" aria-hidden>⚠</span>
      <div className="flex-1">
        <p className="text-red-200 text-sm">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-200 text-lg leading-none"
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </div>
  );
}
