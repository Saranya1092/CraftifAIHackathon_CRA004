// SafeZone AI – shared TypeScript types

export interface Coordinate {
  x: number;
  y: number;
}

export interface Zone {
  id: string;
  name: string;
  description: string;
  coordinates: Coordinate[];
  color: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ZoneCreate {
  name: string;
  description?: string;
  coordinates: Coordinate[];
  color?: string;
  is_active?: boolean;
}

export interface ZoneUpdate {
  name?: string;
  description?: string;
  coordinates?: Coordinate[];
  color?: string;
  is_active?: boolean;
}

export type IncidentStatus = 'active' | 'acknowledged' | 'resolved';
export type IncidentSeverity = 'low' | 'medium' | 'high';

export interface DetectionMetadata {
  class?: string;
  confidence?: number;
  bbox?: number[];
  cx?: number;
  cy?: number;
  frame_index?: number;
  [key: string]: unknown;
}

export interface Incident {
  id: string;
  event_type: string;
  zone_id: string | null;
  zone_name: string | null;
  severity: IncidentSeverity;
  status: IncidentStatus;
  confidence: number | null;
  source: string;
  detection_metadata: DetectionMetadata | null;
  frame_timestamp: string | null;
  acknowledged_by: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface IncidentUpdate {
  status?: IncidentStatus;
  acknowledged_by?: string;
  notes?: string;
}

export type MonitoringStatus = 'running' | 'stopped' | 'error';

export interface MonitoringState {
  status: MonitoringStatus;
  start_time: string | null;
  total_detections: number;
  error_message: string | null;
  adapter: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  monitoring: MonitoringState;
  mqtt: {
    connected: boolean;
    broker: string;
    topic_incidents: string;
    error: string | null;
  };
}

export interface Summary {
  total_people_detected: number;
  total_incidents: number;
  active_incidents: number;
  acknowledged_incidents: number;
  resolved_incidents: number;
  active_zones: number;
  monitoring_status: MonitoringStatus;
}

export interface TrendPoint {
  timestamp: string;
  incidents: number;
}

export interface TrendsResponse {
  period: string;
  data: TrendPoint[];
}

export interface ApiError {
  detail: string;
}
