import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { EmptyState } from '../components/EmptyState'

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No zones found" />)
    expect(screen.getByText('No zones found')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<EmptyState title="No zones" description="Create one to start" />)
    expect(screen.getByText('Create one to start')).toBeInTheDocument()
  })

  it('renders action when provided', () => {
    render(<EmptyState title="Empty" action={<button>Create</button>} />)
    expect(screen.getByText('Create')).toBeInTheDocument()
  })

  it('renders default icon', () => {
    render(<EmptyState title="Empty" />)
    expect(screen.getByText('📭')).toBeInTheDocument()
  })
})
