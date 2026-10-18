import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ConfirmDialog } from '../components/ConfirmDialog'

describe('ConfirmDialog', () => {
  it('does not render when closed', () => {
    render(
      <ConfirmDialog
        isOpen={false}
        title="Delete?" message="Sure?"
        onConfirm={vi.fn()} onCancel={vi.fn()}
      />
    )
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders when open', () => {
    render(
      <ConfirmDialog
        isOpen
        title="Delete Zone" message="This cannot be undone."
        onConfirm={vi.fn()} onCancel={vi.fn()}
      />
    )
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText('Delete Zone')).toBeInTheDocument()
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument()
  })

  it('calls onConfirm', () => {
    const onConfirm = vi.fn()
    render(
      <ConfirmDialog
        isOpen title="T" message="M"
        onConfirm={onConfirm} onCancel={vi.fn()}
      />
    )
    fireEvent.click(screen.getByText('Confirm'))
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('calls onCancel', () => {
    const onCancel = vi.fn()
    render(
      <ConfirmDialog
        isOpen title="T" message="M"
        onConfirm={vi.fn()} onCancel={onCancel}
      />
    )
    fireEvent.click(screen.getByText('Cancel'))
    expect(onCancel).toHaveBeenCalledOnce()
  })

  it('uses custom labels', () => {
    render(
      <ConfirmDialog
        isOpen title="T" message="M"
        confirmLabel="Yes, delete" cancelLabel="Nope"
        onConfirm={vi.fn()} onCancel={vi.fn()}
      />
    )
    expect(screen.getByText('Yes, delete')).toBeInTheDocument()
    expect(screen.getByText('Nope')).toBeInTheDocument()
  })
})
