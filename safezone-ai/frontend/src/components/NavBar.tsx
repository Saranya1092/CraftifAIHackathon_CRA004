import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard', exact: true },
  { to: '/monitoring', label: 'Live Monitor' },
  { to: '/zones', label: 'Hazard Zones' },
  { to: '/incidents', label: 'Incidents' },
  { to: '/settings', label: 'Settings' },
];

export function NavBar() {
  return (
    <nav
      className="bg-navy-800 border-b border-navy-600 px-6 py-3 flex items-center gap-8"
      aria-label="Main navigation"
    >
      <div className="flex items-center gap-2 mr-6">
        <span className="text-red-500 text-2xl" aria-hidden>🛡</span>
        <span className="text-white font-bold text-lg tracking-tight">SafeZone AI</span>
        <span className="text-gray-500 text-xs ml-1 hidden sm:block">Workplace Safety Sentinel</span>
      </div>
      <div className="flex items-center gap-1 flex-wrap">
        {links.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-700 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-navy-600'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
