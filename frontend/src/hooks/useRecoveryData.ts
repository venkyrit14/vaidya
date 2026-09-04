import { useCallback, useEffect, useState } from 'react'
import {
  getBatches,
  getPolicies,
  getRecoveryRecords,
  getRecoverySummary,
  getSystemStatus,
} from '../api/recovery.ts'
import type { RecordQueryParams } from '../api/recovery.ts'
import type {
  BatchSummary,
  PaginatedRecordsResponse,
  PolicyConfig,
  RecoverySummaryResponse,
  SystemStatus,
} from '../types/recovery.ts'

export function useRecoverySummary(pollIntervalMs?: number) {
  const [summary, setSummary] = useState<RecoverySummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchSummary = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getRecoverySummary()
      setSummary(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load summary'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    getRecoverySummary()
      .then((data) => {
        if (active) {
          setSummary(data)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err : new Error('Failed to load summary'))
          setLoading(false)
        }
      })

    if (!pollIntervalMs) return () => { active = false }
    const timer = setInterval(() => {
      void fetchSummary()
    }, pollIntervalMs)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [fetchSummary, pollIntervalMs])

  return { summary, loading, error, refresh: fetchSummary }
}

export function useBatches() {
  const [batches, setBatches] = useState<BatchSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchBatches = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getBatches()
      setBatches(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load batches'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    getBatches()
      .then((data) => {
        if (active) {
          setBatches(data)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err : new Error('Failed to load batches'))
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [])

  return { batches, loading, error, refresh: fetchBatches }
}

export function useRecoveryRecords(initialParams?: RecordQueryParams) {
  const [params, setParams] = useState<RecordQueryParams>(initialParams || { page: 1, limit: 20 })
  const [data, setData] = useState<PaginatedRecordsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchRecords = useCallback(async (customParams?: RecordQueryParams) => {
    const q = customParams ?? params
    setLoading(true)
    try {
      const resp = await getRecoveryRecords(q)
      setData(resp)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load records'))
    } finally {
      setLoading(false)
    }
  }, [params])

  useEffect(() => {
    let active = true
    getRecoveryRecords(params)
      .then((resp) => {
        if (active) {
          setData(resp)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err : new Error('Failed to load records'))
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [params])

  const updateParams = useCallback((newParams: Partial<RecordQueryParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }))
  }, [])

  return {
    data,
    loading,
    error,
    params,
    setParams: updateParams,
    refresh: fetchRecords,
  }
}

export function useSystemStatus(pollIntervalMs?: number) {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchStatus = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getSystemStatus()
      setStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load system status'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    getSystemStatus()
      .then((data) => {
        if (active) {
          setStatus(data)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err : new Error('Failed to load system status'))
          setLoading(false)
        }
      })

    if (!pollIntervalMs) return () => { active = false }
    const timer = setInterval(() => {
      void fetchStatus()
    }, pollIntervalMs)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [fetchStatus, pollIntervalMs])

  return { status, loading, error, refresh: fetchStatus }
}

export function usePolicies() {
  const [policies, setPolicies] = useState<PolicyConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchPolicies = useCallback(async () => {
    setLoading(true)
    try {
      const data = await getPolicies()
      setPolicies(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load policies'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let active = true
    getPolicies()
      .then((data) => {
        if (active) {
          setPolicies(data)
          setError(null)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err : new Error('Failed to load policies'))
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [])

  return { policies, loading, error, refresh: fetchPolicies }
}
