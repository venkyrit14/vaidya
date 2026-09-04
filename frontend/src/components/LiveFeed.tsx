import { LiveFeedEventCard } from './LiveFeedEvent.tsx'
import type { LiveFeedEvent } from '../types/liveFeed.ts'
import type { RecoveryRecord } from '../types/recovery.ts'

type LiveFeedProps = {
  events?: LiveFeedEvent[]
  records?: RecoveryRecord[]
  running: boolean
  onRunBatch?: () => void
  onSelectCase?: (caseId: string) => void
}

export function LiveFeed({
  events = [],
  records = [],
  running,
  onRunBatch,
  onSelectCase,
}: LiveFeedProps) {
  const hasRecords = records.length > 0
  const totalCases = hasRecords ? records.length : events.length

  return (
    <section
      aria-label="Live Recovery Feed"
      aria-busy={running}
      aria-live="polite"
      className="flex min-h-0 flex-1 flex-col overflow-hidden bg-ink px-6 py-4"
    >
      <header className="mb-3 flex shrink-0 items-center justify-between">
        <div className="flex items-center gap-2.5">
          <h3 className="m-0 text-[14px] font-semibold text-primary">
            Live Recovery Feed
          </h3>
          <span className="font-data rounded-[999px] bg-panel px-2 py-0.5 text-[11px] font-medium text-secondary">
            {totalCases} {totalCases === 1 ? 'case' : 'cases'}
          </span>
          {hasRecords ? (
            <span className="rounded bg-recovered/10 px-2 py-0.5 text-[10px] font-medium text-recovered">
              Backend ledger connected
            </span>
          ) : null}
        </div>

        {running ? (
          <div className="flex items-center gap-2 text-[12px] text-agent">
            <span className="live-indicator h-2 w-2 rounded-full bg-agent" />
            <span>Autonomous agent active</span>
          </div>
        ) : null}
      </header>

      {totalCases === 0 ? (
        <div className="flex min-h-0 flex-1 flex-col items-center justify-center rounded-[6px] border border-dashed border-hairline bg-panel/30 p-8 text-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-panel text-tertiary">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          <p className="mt-3 mb-1 text-[14px] font-medium text-primary">
            No active cases matching filter
          </p>
          <p className="m-0 max-w-sm text-[13px] text-secondary">
            Run a recovery batch to process real revenue-risk events through the 7-stage autonomous pipeline.
          </p>
          {onRunBatch ? (
            <button
              type="button"
              onClick={onRunBatch}
              className="mt-4 cursor-pointer rounded-[4px] border border-agent bg-agent px-4 py-2 text-[13px] font-medium text-ink transition-opacity hover:opacity-90"
            >
              Process recovery batch
            </button>
          ) : null}
        </div>
      ) : (
        <div className="flex min-h-0 flex-1 flex-col gap-3.5 overflow-y-auto pr-1">
          {hasRecords
            ? records.map((rec) => (
                <LiveFeedEventCard
                  key={rec.case_id}
                  record={rec}
                  onSelectCase={onSelectCase}
                />
              ))
            : events.map((event) => (
                <LiveFeedEventCard
                  key={event.id}
                  event={event}
                  onSelectCase={onSelectCase}
                />
              ))}
        </div>
      )}
    </section>
  )
}
