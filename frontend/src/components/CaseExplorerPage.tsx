import { useEffect, useState } from 'react'
import { getBatchEvents } from '../api/recovery.ts'
import { CaseDetailsModal } from './CaseDetailsModal.tsx'
import { SourceEventModal } from './SourceEventModal.tsx'
import {
  useBatches,
  useRecoveryRecords,
} from '../hooks/useRecoveryData.ts'
import {
  formatCustomerProfile,
  formatEventType,
  formatInr,
  formatRootCause,
} from '../lib/agentPipeline.ts'
import type { BatchEvent } from '../types/recovery.ts'

export function CaseExplorerPage() {
  const [activeTab, setActiveTab] = useState<'records' | 'batches'>('records')

  // Search & Filter State for Records
  const [searchTerm, setSearchTerm] = useState('')
  const [eventType, setEventType] = useState('')
  const [outcome, setOutcome] = useState('')
  const [action, setAction] = useState('')
  const [requiresHuman, setRequiresHuman] = useState<boolean | undefined>(undefined)
  const limit = 15

  const {
    data: recordsData,
    loading: recordsLoading,
    setParams,
    refresh: refreshRecords,
  } = useRecoveryRecords({
    search: searchTerm || undefined,
    event_type: eventType || undefined,
    outcome: outcome || undefined,
    action: action || undefined,
    requires_human: requiresHuman,
    page: 1,
    limit,
  })

  // Selected case for detail modal
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null)
  const [selectedSourceEvent, setSelectedSourceEvent] = useState<BatchEvent | null>(null)

  // Batch exploration state
  const { batches, loading: batchesLoading } = useBatches()
  const [selectedBatchId, setSelectedBatchId] = useState<string>('BATCH_DEMO_01')
  const [batchEvents, setBatchEvents] = useState<BatchEvent[]>([])
  const [batchTotal, setBatchTotal] = useState(0)
  const [batchPage, setBatchPage] = useState(1)
  const [batchSearch, setBatchSearch] = useState('')
  const [batchLoading, setBatchLoading] = useState(false)

  // Sync params when filters change
  const handleApplyFilters = () => {
    setParams({
      search: searchTerm.trim() || undefined,
      event_type: eventType || undefined,
      outcome: outcome || undefined,
      action: action || undefined,
      requires_human: requiresHuman,
      page: 1,
      limit,
    })
  }

  const handleClearFilters = () => {
    setSearchTerm('')
    setEventType('')
    setOutcome('')
    setAction('')
    setRequiresHuman(undefined)
    setParams({
      search: undefined,
      event_type: undefined,
      outcome: undefined,
      action: undefined,
      requires_human: undefined,
      page: 1,
      limit,
    })
  }

  // Load batch events when batch explorer is active
  useEffect(() => {
    if (activeTab !== 'batches' || !selectedBatchId) return
    let active = true

    getBatchEvents(selectedBatchId, {
      search: batchSearch.trim() || undefined,
      page: batchPage,
      limit: 15,
    })
      .then((res) => {
        if (active) {
          setBatchEvents(res.items)
          setBatchTotal(res.total)
          setBatchLoading(false)
        }
      })
      .catch(() => {
        if (active) setBatchLoading(false)
      })

    return () => {
      active = false
    }
  }, [activeTab, selectedBatchId, batchPage, batchSearch])

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      {/* Header */}
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <h2 className="m-0 text-[18px] font-semibold text-primary">
            Case Explorer & Batch Ledger
          </h2>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Query and inspect autonomous recovery decisions across live records and raw dataset batches
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1 rounded-[4px] border border-hairline bg-panel p-0.5 text-[12px]">
          <button
            type="button"
            onClick={() => setActiveTab('records')}
            className={`cursor-pointer rounded-[3px] px-3 py-1 font-medium transition-colors ${
              activeTab === 'records'
                ? 'bg-agent text-ink'
                : 'text-secondary hover:text-primary'
            }`}
          >
            Processed Records ({recordsData?.total ?? 0})
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('batches')}
            className={`cursor-pointer rounded-[3px] px-3 py-1 font-medium transition-colors ${
              activeTab === 'batches'
                ? 'bg-agent text-ink'
                : 'text-secondary hover:text-primary'
            }`}
          >
            Source Batch Explorer ({batches.length} batches)
          </button>
        </div>
      </header>

      {/* Distinction Banner */}
      <div className="flex items-center justify-between border-b border-hairline bg-panel/60 px-6 py-2 text-[12px]">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-primary">Data Lineage Note:</span>
          <span className="text-secondary">
            <strong className="text-primary">Source Events</strong> represent raw uningested risk data. <strong className="text-primary">Processed Records</strong> represent immutable ledger decisions produced by Vaidya.
          </span>
        </div>
        <button
          type="button"
          onClick={() => refreshRecords()}
          className="cursor-pointer text-[11px] text-agent hover:underline"
        >
          Refresh Ledger
        </button>
      </div>

      {activeTab === 'records' ? (
        /* PROCESSED RECORDS TAB */
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
          {/* Filter Bar */}
          <div className="flex flex-wrap items-center gap-3 border-b border-hairline bg-panel px-6 py-3 text-[12px]">
            {/* Search Box */}
            <div className="flex items-center gap-2 flex-1 min-w-[240px]">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleApplyFilters()}
                placeholder="Search case ID, event type, action, message..."
                className="w-full rounded-[4px] border border-hairline bg-ink px-3 py-1.5 text-[12px] text-primary placeholder:text-tertiary focus:border-agent focus:outline-none"
              />
            </div>

            {/* Event Type */}
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="rounded-[4px] border border-hairline bg-ink px-2.5 py-1.5 text-[12px] text-primary focus:border-agent focus:outline-none"
            >
              <option value="">All Surfaces</option>
              <option value="payment_failure">Payment Failure</option>
              <option value="checkout_abandonment">Checkout Abandonment</option>
              <option value="overdue_invoice">Overdue Invoice</option>
            </select>

            {/* Outcome */}
            <select
              value={outcome}
              onChange={(e) => setOutcome(e.target.value)}
              className="rounded-[4px] border border-hairline bg-ink px-2.5 py-1.5 text-[12px] text-primary focus:border-agent focus:outline-none"
            >
              <option value="">All Outcomes</option>
              <option value="recovered">Recovered</option>
              <option value="blocked">Blocked</option>
              <option value="pending">Pending Review</option>
              <option value="failed">Failed</option>
            </select>

            {/* Action */}
            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="rounded-[4px] border border-hairline bg-ink px-2.5 py-1.5 text-[12px] text-primary focus:border-agent focus:outline-none"
            >
              <option value="">All Actions</option>
              <option value="retry">Retry</option>
              <option value="delayed_retry">Delayed Retry</option>
              <option value="targeted_reminder">Targeted Reminder</option>
              <option value="promise_to_pay">Promise to Pay</option>
              <option value="block_and_escalate">Block & Escalate</option>
              <option value="human_review">Human Review</option>
            </select>

            {/* Human Review Checkbox */}
            <label className="flex items-center gap-1.5 text-secondary cursor-pointer">
              <input
                type="checkbox"
                checked={requiresHuman === true}
                onChange={(e) => setRequiresHuman(e.target.checked ? true : undefined)}
                className="rounded border-hairline bg-ink text-agent"
              />
              <span>Human Review Only</span>
            </label>

            {/* Action Buttons */}
            <button
              type="button"
              onClick={handleApplyFilters}
              className="cursor-pointer rounded-[4px] border border-agent bg-agent px-3 py-1.5 font-medium text-ink hover:opacity-90"
            >
              Search
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              className="cursor-pointer rounded-[4px] border border-hairline bg-panel-raised px-2.5 py-1.5 text-secondary hover:text-primary"
            >
              Reset
            </button>
          </div>

          {/* Table Container */}
          <div className="min-h-0 flex-1 overflow-auto px-6 py-4">
            {recordsLoading ? (
              <div className="flex flex-col items-center justify-center py-20 text-secondary">
                <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
                <p className="mt-3 text-[13px]">Querying recovery ledger...</p>
              </div>
            ) : !recordsData?.items || recordsData.items.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-[6px] border border-dashed border-hairline p-12 text-center text-secondary">
                <p className="text-[14px] font-medium text-primary">No recovery records match the search filters</p>
                <p className="mt-1 text-[12px]">Try clearing filters or run a batch to process fresh records.</p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-[6px] border border-hairline bg-panel">
                <table className="w-full text-left text-[12px] border-collapse">
                  <thead>
                    <tr className="border-b border-hairline bg-ink text-[11px] uppercase tracking-wider text-tertiary">
                      <th className="px-4 py-3 font-semibold">Case ID</th>
                      <th className="px-4 py-3 font-semibold">Surface / Type</th>
                      <th className="px-4 py-3 font-semibold">Amount</th>
                      <th className="px-4 py-3 font-semibold">Action</th>
                      <th className="px-4 py-3 font-semibold">Outcome</th>
                      <th className="px-4 py-3 font-semibold">Recovered</th>
                      <th className="px-4 py-3 font-semibold">Message</th>
                      <th className="px-4 py-3 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-hairline">
                    {recordsData.items.map((rec) => (
                      <tr
                        key={rec.case_id}
                        onClick={() => setSelectedCaseId(rec.case_id)}
                        className="cursor-pointer hover:bg-panel-raised transition-colors"
                      >
                        <td className="px-4 py-3 font-data font-semibold text-agent">
                          {rec.case_id}
                        </td>
                        <td className="px-4 py-3 text-primary">
                          {formatEventType(rec.event_type)}
                        </td>
                        <td className="px-4 py-3 font-data font-medium text-primary">
                          {formatInr(rec.amount_at_risk)}
                        </td>
                        <td className="px-4 py-3 font-data text-secondary">
                          {rec.action}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`rounded px-2 py-0.5 text-[10px] font-medium ${
                              rec.outcome === 'recovered'
                                ? 'bg-recovered/15 text-recovered'
                                : rec.outcome === 'blocked'
                                  ? 'bg-risk/15 text-risk'
                                  : 'bg-escalate/15 text-escalate'
                            }`}
                          >
                            {rec.outcome.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-data text-recovered font-medium">
                          {formatInr(rec.recovered_amount)}
                        </td>
                        <td className="px-4 py-3 text-secondary max-w-xs truncate">
                          {formatRootCause(rec.message)}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedCaseId(rec.case_id)
                            }}
                            className="rounded border border-hairline bg-ink px-2 py-1 text-[11px] font-medium text-primary hover:border-agent hover:text-agent"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination Footer */}
          {recordsData && recordsData.total_pages > 1 ? (
            <footer className="flex shrink-0 items-center justify-between border-t border-hairline bg-panel px-6 py-3 text-[12px]">
              <span className="text-secondary">
                Showing page <strong className="text-primary">{recordsData.page}</strong> of{' '}
                <strong className="text-primary">{recordsData.total_pages}</strong> ({recordsData.total} total cases)
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={recordsData.page <= 1}
                  onClick={() => setParams({ page: recordsData.page - 1 })}
                  className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  type="button"
                  disabled={recordsData.page >= recordsData.total_pages}
                  onClick={() => setParams({ page: recordsData.page + 1 })}
                  className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </footer>
          ) : null}
        </div>
      ) : (
        /* SOURCE BATCH EXPLORER TAB (Phase 2E) */
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
          {/* Batch Selector and Details */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-hairline bg-panel px-6 py-3.5 text-[12px]">
            <div className="flex items-center gap-3">
              <span className="font-semibold text-secondary">Select Batch:</span>
              <select
                value={selectedBatchId}
                onChange={(e) => {
                  setSelectedBatchId(e.target.value)
                  setBatchPage(1)
                }}
                disabled={batchesLoading}
                className="max-w-md rounded-[4px] border border-hairline bg-ink px-3 py-1.5 text-[12px] text-primary focus:border-agent focus:outline-none"
              >
                {batches.map((b) => (
                  <option key={b.batch_id} value={b.batch_id}>
                    {b.title} · {b.surface} ({b.total_events} events · {formatInr(b.total_amount_at_risk)})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                value={batchSearch}
                onChange={(e) => setBatchSearch(e.target.value)}
                placeholder="Search events in batch..."
                className="rounded-[4px] border border-hairline bg-ink px-3 py-1 text-[12px] text-primary placeholder:text-tertiary focus:border-agent focus:outline-none"
              />
            </div>
          </div>

          {/* Batch Events Table */}
          <div className="min-h-0 flex-1 overflow-auto px-6 py-4">
            {batchLoading ? (
              <div className="flex flex-col items-center justify-center py-20 text-secondary">
                <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
                <p className="mt-3 text-[13px]">Streaming batch source events...</p>
              </div>
            ) : batchEvents.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-[6px] border border-dashed border-hairline p-12 text-center text-secondary">
                <p className="text-[14px] font-medium text-primary">No source events found in batch</p>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-[6px] border border-hairline bg-panel">
                <table className="w-full text-left text-[12px] border-collapse">
                  <thead>
                    <tr className="border-b border-hairline bg-ink text-[11px] uppercase tracking-wider text-tertiary">
                      <th className="px-4 py-3 font-semibold">Event ID</th>
                      <th className="px-4 py-3 font-semibold">Surface</th>
                      <th className="px-4 py-3 font-semibold">Amount At Risk</th>
                      <th className="px-4 py-3 font-semibold">Root Cause</th>
                      <th className="px-4 py-3 font-semibold">Customer ID</th>
                      <th className="px-4 py-3 font-semibold">Customer Profile</th>
                      <th className="px-4 py-3 font-semibold">Source Timestamp</th>
                      <th className="px-4 py-3 text-right font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-hairline">
                    {batchEvents.map((ev, idx) => (
                      <tr key={`${ev.event_id}-${idx}`} className="hover:bg-panel-raised transition-colors">
                        <td className="px-4 py-3 font-data font-semibold text-primary">
                          {ev.event_id}
                        </td>
                        <td className="px-4 py-3 text-secondary">
                          {formatEventType(ev.event_type)}
                        </td>
                        <td className="px-4 py-3 font-data font-medium text-primary">
                          {formatInr(ev.amount)}
                        </td>
                        <td className="px-4 py-3 text-secondary">
                          {formatRootCause(ev.root_cause)}
                        </td>
                        <td className="px-4 py-3 font-data text-tertiary">
                          {ev.customer_id}
                        </td>
                        <td className="px-4 py-3 text-secondary">
                          {formatCustomerProfile(ev.customer_profile)}
                        </td>
                        <td className="px-4 py-3 font-data text-tertiary">
                          {ev.timestamp}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedSourceEvent(ev)
                            }}
                            className="rounded border border-hairline bg-ink px-2 py-1 text-[11px] font-medium text-primary hover:border-agent hover:text-agent cursor-pointer transition-colors"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Batch Pagination Footer */}
          {batchTotal > 15 ? (
            <footer className="flex shrink-0 items-center justify-between border-t border-hairline bg-panel px-6 py-3 text-[12px]">
              <span className="text-secondary">
                Showing page <strong className="text-primary">{batchPage}</strong> ({batchTotal} raw source events in this batch)
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={batchPage <= 1}
                  onClick={() => setBatchPage((p) => Math.max(1, p - 1))}
                  className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
                >
                  Previous
                </button>
                <button
                  type="button"
                  disabled={batchPage * 15 >= batchTotal}
                  onClick={() => setBatchPage((p) => p + 1)}
                  className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
                >
                  Next
                </button>
              </div>
            </footer>
          ) : null}
        </div>
      )}

      {/* Case Details Modal */}
      <CaseDetailsModal
        caseId={selectedCaseId}
        onClose={() => setSelectedCaseId(null)}
      />

      {/* Source Event Details Modal */}
      <SourceEventModal
        event={selectedSourceEvent}
        batchId={selectedBatchId}
        onClose={() => setSelectedSourceEvent(null)}
      />
    </div>
  )
}
