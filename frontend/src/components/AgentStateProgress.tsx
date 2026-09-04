import type { ReactNode } from 'react'
import {
  getStageIndex,
  isTerminalState,
} from '../lib/agentPipeline.ts'
import type { LiveFeedEvent, SimulatedAgentState } from '../types/liveFeed.ts'

type AgentStateProgressProps = {
  event?: LiveFeedEvent
  outcome?: string
  requiresHuman?: boolean
  simulatedState?: SimulatedAgentState
}

type StageMeta = {
  id: SimulatedAgentState
  label: string
  shortLabel: string
}

const STAGE_CONFIGS: StageMeta[] = [
  { id: 'detected', label: 'Detected', shortLabel: 'Detected' },
  { id: 'diagnosing', label: 'Diagnosing', shortLabel: 'Diagnosing' },
  { id: 'evidence', label: 'Evidence', shortLabel: 'Evidence' },
  { id: 'decision', label: 'Decision', shortLabel: 'Decision' },
  { id: 'policy', label: 'Policy', shortLabel: 'Policy' },
  { id: 'action', label: 'Action', shortLabel: 'Action' },
  { id: 'outcome', label: 'Outcome', shortLabel: 'Outcome' },
]

export function AgentStateProgress({
  event,
  outcome: propOutcome,
  requiresHuman: propRequiresHuman,
  simulatedState: propState,
}: AgentStateProgressProps) {
  // Derive state and outcome whether fed from simulated event or real backend record
  const state: SimulatedAgentState = propState || event?.simulatedState || 'outcome'
  const currentIdx = getStageIndex(state)
  const isComplete = isTerminalState(state)

  let outcomeType: 'recovered' | 'blocked' | 'human_review' = 'recovered'
  if (event) {
    outcomeType = event.finalOutcome
  } else {
    const rawOutcome = propOutcome?.toLowerCase() || ''
    if (rawOutcome === 'blocked') {
      outcomeType = 'blocked'
    } else if (
      rawOutcome === 'human_review' ||
      rawOutcome === 'pending' ||
      propRequiresHuman
    ) {
      outcomeType = 'human_review'
    } else if (rawOutcome === 'recovered') {
      outcomeType = 'recovered'
    } else {
      outcomeType = 'recovered'
    }
  }

  return (
    <div
      aria-label="Horizontal agent pipeline progression"
      className="w-full py-1.5"
    >
      <div className="flex w-full items-center justify-between">
        {STAGE_CONFIGS.map((stage, idx) => {
          const isPassed = idx < currentIdx
          const isCurrent = idx === currentIdx
          const isLast = idx === STAGE_CONFIGS.length - 1

          // Determine node styling
          let nodeBg: string
          let textColor: string
          let dotInner: ReactNode

          if (isPassed) {
            nodeBg = 'border-agent/60 bg-agent/20 text-agent'
            textColor = 'text-secondary'
            dotInner = <span className="h-1.5 w-1.5 rounded-full bg-agent" />
          } else if (isCurrent) {
            if (isLast && isComplete) {
              if (outcomeType === 'recovered') {
                nodeBg = 'border-recovered bg-recovered/20 text-recovered'
                textColor = 'text-recovered font-medium'
                dotInner = <span className="h-2 w-2 rounded-full bg-recovered" />
              } else if (outcomeType === 'blocked') {
                nodeBg = 'border-risk bg-risk/20 text-risk'
                textColor = 'text-risk font-medium'
                dotInner = <span className="h-2 w-2 rounded-full bg-risk" />
              } else {
                nodeBg = 'border-escalate bg-escalate/20 text-escalate'
                textColor = 'text-escalate font-medium'
                dotInner = <span className="h-2 w-2 rounded-full bg-escalate" />
              }
            } else {
              nodeBg = 'border-agent bg-agent/25 text-agent node-active-pulse'
              textColor = 'text-agent font-medium'
              dotInner = <span className="h-2 w-2 rounded-full bg-agent" />
            }
          } else {
            // Future
            nodeBg = 'border-hairline bg-ink'
            textColor = 'text-tertiary'
            dotInner = <span className="h-1 w-1 rounded-full bg-hairline" />
          }

          // Line styling between this node and next
          const isNextReached = idx < currentIdx

          return (
            <div
              key={stage.id}
              className={`flex items-center ${isLast ? 'flex-none' : 'flex-1'}`}
            >
              {/* Node and Label */}
              <div className="flex flex-col items-center">
                <div
                  className={`relative flex h-5 w-5 items-center justify-center rounded-full border transition-all duration-200 ${nodeBg}`}
                  title={`${stage.label}: ${
                    isCurrent
                      ? 'In progress'
                      : isPassed
                        ? 'Completed'
                        : 'Pending'
                  }`}
                >
                  {dotInner}
                </div>
                <span
                  className={`mt-1.5 text-[11px] tracking-tight transition-colors duration-150 ${textColor}`}
                >
                  {isLast && isComplete
                    ? outcomeType === 'recovered'
                      ? 'Recovered'
                      : outcomeType === 'blocked'
                        ? 'Blocked'
                        : 'Review'
                    : stage.shortLabel}
                </span>
              </div>

              {/* Connecting line to next stage */}
              {!isLast ? (
                <div
                  className={`mx-1.5 mb-4 h-[2px] flex-1 transition-all duration-300 ${
                    isNextReached ? 'bg-agent/60' : 'bg-hairline'
                  }`}
                  aria-hidden="true"
                />
              ) : null}
            </div>
          )
        })}
      </div>
    </div>
  )
}
