import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ErrorAlert } from '../components/ErrorAlert'

describe('ErrorAlert', () => {
  it('renders the error message', () => {
    render(<ErrorAlert message="Something went wrong" />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('has alert role', () => {
    render(<ErrorAlert message="Error!" />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('calls onDismiss when dismiss button clicked', () => {
    const onDismiss = vi.fn()
    render(<ErrorAlert message="Error" onDismiss={onDismiss} />)
    fireEvent.click(screen.getByLabelText('Dismiss error'))
    expect(onDismiss).toHaveBeenCalledOnce()
  })

  it('does not show dismiss button when no handler', () => {
    render(<ErrorAlert message="Error" />)
    expect(screen.queryByLabelText('Dismiss error')).not.toBeInTheDocument()
  })
})
