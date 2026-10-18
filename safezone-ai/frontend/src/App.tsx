import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { NavBar } from './components/NavBar';
import { Dashboard } from './pages/Dashboard';
import { LiveMonitor } from './pages/LiveMonitor';
import { HazardZones } from './pages/HazardZones';
import { Incidents } from './pages/Incidents';
import { Settings } from './pages/Settings';

export function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-navy-900 text-white">
        <NavBar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/monitoring" element={<LiveMonitor />} />
            <Route path="/zones" element={<HazardZones />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
