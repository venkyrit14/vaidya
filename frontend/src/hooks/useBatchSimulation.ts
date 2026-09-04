import { useCallback, useEffect, useRef, useState } from 'react'
import { DEMO_CASES, PIPELINE_STAGES } from '../lib/agentPipeline.ts'
import type { LiveFeedEvent, SimulatedAgentState } from '../types/liveFeed.ts'

type TimeoutHandle = ReturnType<typeof setTimeout>

function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

function delay(
  ms: number,
  timeouts: TimeoutHandle[],
  resolvers: Array<() => void>,
) {
  return new Promise<void>((resolve) => {
    const handle = setTimeout(() => {
      resolve()
    }, ms)
    timeouts.push(handle)
    resolvers.push(resolve)
  })
}

export function useBatchSimulation() {
  const [events, setEvents] = useState<LiveFeedEvent[]>([])
  const [running, setRunning] = useState(false)
  const timeoutsRef = useRef<TimeoutHandle[]>([])
  const resolversRef = useRef<Array<() => void>>([])
  const signalRef = useRef({ cancelled: false })
  const runIdRef = useRef(0)

  const clearTimers = useCallback(() => {
    for (const handle of timeoutsRef.current) {
      clearTimeout(handle)
    }
    timeoutsRef.current = []
    for (const resolve of resolversRef.current) {
      resolve()
    }
    resolversRef.current = []
  }, [])

  const reset = useCallback(() => {
    signalRef.current.cancelled = true
    runIdRef.current += 1
    clearTimers()
    setRunning(false)
    setEvents([])
  }, [clearTimers])

  useEffect(() => {
    return () => {
      signalRef.current.cancelled = true
      clearTimers()
    }
  }, [clearTimers])

  const runBatch = useCallback(async () => {
    signalRef.current.cancelled = true
    clearTimers()
    runIdRef.current += 1
    const runId = runIdRef.current
    const signal = { cancelled: false }
    signalRef.current = signal
    timeoutsRef.current = []
    resolversRef.current = []

    setEvents([])
    setRunning(true)

    const reduced = prefersReducedMotion()
    const staggerMs = reduced ? 180 : 800
    const stepMs = reduced ? 100 : 550

    const wait = (ms: number) =>
      delay(ms, timeoutsRef.current, resolversRef.current)

    const runCase = async (index: number) => {
      await wait(index * staggerMs)
      if (signal.cancelled || runId !== runIdRef.current) {
        return
      }

      const demo = DEMO_CASES[index]
      const eventId = `batch-${runId}-${index + 1}`

      const createEvent = (state: SimulatedAgentState): LiveFeedEvent => ({
        id: eventId,
        caseId: demo.caseId,
        eventType: demo.eventType,
        amount: demo.amount,
        rootCause: demo.rootCause,
        customerProfile: demo.customerProfile,
        evidence: demo.evidence,
        decision: demo.decision,
        policy: demo.policy,
        execution: demo.execution,
        finalOutcome: demo.finalOutcome,
        recoveredAmount: demo.recoveredAmount,
        outcomeMessage: demo.outcomeMessage,
        simulatedState: state,
        appearedAt: Date.now(),
      })

      // Stage 0: detected
      setEvents((current) => {
        if (current.some((e) => e.id === eventId)) {
          return current
        }
        return [...current, createEvent('detected')]
      })

      // Progress through remaining stages: diagnosing, evidence, decision, policy, action, outcome
      for (let sIdx = 1; sIdx < PIPELINE_STAGES.length; sIdx += 1) {
        await wait(stepMs)
        if (signal.cancelled || runId !== runIdRef.current) {
          return
        }

        const nextState = PIPELINE_STAGES[sIdx]
        setEvents((current) =>
          current.map((e) =>
            e.id === eventId ? { ...e, simulatedState: nextState } : e,
          ),
        )
      }
    }

    try {
      await Promise.all(DEMO_CASES.map((_, index) => runCase(index)))
    } finally {
      if (runId === runIdRef.current) {
        setRunning(false)
      }
    }
  }, [clearTimers])

  const activeCount = events.filter(
    (e) => e.simulatedState !== 'outcome',
  ).length

  return {
    events,
    running,
    activeCount,
    runBatch,
    reset,
  }
}
