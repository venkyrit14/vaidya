import { useRecoverySummary } from '../hooks/useRecoveryData.ts'
import { formatEventType, formatInr } from '../lib/agentPipeline.ts'

export function AnalyticsPage() {
  const { summary, loading, refresh } = useRecoverySummary()

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-ink text-secondary">
        <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
        <span className="ml-3 text-[13px]">Aggregating financial recovery telemetry...</span>
      </div>
    )
  }

  const atRisk = summary?.total_amount_at_risk ?? 0
  const recovered = summary?.total_recovered ?? 0
  const remaining = summary?.total_remaining ?? 0
  const rate = summary?.recovery_rate ?? 0

  const outcomes = summary?.outcomes || {}
  const actions = summary?.actions || {}
  const eventTypes = summary?.event_types || {}

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <h2 className="m-0 text-[18px] font-semibold text-primary">
            Revenue Recovery Analytics & Intelligence
          </h2>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Aggregate recovery performance, policy efficacy, and surface distribution across the merchant portfolio
          </p>
        </div>

        <button
          type="button"
          onClick={() => refresh()}
          className="cursor-pointer rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] text-primary hover:bg-panel-raised"
        >
          Refresh Analytics
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
        <div className="flex flex-col gap-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded-[6px] border border-hairline bg-panel p-4">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Total Revenue At Risk
              </span>
              <p className="font-data m-0 mt-1.5 text-[22px] font-bold text-primary">
                {formatInr(atRisk)}
              </p>
              <p className="m-0 mt-1 text-[11px] text-secondary">
                {summary?.total_cases ?? 0} total cases tracked
              </p>
            </div>

            <div className="rounded-[6px] border border-hairline bg-panel p-4">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Recovered Revenue
              </span>
              <p className="font-data m-0 mt-1.5 text-[22px] font-bold text-recovered">
                {formatInr(recovered)}
              </p>
              <p className="m-0 mt-1 text-[11px] text-recovered">
                {summary?.successful_recoveries ?? 0} full · {summary?.partial_recoveries ?? 0} partial
              </p>
            </div>

            <div className="rounded-[6px] border border-hairline bg-panel p-4">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Capital Under Review / Gated
              </span>
              <p className="font-data m-0 mt-1.5 text-[22px] font-bold text-primary">
                {formatInr(remaining)}
              </p>
              <p className="m-0 mt-1 text-[11px] text-tertiary">
                {summary?.blocked_cases ?? 0} blocked · {summary?.human_review_cases ?? 0} human review
              </p>
            </div>

            <div className="rounded-[6px] border border-hairline bg-panel p-4">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Gross Recovery Yield
              </span>
              <p className="font-data m-0 mt-1.5 text-[22px] font-bold text-recovered">
                {rate.toFixed(1)}%
              </p>
              <p className="m-0 mt-1 text-[11px] text-secondary">
                Across {summary?.available_source_events.toLocaleString('en-IN')} uningested events
              </p>
            </div>
          </div>

          {/* Breakdown Grids */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* 1. Outcomes Distribution */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <h3 className="m-0 text-[14px] font-semibold text-primary">
                Outcomes Distribution
              </h3>
              <p className="mt-1 mb-4 text-[12px] text-secondary">
                Terminal outcomes across processed cases
              </p>
              <div className="flex flex-col gap-3">
                {Object.entries(outcomes).map(([outcome, count]) => {
                  const pct = summary?.total_cases ? ((count / summary.total_cases) * 100).toFixed(0) : '0'
                  return (
                    <div key={outcome}>
                      <div className="flex items-center justify-between text-[12px] mb-1">
                        <span className="capitalize font-medium text-primary">{outcome}</span>
                        <span className="font-data text-secondary">{count} ({pct}%)</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-ink overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            outcome === 'recovered'
                              ? 'bg-recovered'
                              : outcome === 'blocked'
                                ? 'bg-risk'
                                : 'bg-escalate'
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 2. Action Spaces Executed */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <h3 className="m-0 text-[14px] font-semibold text-primary">
                Action Space Utilization
              </h3>
              <p className="mt-1 mb-4 text-[12px] text-secondary">
                Interventions selected by Decision Engine
              </p>
              <div className="flex flex-col gap-3">
                {Object.entries(actions).map(([act, count]) => {
                  const pct = summary?.total_cases ? ((count / summary.total_cases) * 100).toFixed(0) : '0'
                  return (
                    <div key={act}>
                      <div className="flex items-center justify-between text-[12px] mb-1">
                        <span className="font-data font-medium text-agent">{act}</span>
                        <span className="font-data text-secondary">{count} ({pct}%)</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-ink overflow-hidden">
                        <div className="h-full rounded-full bg-agent" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* 3. Surface Mix */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <h3 className="m-0 text-[14px] font-semibold text-primary">
                Revenue Surface Mix
              </h3>
              <p className="mt-1 mb-4 text-[12px] text-secondary">
                Distribution across loss vectors
              </p>
              <div className="flex flex-col gap-3">
                {Object.entries(eventTypes).map(([type, count]) => {
                  const pct = summary?.total_cases ? ((count / summary.total_cases) * 100).toFixed(0) : '0'
                  return (
                    <div key={type}>
                      <div className="flex items-center justify-between text-[12px] mb-1">
                        <span className="font-medium text-primary">{formatEventType(type)}</span>
                        <span className="font-data text-secondary">{count} ({pct}%)</span>
                      </div>
                      <div className="h-1.5 w-full rounded-full bg-ink overflow-hidden">
                        <div className="h-full rounded-full bg-recovered" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Dataset Ingestion Pipeline Health */}
          <div className="rounded-[6px] border border-hairline bg-panel p-5">
            <h3 className="m-0 text-[14px] font-semibold text-primary">
              Canonical Reservoir Capacity
            </h3>
            <p className="mt-1 mb-3 text-[12px] text-secondary">
              Available un-ingested revenue-at-risk source events in storage
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 text-[12px]">
              <div className="rounded bg-ink p-3">
                <span className="text-tertiary">Total Available Events:</span>
                <p className="font-data m-0 mt-1 text-[16px] font-semibold text-primary">
                  {summary?.available_source_events.toLocaleString('en-IN')} events
                </p>
              </div>
              <div className="rounded bg-ink p-3">
                <span className="text-tertiary">Total Unrecovered Capital Pool:</span>
                <p className="font-data m-0 mt-1 text-[16px] font-semibold text-primary">
                  {formatInr(summary?.available_source_amount ?? 0)}
                </p>
              </div>
              <div className="rounded bg-ink p-3">
                <span className="text-tertiary">Active Batches Configured:</span>
                <p className="font-data m-0 mt-1 text-[16px] font-semibold text-agent">
                  7 batches ready
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
