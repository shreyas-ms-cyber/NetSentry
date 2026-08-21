import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatCard from '../components/dashboard/StatCard'

// Mock the FontAwesomeIcon
vi.mock('@fortawesome/react-fontawesome', () => ({
  FontAwesomeIcon: () => <span data-testid="mock-icon">icon</span>
}))

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="Test Title" value="42" />)
    expect(screen.getByText('Test Title')).toBeDefined()
    expect(screen.getByText('42')).toBeDefined()
  })

  it('renders with custom color', () => {
    render(<StatCard title="Test" value="100" color="#FF0000" />)
    const valueElement = screen.getByText('100')
    expect(valueElement).toBeDefined()
  })

  it('renders with subtitle', () => {
    render(<StatCard title="Test" value="100" subtitle="MB/s" />)
    expect(screen.getByText('MB/s')).toBeDefined()
  })
})
