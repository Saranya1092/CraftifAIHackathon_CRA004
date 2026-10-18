import React, { useState } from 'react';
import {
  getZones, createZone, updateZone, deleteZone, errorMessage,
} from '../services/api';
import { useApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { EmptyState } from '../components/EmptyState';
import { ConfirmDialog } from '../components/ConfirmDialog';
import type { Zone, ZoneCreate, Coordinate } from '../types';

const DEFAULT_ZONE: ZoneCreate = {
  name: '',
  description: '',
  coordinates: [
    { x: 0.1, y: 0.1 },
    { x: 0.5, y: 0.1 },
    { x: 0.5, y: 0.5 },
    { x: 0.1, y: 0.5 },
  ],
  color: '#ef4444',
  is_active: true,
};

function CoordEditor({
  coords,
  onChange,
}: {
  coords: Coordinate[];
  onChange: (c: Coordinate[]) => void;
}) {
  return (
    <div className="space-y-2">
      <label className="text-gray-300 text-sm font-medium block">
        Polygon Vertices (x,y normalised to 0–1)
      </label>
      {coords.map((c, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="text-gray-500 text-xs w-4">{i + 1}</span>
          <input
            type="number" min={0} max={1} step={0.01}
            value={c.x} onChange={(e) => {
              const next = [...coords];
              next[i] = { ...c, x: parseFloat(e.target.value) };
              onChange(next);
            }}
            className="w-24 bg-navy-700 border border-navy-500 rounded px-2 py-1 text-white text-sm"
            aria-label={`Vertex ${i + 1} x`}
          />
          <input
            type="number" min={0} max={1} step={0.01}
            value={c.y} onChange={(e) => {
              const next = [...coords];
              next[i] = { ...c, y: parseFloat(e.target.value) };
              onChange(next);
            }}
            className="w-24 bg-navy-700 border border-navy-500 rounded px-2 py-1 text-white text-sm"
            aria-label={`Vertex ${i + 1} y`}
          />
          {coords.length > 3 && (
            <button
              onClick={() => onChange(coords.filter((_, j) => j !== i))}
              className="text-red-400 hover:text-red-300 text-xs"
              aria-label={`Remove vertex ${i + 1}`}
            >✕</button>
          )}
        </div>
      ))}
      <button
        onClick={() => onChange([...coords, { x: 0.5, y: 0.5 }])}
        className="text-blue-400 hover:text-blue-300 text-xs mt-1"
      >+ Add vertex</button>
    </div>
  );
}

function ZoneForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: ZoneCreate;
  onSave: (z: ZoneCreate) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<ZoneCreate>(initial);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof ZoneCreate, val: unknown) =>
    setForm((f) => ({ ...f, [key]: val }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSave(form);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
      <div>
        <label className="text-gray-300 text-sm font-medium block mb-1" htmlFor="zone-name">Name</label>
        <input
          id="zone-name" required
          value={form.name} onChange={(e) => set('name', e.target.value)}
          className="w-full bg-navy-700 border border-navy-500 rounded-lg px-3 py-2 text-white text-sm"
          placeholder="e.g. Press Machine Area"
        />
      </div>
      <div>
        <label className="text-gray-300 text-sm font-medium block mb-1" htmlFor="zone-desc">Description</label>
        <input
          id="zone-desc"
          value={form.description ?? ''} onChange={(e) => set('description', e.target.value)}
          className="w-full bg-navy-700 border border-navy-500 rounded-lg px-3 py-2 text-white text-sm"
          placeholder="Optional description"
        />
      </div>
      <div>
        <label className="text-gray-300 text-sm font-medium block mb-1" htmlFor="zone-color">Color</label>
        <input
          id="zone-color" type="color"
          value={form.color ?? '#ef4444'} onChange={(e) => set('color', e.target.value)}
          className="h-9 w-16 bg-transparent border-0 cursor-pointer"
        />
      </div>
      <CoordEditor coords={form.coordinates} onChange={(c) => set('coordinates', c)} />
      <div className="flex items-center gap-2">
        <input
          id="zone-active" type="checkbox"
          checked={form.is_active ?? true} onChange={(e) => set('is_active', e.target.checked)}
          className="w-4 h-4 accent-blue-500"
        />
        <label htmlFor="zone-active" className="text-gray-300 text-sm">Active</label>
      </div>
      <div className="flex gap-3 pt-2">
        <button
          type="submit" disabled={saving}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-lg text-sm font-semibold transition-colors"
        >
          {saving ? 'Saving…' : 'Save Zone'}
        </button>
        <button
          type="button" onClick={onCancel}
          className="px-5 py-2 bg-navy-600 hover:bg-navy-500 text-gray-300 rounded-lg text-sm transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export function HazardZones() {
  const { data: zones, loading, error, refetch } = useApi(getZones);
  const [creating, setCreating] = useState(false);
  const [editingZone, setEditingZone] = useState<Zone | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Zone | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const handleCreate = async (data: ZoneCreate) => {
    await createZone(data);
    setCreating(false);
    refetch();
  };

  const handleUpdate = async (data: ZoneCreate) => {
    if (!editingZone) return;
    await updateZone(editingZone.id, data);
    setEditingZone(null);
    refetch();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteZone(deleteTarget.id);
      refetch();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleToggle = async (zone: Zone) => {
    try {
      await updateZone(zone.id, { is_active: !zone.is_active });
      refetch();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  if (loading) return <LoadingSpinner label="Loading zones..." />;
  if (error) return <ErrorAlert message={error} />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Hazard Zones</h1>
          <p className="text-gray-400 text-sm">Define restricted areas to monitor</p>
        </div>
        <button
          onClick={() => { setCreating(true); setEditingZone(null); }}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors"
        >
          + New Zone
        </button>
      </div>

      {actionError && <ErrorAlert message={actionError} onDismiss={() => setActionError(null)} />}

      {creating && (
        <div className="bg-navy-800 border border-blue-700 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Create New Zone</h2>
          <ZoneForm
            initial={DEFAULT_ZONE}
            onSave={handleCreate}
            onCancel={() => setCreating(false)}
          />
        </div>
      )}

      {editingZone && (
        <div className="bg-navy-800 border border-yellow-700 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Edit Zone: {editingZone.name}</h2>
          <ZoneForm
            initial={{
              name: editingZone.name,
              description: editingZone.description,
              coordinates: editingZone.coordinates,
              color: editingZone.color,
              is_active: editingZone.is_active,
            }}
            onSave={handleUpdate}
            onCancel={() => setEditingZone(null)}
          />
        </div>
      )}

      {!zones || zones.length === 0 ? (
        <EmptyState
          icon="📍"
          title="No hazard zones defined"
          description="Create a zone to start detecting unsafe entries."
          action={
            <button onClick={() => setCreating(true)} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm">
              Create First Zone
            </button>
          }
        />
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {zones.map((zone) => (
            <div
              key={zone.id}
              className="bg-navy-800 border border-navy-600 rounded-xl p-4 flex flex-col gap-3"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className="w-4 h-4 rounded-full flex-shrink-0"
                    style={{ backgroundColor: zone.color }}
                    aria-hidden
                  />
                  <span className="text-white font-semibold">{zone.name}</span>
                </div>
                <span className={`text-xs rounded-full px-2 py-0.5 ${zone.is_active ? 'bg-green-800 text-green-200' : 'bg-gray-700 text-gray-400'}`}>
                  {zone.is_active ? 'Active' : 'Disabled'}
                </span>
              </div>
              {zone.description && (
                <p className="text-gray-400 text-sm">{zone.description}</p>
              )}
              <p className="text-gray-500 text-xs">{zone.coordinates.length} vertices</p>
              <div className="flex gap-2 mt-auto pt-2 border-t border-navy-700">
                <button
                  onClick={() => { setEditingZone(zone); setCreating(false); }}
                  className="flex-1 py-1.5 rounded bg-navy-600 hover:bg-navy-500 text-gray-300 text-xs transition-colors"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleToggle(zone)}
                  className="flex-1 py-1.5 rounded bg-navy-600 hover:bg-navy-500 text-gray-300 text-xs transition-colors"
                >
                  {zone.is_active ? 'Disable' : 'Enable'}
                </button>
                <button
                  onClick={() => setDeleteTarget(zone)}
                  className="px-3 py-1.5 rounded bg-red-900/40 hover:bg-red-800 text-red-400 text-xs transition-colors"
                  aria-label={`Delete zone ${zone.name}`}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={!!deleteTarget}
        title="Delete Zone"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? This cannot be undone.`}
        confirmLabel="Delete"
        destructive
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
