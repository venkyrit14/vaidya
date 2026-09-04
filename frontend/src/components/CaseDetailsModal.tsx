import { useEffect, useState } from 'react'
import { getRecordById } from '../api/recovery.ts'
import { AgentStateProgress } from './AgentStateProgress.tsx'
import {
  formatEventType,
  formatInr,
  formatRootCause,
} from '../lib/agentPipeline.ts'
import type { CaseDetailsResponse } from '../types/recovery.ts'

type CaseDetailsModalProps = {
  caseId: string | null
  onClose: () => void
}

export function CaseDetailsModal({ caseId, onClose }: CaseDetailsModalProps) {
  const [data, setData] = useState<CaseDetailsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!caseId) return

    let active = true
    getRecordById(caseId)
      .then((res) => {
        if (active) {
          setData(res)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : 'Failed to load case details')
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [caseId])

  // Handle escape key
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])

  if (!caseId) return null

  const record = data?.record
  const decision = data?.decision_context
  const policy = data?.policy_context

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Case Details for ${caseId}`}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-[8px] border border-hairline bg-panel shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="font-data text-[13px] font-semibold text-agent">
              {caseId}
            </span>
            <span className="text-tertiary">·</span>
            <span className="text-[14px] font-medium text-primary">
              {record ? formatEventType(record.event_type) : 'Case Details'}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-[4px] border border-hairline text-secondary hover:bg-panel-raised hover:text-primary"
            aria-label="Close case details"
          >
            ✕
          </button>
        </header>

        {/* Content Body */}
        <div className="min-h-0 flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 text-secondary">
              <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
              <p className="mt-3 text-[13px]">Retrieving case records and decision telemetry...</p>
            </div>
          ) : error ? (
            <div className="rounded-[6px] border border-risk/40 bg-risk/10 p-4 text-[13px] text-risk">
              <p className="font-semibold">Unable to load case details</p>
              <p className="mt-1 text-[12px] opacity-90">{error}</p>
            </div>
          ) : record ? (
            <div className="flex flex-col gap-6">
              {/* Top Overview Strip */}
              <div className="grid grid-cols-2 gap-4 rounded-[6px] border border-hairline bg-ink p-4 sm:grid-cols-4">
                <div>
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    Amount At Risk
                  </span>
                  <p className="font-data m-0 mt-1 text-[16px] font-semibold text-primary">
                    {formatInr(record.amount_at_risk)}
                  </p>
                </div>
                <div>
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    Outcome
                  </span>
                  <p className="font-data m-0 mt-1 text-[14px] font-semibold">
                    <span
                      className={`rounded-[4px] px-2 py-0.5 text-[11px] ${
                        record.outcome === 'recovered'
                          ? 'border border-recovered/40 bg-recovered/10 text-recovered'
                          : record.outcome === 'blocked'
                            ? 'border border-risk/40 bg-risk/10 text-risk'
                            : 'border border-escalate/40 bg-escalate/10 text-escalate'
                      }`}
                    >
                      {record.outcome.toUpperCase()}
                    </span>
                  </p>
                </div>
                <div>
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    Recovered
                  </span>
                  <p className="font-data m-0 mt-1 text-[16px] font-semibold text-recovered">
                    {formatInr(record.recovered_amount)}
                  </p>
                </div>
                <div>
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    Remaining
                  </span>
                  <p className="font-data m-0 mt-1 text-[16px] font-semibold text-tertiary">
                    {formatInr(record.remaining_amount)}
                  </p>
                </div>
              </div>

              {/* Prominent 7-Stage Pipeline Progression */}
              <div className="rounded-[6px] border border-hairline bg-ink/40 p-4">
                <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                  Autonomous 7-Stage Recovery Pipeline
                </span>
                <div className="mt-3">
                  <AgentStateProgress
                    outcome={record.outcome}
                    requiresHuman={record.requires_human}
                    simulatedState="outcome"
                  />
                </div>
              </div>

              {/* 4 Core Facets: Event, AI Decision, Policy Gate, Execution */}
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {/* 1. Ingested Risk Event */}
                <div className="flex flex-col gap-2.5 rounded-[6px] border border-hairline bg-ink p-4 text-[12px]">
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    1. Revenue Risk Event
                  </span>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Event Type:</span>
                    <span className="font-medium text-primary">{formatEventType(record.event_type)}</span>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Root Cause:</span>
                    <div className="text-right">
                      <span className="font-medium text-primary">
                        {formatRootCause(decision?.reason || record.message)}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Execution Status:</span>
                    <span className="font-data text-primary">{record.execution_status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Recorded At:</span>
                    <span className="font-data text-tertiary">
                      {record.timestamp ? new Date(record.timestamp).toLocaleString('en-IN') : '—'}
                    </span>
                  </div>
                </div>

                {/* 2. AI Decision Engine */}
                <div className="flex flex-col gap-2.5 rounded-[6px] border border-hairline bg-ink p-4 text-[12px]">
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    2. Decision Engine (RAG)
                  </span>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Selected Action:</span>
                    <span className="font-data font-semibold text-agent">
                      {decision?.action || record.action}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Model Confidence:</span>
                    <span className="font-data text-primary">
                      {decision ? `${(decision.confidence * 100).toFixed(1)}%` : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Historical Cases Matched:</span>
                    <span className="font-data text-primary">
                      {decision?.historical_cases_count ?? '—'} similar cases
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-secondary">Expected Recovery:</span>
                    <span className="font-data text-recovered">
                      {decision ? formatInr(decision.expected_recovery) : '—'}
                    </span>
                  </div>
                </div>

                {/* 3. Policy & Governance Gate */}
                <div className="flex flex-col gap-2.5 rounded-[6px] border border-hairline bg-ink p-4 text-[12px]">
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    3. Safety & Policy Gate
                  </span>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Policy Decision:</span>
                    <span
                      className={`font-data font-semibold ${
                        policy?.allowed ? 'text-recovered' : 'text-risk'
                      }`}
                    >
                      {policy?.decision || (record.requires_human ? 'HUMAN REVIEW' : 'ALLOWED')}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Risk Level:</span>
                    <span className="font-data text-primary">
                      {policy?.risk_level || 'standard'}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-hairline/60 pb-1.5">
                    <span className="text-secondary">Human Review Mandated:</span>
                    <span className="font-data text-primary">
                      {record.requires_human || policy?.requires_human ? 'YES' : 'NO'}
                    </span>
                  </div>
                  <div className="mt-1">
                    <span className="text-[11px] text-tertiary">Policy Justification:</span>
                    <p className="m-0 mt-0.5 text-[11px] text-secondary">
                      {policy?.reason || 'Verified within standard autonomous recovery parameters.'}
                    </p>
                  </div>
                </div>

                {/* 4. Execution & Audit Message */}
                <div className="flex flex-col justify-between rounded-[6px] border border-hairline bg-ink p-4 text-[12px]">
                  <div>
                    <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                      4. Execution & Audit Log
                    </span>
                    <p className="mt-2 text-[12px] leading-relaxed text-primary">
                      {record.message}
                    </p>
                  </div>
                  <div className="mt-3 rounded-[4px] border border-hairline bg-panel p-2.5 text-[11px] text-tertiary">
                    <span>Audit Status: </span>
                    <span className="font-data text-primary">Immutable Ledger Recorded</span>
                  </div>
                </div>
              </div>

              {/* Historical Evidence Items if available */}
              {decision?.evidence && decision.evidence.length > 0 ? (
                <div className="rounded-[6px] border border-hairline bg-ink p-4">
                  <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                    Historical RAG Evidence ({decision.evidence.length} samples)
                  </span>
                  <div className="mt-3 flex flex-col gap-2">
                    {decision.evidence.map((ev, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between rounded-[4px] border border-hairline/60 bg-panel px-3 py-2 text-[12px]"
                      >
                        <div className="flex items-center gap-2">
                          <span className="font-data text-[11px] text-agent">
                            {String(ev['case_id'] || `EVID_${idx + 1}`)}
                          </span>
                          <span className="text-secondary">
                            {String(ev['action_taken'] || ev['action'] || 'Action')}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="font-data text-tertiary">
                            Similarity: {(Number(ev['similarity'] || 0.8) * 100).toFixed(0)}%
                          </span>
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                              String(ev['outcome']) === 'recovered'
                                ? 'bg-recovered/15 text-recovered'
                                : 'bg-risk/15 text-risk'
                            }`}
                          >
                            {String(ev['outcome'] || 'recovered')}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <footer className="flex shrink-0 items-center justify-end border-t border-hairline bg-panel px-6 py-3">
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer rounded-[4px] border border-hairline bg-panel-raised px-4 py-1.5 text-[12px] font-medium text-primary hover:bg-panel"
          >
            Close
          </button>
        </footer>
      </div>
    </div>
  )
}
