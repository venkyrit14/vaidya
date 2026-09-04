import { AgentStateProgress } from './AgentStateProgress.tsx'
import {
  formatEventType,
  formatInr,
  formatRootCause,
  getStageIndex,
  isTerminalState,
} from '../lib/agentPipeline.ts'
import type { LiveFeedEvent } from '../types/liveFeed.ts'
import type { RecoveryRecord } from '../types/recovery.ts'

type LiveFeedEventCardProps = {
  event?: LiveFeedEvent
  record?: RecoveryRecord
  onSelectCase?: (caseId: string) => void
}

export function LiveFeedEventCard({
  event,
  record,
  onSelectCase,
}: LiveFeedEventCardProps) {
  // If record is passed directly from backend
  if (record) {
    const isRecovered = record.outcome === 'recovered'
    const isBlocked = record.outcome === 'blocked'

    const getBorder = () => {
      if (isRecovered) return 'border-hairline hover:border-recovered/60'
      if (isBlocked) return 'border-risk/40 bg-risk/[0.02] hover:border-risk/60'
      return 'border-escalate/40 bg-escalate/[0.02] hover:border-escalate/60'
    }

    return (
      <article
        role="button"
        tabIndex={0}
        onClick={() => onSelectCase?.(record.case_id)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onSelectCase?.(record.case_id)
          }
        }}
        className={`feed-event-enter cursor-pointer rounded-[6px] border bg-panel px-5 py-4 transition-all duration-150 ${getBorder()} hover:bg-panel-raised focus:outline-none focus:ring-1 focus:ring-agent`}
        aria-label={`Case ${record.case_id} Details`}
      >
        {/* Top row */}
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="text-[14px] font-semibold text-primary">
              {formatEventType(record.event_type)}
            </span>
            <span className="font-data text-[12px] font-medium text-agent">
              {record.case_id}
            </span>
            <span className="rounded-[4px] bg-panel px-2 py-0.5 text-[11px] text-tertiary">
              Click for telemetry
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="font-data text-[15px] font-semibold text-primary">
              {formatInr(record.amount_at_risk)}
            </span>
            {isRecovered ? (
              <span className="flex items-center gap-1.5 rounded-[4px] border border-recovered/40 bg-recovered/10 px-2 py-0.5 text-[11px] font-medium text-recovered">
                <span>Recovered {formatInr(record.recovered_amount)}</span>
              </span>
            ) : isBlocked ? (
              <span className="flex items-center gap-1.5 rounded-[4px] border border-risk/40 bg-risk/10 px-2 py-0.5 text-[11px] font-medium text-risk">
                <span>Blocked for safety</span>
              </span>
            ) : (
              <span className="flex items-center gap-1.5 rounded-[4px] border border-escalate/40 bg-escalate/10 px-2 py-0.5 text-[11px] font-medium text-escalate">
                <span>Human review required</span>
              </span>
            )}
          </div>
        </header>

        {/* Message / Explanation */}
        <div className="mt-1.5 flex items-center justify-between gap-2">
          <p className="m-0 text-[13px] font-medium text-secondary line-clamp-1">
            {formatRootCause(record.message)}
          </p>
          <span className="font-data text-[11px] text-tertiary shrink-0">
            {record.timestamp ? new Date(record.timestamp).toLocaleTimeString() : '—'}
          </span>
        </div>

        {/* Horizontal Connected 7-Stage Agent Pipeline */}
        <div className="mt-3.5 mb-3 border-t border-b border-hairline/60 py-2">
          <AgentStateProgress
            outcome={record.outcome}
            requiresHuman={record.requires_human}
            simulatedState="outcome"
          />
        </div>

        {/* 4-Pillar Reasoning Grid */}
        <div className="grid grid-cols-1 gap-3 text-[12px] sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-[4px] bg-ink/60 p-2.5">
            <span className="text-[11px] font-medium uppercase tracking-wide text-tertiary">
              Action Taken
            </span>
            <p className="font-data m-0 mt-1 text-[12px] font-medium text-primary">
              {record.action}
            </p>
          </div>
          <div className="rounded-[4px] bg-ink/60 p-2.5">
            <span className="text-[11px] font-medium uppercase tracking-wide text-tertiary">
              Execution Status
            </span>
            <p className="font-data m-0 mt-1 text-[12px] text-primary">
              {record.execution_status}
            </p>
          </div>
          <div className="rounded-[4px] bg-ink/60 p-2.5">
            <span className="text-[11px] font-medium uppercase tracking-wide text-tertiary">
              Governance Gate
            </span>
            <p className="font-data m-0 mt-1 text-[12px] font-medium">
              <span className={record.requires_human ? 'text-escalate' : isBlocked ? 'text-risk' : 'text-recovered'}>
                {record.requires_human ? 'HUMAN REVIEW' : isBlocked ? 'PROHIBITED' : 'APPROVED'}
              </span>
            </p>
          </div>
          <div className="rounded-[4px] bg-ink/60 p-2.5">
            <span className="text-[11px] font-medium uppercase tracking-wide text-tertiary">
              Net Result
            </span>
            <p className="m-0 mt-1 text-[12px] font-medium text-primary">
              {isRecovered ? `+${formatInr(record.recovered_amount)}` : isBlocked ? 'Protected' : 'Pending Review'}
            </p>
          </div>
        </div>
      </article>
    )
  }

  // Otherwise, render simulated event
  if (!event) return null

  const currentStageIdx = getStageIndex(event.simulatedState)
  const isComplete = isTerminalState(event.simulatedState)

  const showEvidence = currentStageIdx >= 2
  const showDecision = currentStageIdx >= 3
  const showPolicy = currentStageIdx >= 4
  const showExecution = currentStageIdx >= 5

  const getOutcomeBadge = () => {
    if (!isComplete) {
      return (
        <span className="flex items-center gap-1.5 rounded-[4px] border border-agent/40 bg-agent/10 px-2 py-0.5 text-[11px] font-medium text-agent">
          <span className="live-indicator h-1.5 w-1.5 rounded-full bg-agent" />
          <span>In progress</span>
        </span>
      )
    }

    if (event.finalOutcome === 'recovered') {
      return (
        <span className="flex items-center gap-1.5 rounded-[4px] border border-recovered/40 bg-recovered/10 px-2 py-0.5 text-[11px] font-medium text-recovered">
          <span>Recovered {formatInr(event.recoveredAmount)}</span>
        </span>
      )
    }

    if (event.finalOutcome === 'blocked') {
      return (
        <span className="flex items-center gap-1.5 rounded-[4px] border border-risk/40 bg-risk/10 px-2 py-0.5 text-[11px] font-medium text-risk">
          <span>Blocked for safety</span>
        </span>
      )
    }

    return (
      <span className="flex items-center gap-1.5 rounded-[4px] border border-escalate/40 bg-escalate/10 px-2 py-0.5 text-[11px] font-medium text-escalate">
        <span>Human review required</span>
      </span>
    )
  }

  const getCardBorderClass = () => {
    if (!isComplete) return 'border-agent/60 shadow-[0_0_12px_rgba(76,124,243,0.08)]'
    if (event.finalOutcome === 'recovered') return 'border-hairline hover:border-recovered/40'
    if (event.finalOutcome === 'blocked') return 'border-risk/40 bg-risk/[0.02]'
    return 'border-escalate/40 bg-escalate/[0.02]'
  }

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={() => onSelectCase?.(event.caseId)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelectCase?.(event.caseId)
        }
      }}
      className={`feed-event-enter cursor-pointer rounded-[6px] border bg-panel px-5 py-4 transition-all duration-150 ${getCardBorderClass()} hover:bg-panel-raised focus:outline-none focus:ring-1 focus:ring-agent`}
      aria-label={`Case ${event.caseId} Details`}
    >
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="text-[14px] font-semibold text-primary">
            {formatEventType(event.eventType)}
          </span>
          <span className="font-data text-[12px] text-agent">
            {event.caseId}
          </span>
          <span className="rounded-[4px] bg-panel px-2 py-0.5 text-[11px] text-tertiary">
            Click for telemetry
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="font-data text-[15px] font-semibold text-primary">
            {formatInr(event.amount)}
          </span>
          {getOutcomeBadge()}
        </div>
      </header>

      <div className="mt-1.5 flex items-center gap-2">
        <p className="m-0 text-[13px] font-medium text-secondary">
          {formatRootCause(event.rootCause)}
        </p>
      </div>

      <div className="mt-3.5 mb-3 border-t border-b border-hairline/60 py-2">
        <AgentStateProgress event={event} />
      </div>

      <div className="grid grid-cols-1 gap-3 text-[12px] sm:grid-cols-2 lg:grid-cols-4">
        <div className="flex flex-col justify-between rounded-[4px] bg-ink/60 p-2.5">
          <span className="text-[11px] font-medium tracking-wide text-tertiary uppercase">
            Historical Evidence
          </span>
          <div className="mt-1">
            {showEvidence ? (
              <p className="m-0 text-[12px] text-primary">{event.evidence.note}</p>
            ) : (
              <span className="font-data text-[11px] text-tertiary">Querying vector corpus...</span>
            )}
          </div>
        </div>

        <div className="flex flex-col justify-between rounded-[4px] bg-ink/60 p-2.5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-medium tracking-wide text-tertiary uppercase">
              AI Decision
            </span>
            {showDecision && (
              <span className="font-data text-[11px] font-medium text-agent">
                {event.decision.confidence.toFixed(2)}% conf
              </span>
            )}
          </div>
          <div className="mt-1">
            {showDecision ? (
              <p className="font-data m-0 text-[12px] font-medium text-primary">
                {event.decision.action}
              </p>
            ) : (
              <span className="font-data text-[11px] text-tertiary">Evaluating actions...</span>
            )}
          </div>
        </div>

        <div className="flex flex-col justify-between rounded-[4px] bg-ink/60 p-2.5">
          <span className="text-[11px] font-medium tracking-wide text-tertiary uppercase">
            Policy Gate
          </span>
          <div className="mt-1">
            {showPolicy ? (
              <div>
                <span
                  className={`font-data text-[11px] font-semibold ${
                    event.policy.status === 'APPROVED'
                      ? 'text-recovered'
                      : event.policy.status === 'AUTOMATIC RECOVERY PROHIBITED'
                        ? 'text-risk'
                        : 'text-escalate'
                  }`}
                >
                  {event.policy.status}
                </span>
                {event.policy.reason ? (
                  <p className="m-0 mt-0.5 line-clamp-1 text-[11px] text-secondary">
                    {event.policy.reason}
                  </p>
                ) : null}
              </div>
            ) : (
              <span className="font-data text-[11px] text-tertiary">Evaluating policy rules...</span>
            )}
          </div>
        </div>

        <div className="flex flex-col justify-between rounded-[4px] bg-ink/60 p-2.5">
          <span className="text-[11px] font-medium tracking-wide text-tertiary uppercase">
            {isComplete ? 'Final Outcome' : 'Execution'}
          </span>
          <div className="mt-1">
            {showExecution ? (
              <p
                className={`m-0 text-[12px] ${
                  isComplete
                    ? event.finalOutcome === 'recovered'
                      ? 'font-medium text-recovered'
                      : event.finalOutcome === 'blocked'
                        ? 'font-medium text-risk'
                        : 'font-medium text-escalate'
                    : 'text-agent'
                }`}
              >
                {isComplete ? event.outcomeMessage : event.execution.status}
              </p>
            ) : (
              <span className="font-data text-[11px] text-tertiary">Awaiting policy pass...</span>
            )}
          </div>
        </div>
      </div>
    </article>
  )
}
