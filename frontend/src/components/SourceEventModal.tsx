import { useEffect } from 'react'
import {
  formatCustomerProfile,
  formatEventType,
  formatInr,
  formatRootCause,
} from '../lib/agentPipeline.ts'
import type { BatchEvent } from '../types/recovery.ts'

type SourceEventModalProps = {
  event: BatchEvent | null
  batchId?: string | null
  onClose: () => void
}

export function SourceEventModal({ event, batchId, onClose }: SourceEventModalProps) {
  // Handle escape key
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [onClose])

  if (!event) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Source Event Details for ${event.event_id}`}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-[8px] border border-hairline bg-panel shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="rounded-[3px] bg-agent/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-agent">
              RAW SOURCE EVENT
            </span>
            <span className="font-data text-[13px] font-semibold text-primary">
              {event.event_id}
            </span>
            <span className="text-tertiary">·</span>
            <span className="text-[13px] font-medium text-secondary">
              {formatEventType(event.event_type)}
            </span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-[4px] border border-hairline text-secondary hover:bg-panel-raised hover:text-primary"
            aria-label="Close source event details"
          >
            ✕
          </button>
        </header>

        {/* Content Body */}
        <div className="min-h-0 flex-1 overflow-y-auto p-6 space-y-6">
          {/* Explanation Banner */}
          <div className="rounded-[6px] border border-agent/30 bg-agent/5 p-3.5 text-[12px] text-secondary">
            <div className="flex items-start gap-2.5">
              <span className="mt-1 inline-block h-2 w-2 shrink-0 rounded-full bg-agent" />
              <div>
                <span className="font-semibold text-primary">Raw Ingestion Ledger Entry: </span>
                This is a raw source event ingested from the selected batch. Recovery decisions,
                policy evaluations, execution, and outcomes are generated only when the event is
                processed through Vaidya&apos;s autonomous recovery pipeline.
              </div>
            </div>
          </div>

          {/* Primary Field Cards */}
          <div className="grid grid-cols-2 gap-4 rounded-[6px] border border-hairline bg-ink p-4 sm:grid-cols-4">
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Event ID
              </span>
              <p className="font-data m-0 mt-1 text-[13px] font-semibold text-primary truncate">
                {event.event_id}
              </p>
            </div>
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Batch ID
              </span>
              <p className="font-data m-0 mt-1 text-[13px] font-semibold text-secondary truncate">
                {batchId || 'N/A'}
              </p>
            </div>
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Surface
              </span>
              <p className="m-0 mt-1 text-[13px] font-medium text-primary truncate">
                {formatEventType(event.event_type)}
              </p>
            </div>
            <div>
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Amount At Risk
              </span>
              <p className="font-data m-0 mt-1 text-[14px] font-semibold text-primary">
                {formatInr(event.amount)}
              </p>
            </div>
          </div>

          {/* Detail Attributes */}
          <div className="grid grid-cols-1 gap-3 rounded-[6px] border border-hairline bg-panel-raised/50 p-4 sm:grid-cols-2 text-[12px]">
            <div className="flex flex-col gap-1 border-b border-hairline/60 pb-3 sm:border-b-0 sm:pb-0">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Root Cause
              </span>
              <span className="font-medium text-primary">
                {formatRootCause(event.root_cause)}
              </span>
              <span className="font-data text-[11px] text-tertiary">
                Code: {event.root_cause}
              </span>
            </div>

            <div className="flex flex-col gap-1 border-b border-hairline/60 pb-3 sm:border-b-0 sm:pb-0">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Customer Profile
              </span>
              <span className="font-medium text-primary">
                {formatCustomerProfile(event.customer_profile)}
              </span>
              <span className="font-data text-[11px] text-tertiary">
                Tag: {event.customer_profile}
              </span>
            </div>

            <div className="flex flex-col gap-1 pt-1">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Customer Identifier
              </span>
              <span className="font-data text-primary">
                {event.customer_id}
              </span>
            </div>

            <div className="flex flex-col gap-1 pt-1">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Source Timestamp
              </span>
              <span className="font-data text-secondary">
                {event.timestamp}
              </span>
            </div>
          </div>

          {/* Raw Backend Payload */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Raw Backend Payload (Source Event)
              </span>
              <span className="font-data text-[11px] text-tertiary">
                Exact API Response Object
              </span>
            </div>
            <pre className="m-0 overflow-x-auto rounded-[6px] border border-hairline bg-ink p-4 font-mono text-[12px] leading-relaxed text-secondary">
              <code>{JSON.stringify(event, null, 2)}</code>
            </pre>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex shrink-0 items-center justify-end border-t border-hairline bg-panel px-6 py-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded border border-hairline bg-ink px-4 py-1.5 text-[12px] font-medium text-primary hover:border-agent hover:text-agent cursor-pointer transition-colors"
          >
            Close
          </button>
        </footer>
      </div>
    </div>
  )
}
