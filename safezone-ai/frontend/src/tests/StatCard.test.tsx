import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatCard } from '../components/StatCard'

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Total Incidents" value={42} />)
    expect(screen.getByText('Total Incidents')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<StatCard label="Test" value={0} icon="🔴" />)
    expect(screen.getByText('🔴')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<StatCard label="Test" value={0} description="since last hour" />)
    expect(screen.getByText('since last hour')).toBeInTheDocument()
  })

  it('has accessible region label', () => {
    render(<StatCard label="Active Zones" value={3} />)
    expect(screen.getByRole('region', { name: 'Active Zones' })).toBeInTheDocument()
  })
})
