import { useState } from 'react'
import { CaseDetailsModal } from './CaseDetailsModal.tsx'
import { useRecoveryRecords } from '../hooks/useRecoveryData.ts'
import {
  formatEventType,
  formatInr,
  formatRootCause,
} from '../lib/agentPipeline.ts'

export function HumanReviewPage() {
  const { data, loading, refresh } = useRecoveryRecords({
    requires_human: true,
    page: 1,
    limit: 50,
  })

  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null)

  const items = data?.items || []

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="m-0 text-[18px] font-semibold text-primary">
              Human Review & Escalation Queue
            </h2>
            <span className="font-data rounded bg-escalate/15 px-2 py-0.5 text-[11px] font-medium text-escalate">
              {data?.total ?? 0} Pending
            </span>
          </div>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Transactions intercepted by PolicyEngine thresholds or security zero-tolerance rules requiring merchant approval
          </p>
        </div>

        <button
          type="button"
          onClick={() => refresh()}
          className="cursor-pointer rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] text-primary hover:bg-panel-raised"
        >
          Refresh Queue
        </button>
      </header>

      {/* Safety Policy Explainer */}
      <div className="flex items-center justify-between border-b border-hairline bg-panel/40 px-6 py-2.5 text-[12px]">
        <span className="text-secondary">
          <strong className="text-escalate">Policy Gate Criteria:</strong> Cases exceeding ₹1,00,000 threshold or flagged with elevated risk/fraud are strictly quarantined from automated recovery.
        </span>
        <span className="font-data text-tertiary">Real-time ledger gated</span>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-secondary">
            <span className="live-indicator h-3 w-3 rounded-full bg-escalate" />
            <p className="mt-3 text-[13px]">Scanning review queue...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-[6px] border border-dashed border-hairline p-16 text-center text-secondary">
            <p className="text-[14px] font-medium text-primary">Queue is clear</p>
            <p className="mt-1 text-[12px]">No transactions currently require human intervention or security clearance.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {items.map((caseItem) => {
              const isBlocked = caseItem.outcome === 'blocked'

              return (
                <div
                  key={caseItem.case_id}
                  onClick={() => setSelectedCaseId(caseItem.case_id)}
                  className={`cursor-pointer rounded-[6px] border p-5 transition-all duration-150 ${
                    isBlocked
                      ? 'border-risk/40 bg-risk/[0.02] hover:border-risk'
                      : 'border-escalate/40 bg-escalate/[0.02] hover:border-escalate'
                  }`}
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <span className="font-data text-[13px] font-semibold text-agent">
                        {caseItem.case_id}
                      </span>
                      <span className="rounded bg-panel px-2 py-0.5 text-[11px] font-medium text-secondary">
                        {formatEventType(caseItem.event_type)}
                      </span>
                      <span
                        className={`rounded px-2 py-0.5 text-[10px] font-semibold ${
                          isBlocked
                            ? 'bg-risk/15 text-risk'
                            : 'bg-escalate/15 text-escalate'
                        }`}
                      >
                        {isBlocked ? 'PROHIBITED / BLOCKED' : 'AWAITING APPROVAL'}
                      </span>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className="font-data text-[16px] font-semibold text-primary">
                        {formatInr(caseItem.amount_at_risk)}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedCaseId(caseItem.case_id)
                        }}
                        className="rounded border border-hairline bg-panel px-3 py-1 text-[12px] font-medium text-primary hover:bg-panel-raised"
                      >
                        Review Case
                      </button>
                    </div>
                  </div>

                  <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3 text-[12px]">
                    <div className="rounded bg-ink/60 p-2.5">
                      <span className="text-[11px] font-medium uppercase text-tertiary">
                        AI Recommended Action
                      </span>
                      <p className="font-data m-0 mt-1 font-semibold text-primary">
                        {caseItem.action}
                      </p>
                    </div>

                    <div className="rounded bg-ink/60 p-2.5">
                      <span className="text-[11px] font-medium uppercase text-tertiary">
                        Intervention Reason
                      </span>
                      <p className="m-0 mt-1 text-secondary line-clamp-1">
                        {formatRootCause(caseItem.message)}
                      </p>
                    </div>

                    <div className="rounded bg-ink/60 p-2.5">
                      <span className="text-[11px] font-medium uppercase text-tertiary">
                        Recorded Timestamp
                      </span>
                      <p className="font-data m-0 mt-1 text-tertiary">
                        {caseItem.timestamp ? new Date(caseItem.timestamp).toLocaleString('en-IN') : '—'}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Details modal */}
      <CaseDetailsModal
        caseId={selectedCaseId}
        onClose={() => setSelectedCaseId(null)}
      />
    </div>
  )
}
