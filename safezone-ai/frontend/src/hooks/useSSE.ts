/**
 * Subscribes to the backend Server-Sent Events stream.
 * Calls onEvent whenever a new event arrives.
 */
import { useEffect } from 'react';

const SSE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api') + '/events/stream';

export function useSSE(onEvent: (event: unknown) => void): void {
  useEffect(() => {
    let es: EventSource | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      es = new EventSource(SSE_URL);
      es.onmessage = (e) => {
        try {
          onEvent(JSON.parse(e.data));
        } catch {
          // ignore malformed events
        }
      };
      es.onerror = () => {
        es?.close();
        reconnectTimer = setTimeout(connect, 5000);
      };
    }

    connect();
    return () => {
      clearTimeout(reconnectTimer);
      es?.close();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
