import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { StatusBadge } from '../components/StatusBadge'

describe('StatusBadge', () => {
  it('renders status text', () => {
    render(<StatusBadge status="active" />)
    expect(screen.getByText('active')).toBeInTheDocument()
  })

  it('renders resolved status', () => {
    render(<StatusBadge status="resolved" />)
    expect(screen.getByText('resolved')).toBeInTheDocument()
  })

  it('renders running status', () => {
    render(<StatusBadge status="running" />)
    expect(screen.getByText('running')).toBeInTheDocument()
  })

  it('uses uppercase styling', () => {
    render(<StatusBadge status="acknowledged" />)
    const badge = screen.getByText('acknowledged')
    expect(badge.className).toContain('uppercase')
  })

  it('accepts size md', () => {
    render(<StatusBadge status="active" size="md" />)
    const badge = screen.getByText('active')
    expect(badge.className).toContain('text-sm')
  })
})
