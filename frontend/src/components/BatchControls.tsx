import { formatInr } from '../lib/agentPipeline.ts'
import type { BatchSummary, RecoverySummaryResponse } from '../types/recovery.ts'

export type FilterStatus = 'all' | 'recovered' | 'human_review' | 'blocked'

type BatchControlsProps = {
  summary: RecoverySummaryResponse | null
  batches: BatchSummary[]
  selectedBatchId: string
  running: boolean
  activeCasesCount: number
  filter: FilterStatus
  onSelectBatch: (batchId: string) => void
  onRunBatch: () => void
  onRefresh: () => void
  onFilterChange: (filter: FilterStatus) => void
}

export function BatchControls({
  summary,
  batches,
  selectedBatchId,
  running,
  activeCasesCount,
  filter,
  onSelectBatch,
  onRunBatch,
  onRefresh,
  onFilterChange,
}: BatchControlsProps) {
  const selectedBatch = batches.find((b) => b.batch_id === selectedBatchId)

  return (
    <section
      aria-label="Operations and batch controls"
      className="flex shrink-0 flex-col gap-3 border-b border-hairline bg-panel px-6 py-3.5"
    >
      {/* Top row: Operations summary & Agent activity */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Operations summary from real backend */}
        <div className="flex flex-wrap items-center gap-4 text-[12px]">
          <span className="font-medium text-primary">
            <span className="font-data">{summary?.total_cases ?? 0}</span> cases tracked
          </span>
          <span className="text-tertiary">|</span>
          <span className="flex items-center gap-1.5 text-secondary">
            <span className="h-1.5 w-1.5 rounded-full bg-recovered" />
            <span className="font-data text-primary">
              {summary?.successful_recoveries ?? 0}
            </span>{' '}
            recovered
          </span>
          <span className="flex items-center gap-1.5 text-secondary">
            <span className="h-1.5 w-1.5 rounded-full bg-escalate" />
            <span className="font-data text-primary">
              {summary?.human_review_cases ?? 0}
            </span>{' '}
            human review
          </span>
          <span className="flex items-center gap-1.5 text-secondary">
            <span className="h-1.5 w-1.5 rounded-full bg-risk" />
            <span className="font-data text-primary">
              {summary?.blocked_cases ?? 0}
            </span>{' '}
            blocked
          </span>
        </div>

        {/* Real Agent Activity / Selected Batch Status */}
        <div className="flex items-center gap-3 rounded-[4px] border border-hairline bg-ink px-3 py-1.5 text-[12px]">
          <span className="text-[11px] font-medium tracking-wide text-tertiary uppercase">
            Execution Engine
          </span>
          <span className="text-tertiary">|</span>
          <span className="flex items-center gap-1 text-secondary">
            {running ? (
              <span className="live-indicator h-1.5 w-1.5 rounded-full bg-agent" />
            ) : (
              <span className="h-1.5 w-1.5 rounded-full bg-recovered" />
            )}
            <span className="font-data text-primary">
              {running ? `Processing (${activeCasesCount} cases)` : 'Ready'}
            </span>
          </span>
          {selectedBatch ? (
            <>
              <span className="text-tertiary">|</span>
              <span className="text-secondary">
                <span className="font-data text-primary">
                  {selectedBatch.processed_count}
                </span>{' '}
                / {selectedBatch.total_events} processed
              </span>
            </>
          ) : null}
        </div>
      </div>

      {/* Bottom row: Action triggers, Real Batch Selector & Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-1">
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={onRunBatch}
            disabled={running || !selectedBatchId}
            aria-busy={running}
            className={`flex cursor-pointer items-center gap-2 rounded-[4px] border px-3.5 py-1.5 text-[13px] font-medium transition-all ${
              running
                ? 'border-agent/50 bg-agent/10 text-agent'
                : 'border-agent bg-agent text-ink hover:bg-agent/90 disabled:opacity-50'
            }`}
          >
            {running ? (
              <>
                <span className="live-indicator h-2 w-2 rounded-full bg-agent" />
                <span>Running backend batch...</span>
              </>
            ) : (
              <>
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                <span>Process batch</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={onRefresh}
            disabled={running}
            title="Refresh backend records and summary"
            className="cursor-pointer rounded-[4px] border border-hairline bg-panel-raised px-2.5 py-1.5 text-[13px] text-secondary hover:text-primary disabled:opacity-50"
          >
            Refresh
          </button>

          {/* Real Backend Batch Dropdown */}
          <div className="flex items-center gap-1.5 text-[12px] text-secondary">
            <span>Batch:</span>
            <select
              value={selectedBatchId}
              onChange={(e) => onSelectBatch(e.target.value)}
              disabled={running}
              className="max-w-[320px] truncate cursor-pointer rounded-[4px] border border-hairline bg-ink px-2 py-1 text-[12px] text-primary focus:border-agent focus:outline-none"
            >
              {batches.map((batch) => (
                <option key={batch.batch_id} value={batch.batch_id}>
                  {batch.title} ({batch.total_events} events · {formatInr(batch.total_amount_at_risk)})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* View Filter Tabs */}
        <div className="flex items-center gap-1 rounded-[4px] border border-hairline bg-ink p-0.5 text-[12px]">
          {(
            [
              { id: 'all', label: 'All cases' },
              { id: 'recovered', label: 'Recovered' },
              { id: 'human_review', label: 'Human review' },
              { id: 'blocked', label: 'Blocked' },
            ] as const
          ).map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => onFilterChange(tab.id)}
              className={`cursor-pointer rounded-[3px] px-2.5 py-1 transition-colors ${
                filter === tab.id
                  ? 'bg-panel-raised font-medium text-primary'
                  : 'text-tertiary hover:text-secondary'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}
