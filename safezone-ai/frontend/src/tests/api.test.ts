import { describe, it, expect, vi } from 'vitest'

// Partially mock axios: keep AxiosError, replace create()
vi.mock('axios', async (importOriginal) => {
  const actual = await importOriginal<typeof import('axios')>()
  return {
    ...actual,
    default: {
      ...actual.default,
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn(),
        put: vi.fn(),
        patch: vi.fn(),
        delete: vi.fn(),
      })),
    },
  }
})

describe('API module', () => {
  it('exports getHealth', async () => {
    const api = await import('../services/api')
    expect(typeof api.getHealth).toBe('function')
  })

  it('exports getZones', async () => {
    const api = await import('../services/api')
    expect(typeof api.getZones).toBe('function')
  })

  it('exports createZone', async () => {
    const api = await import('../services/api')
    expect(typeof api.createZone).toBe('function')
  })

  it('exports getIncidents', async () => {
    const api = await import('../services/api')
    expect(typeof api.getIncidents).toBe('function')
  })

  it('exports getSummary', async () => {
    const api = await import('../services/api')
    expect(typeof api.getSummary).toBe('function')
  })

  it('getIncidentsCsvUrl contains incidents.csv', async () => {
    const api = await import('../services/api')
    const url = api.getIncidentsCsvUrl()
    expect(url).toContain('incidents.csv')
  })

  it('errorMessage returns string for plain Error', async () => {
    const api = await import('../services/api')
    const err = new Error('network fail')
    const result = api.errorMessage(err)
    expect(typeof result).toBe('string')
  })

  it('errorMessage returns string for string input', async () => {
    const api = await import('../services/api')
    const result = api.errorMessage('oops')
    expect(result).toBe('oops')
  })
})
