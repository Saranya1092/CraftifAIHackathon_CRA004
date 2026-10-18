/**
 * SafeZone AI – centralised API client.
 * All calls go through this module; never import axios directly in pages.
 */
import axios, { AxiosError } from 'axios';
import type {
  HealthResponse,
  Incident,
  IncidentListResponse,
  IncidentUpdate,
  MonitoringState,
  Summary,
  TrendsResponse,
  Zone,
  ZoneCreate,
  ZoneUpdate,
} from '../types';

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api';

const client = axios.create({ baseURL: BASE, timeout: 15_000 });

function errorMessage(err: unknown): string {
  if (err instanceof AxiosError) {
    return err.response?.data?.detail ?? err.message;
  }
  return String(err);
}

// ── Health ──────────────────────────────────────────────────────────────────

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await client.get<HealthResponse>('/health');
  return data;
}

// ── Monitoring ───────────────────────────────────────────────────────────────

export async function getMonitoringStatus(): Promise<MonitoringState> {
  const { data } = await client.get<MonitoringState>('/monitoring/status');
  return data;
}

export async function startMonitoring(): Promise<void> {
  await client.post('/monitoring/start');
}

export async function stopMonitoring(): Promise<void> {
  await client.post('/monitoring/stop');
}

// ── Zones ────────────────────────────────────────────────────────────────────

export async function getZones(): Promise<Zone[]> {
  const { data } = await client.get<Zone[]>('/zones');
  return data;
}

export async function createZone(zone: ZoneCreate): Promise<Zone> {
  const { data } = await client.post<Zone>('/zones', zone);
  return data;
}

export async function updateZone(id: string, zone: ZoneUpdate): Promise<Zone> {
  const { data } = await client.put<Zone>(`/zones/${id}`, zone);
  return data;
}

export async function deleteZone(id: string): Promise<void> {
  await client.delete(`/zones/${id}`);
}

// ── Incidents ────────────────────────────────────────────────────────────────

export interface IncidentFilters {
  status?: string;
  event_type?: string;
  zone_id?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

export async function getIncidents(filters: IncidentFilters = {}): Promise<IncidentListResponse> {
  const { data } = await client.get<IncidentListResponse>('/incidents', { params: filters });
  return data;
}

export async function getIncident(id: string): Promise<Incident> {
  const { data } = await client.get<Incident>(`/incidents/${id}`);
  return data;
}

export async function updateIncident(id: string, update: IncidentUpdate): Promise<Incident> {
  const { data } = await client.patch<Incident>(`/incidents/${id}`, update);
  return data;
}

// ── Analytics ────────────────────────────────────────────────────────────────

export async function getSummary(): Promise<Summary> {
  const { data } = await client.get<Summary>('/analytics/summary');
  return data;
}

export async function getTrends(period: '24h' | '7d' | '30d' = '24h'): Promise<TrendsResponse> {
  const { data } = await client.get<TrendsResponse>('/analytics/trends', { params: { period } });
  return data;
}

// ── Export ───────────────────────────────────────────────────────────────────

export function getIncidentsCsvUrl(filters: { status?: string } = {}): string {
  const params = new URLSearchParams();
  if (filters.status) params.set('status', filters.status);
  return `${BASE}/export/incidents.csv?${params.toString()}`;
}

export { errorMessage };
