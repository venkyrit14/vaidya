import { useState } from 'react'
import { CaseDetailsModal } from './CaseDetailsModal.tsx'
import { useRecoveryRecords } from '../hooks/useRecoveryData.ts'
import {
  formatEventType,
  formatInr,
  formatRootCause,
} from '../lib/agentPipeline.ts'

export function ActionHistoryPage() {
  const { data, loading, refresh, setParams } = useRecoveryRecords({ page: 1, limit: 20 })
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null)

  const items = data?.items || []

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <h2 className="m-0 text-[18px] font-semibold text-primary">
            Autonomous Action Audit Trail
          </h2>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Chronological audit log of all decisions, policy gates, and execution actions taken by Vaidya
          </p>
        </div>

        <button
          type="button"
          onClick={() => refresh()}
          className="cursor-pointer rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] text-primary hover:bg-panel-raised"
        >
          Refresh Ledger
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-auto px-6 py-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-secondary">
            <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
            <p className="mt-3 text-[13px]">Streaming immutable audit logs...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-[6px] border border-dashed border-hairline p-16 text-center text-secondary">
            <p className="text-[14px] font-medium text-primary">No actions recorded yet</p>
            <p className="mt-1 text-[12px]">Processed recovery cases will automatically appear in this immutable timeline.</p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-[6px] border border-hairline bg-panel">
            <table className="w-full text-left text-[12px] border-collapse">
              <thead>
                <tr className="border-b border-hairline bg-ink text-[11px] uppercase tracking-wider text-tertiary">
                  <th className="px-4 py-3 font-semibold">Timestamp</th>
                  <th className="px-4 py-3 font-semibold">Case ID</th>
                  <th className="px-4 py-3 font-semibold">Surface</th>
                  <th className="px-4 py-3 font-semibold">Action Taken</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold">At Risk</th>
                  <th className="px-4 py-3 font-semibold">Recovered</th>
                  <th className="px-4 py-3 font-semibold">Outcome</th>
                  <th className="px-4 py-3 font-semibold">Audit Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hairline">
                {items.map((rec) => (
                  <tr
                    key={rec.case_id}
                    onClick={() => setSelectedCaseId(rec.case_id)}
                    className="cursor-pointer hover:bg-panel-raised transition-colors"
                  >
                    <td className="px-4 py-3 font-data text-tertiary">
                      {rec.timestamp ? new Date(rec.timestamp).toLocaleString('en-IN') : '—'}
                    </td>
                    <td className="px-4 py-3 font-data font-semibold text-agent">
                      {rec.case_id}
                    </td>
                    <td className="px-4 py-3 text-primary">
                      {formatEventType(rec.event_type)}
                    </td>
                    <td className="px-4 py-3 font-data font-medium text-primary">
                      {rec.action}
                    </td>
                    <td className="px-4 py-3 font-data text-secondary">
                      {rec.execution_status}
                    </td>
                    <td className="px-4 py-3 font-data text-primary">
                      {formatInr(rec.amount_at_risk)}
                    </td>
                    <td className="px-4 py-3 font-data text-recovered font-medium">
                      {formatInr(rec.recovered_amount)}
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
                    <td className="px-4 py-3 text-secondary max-w-xs truncate">
                      {formatRootCause(rec.message)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {data && data.total_pages > 1 ? (
        <footer className="flex shrink-0 items-center justify-between border-t border-hairline bg-panel px-6 py-3 text-[12px]">
          <span className="text-secondary">
            Page <strong className="text-primary">{data.page}</strong> of{' '}
            <strong className="text-primary">{data.total_pages}</strong> ({data.total} audit records)
          </span>
          <div className="flex items-center gap-2">
            <button
               disabled={data?.page <= 1}
               onClick={() => setParams({ page: (data?.page ?? 1) - 1 })}
               className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
             >
               Previous
             </button>
             <button
               type="button"
               disabled={data?.page >= data?.total_pages}
               onClick={() => setParams({ page: (data?.page ?? 1) + 1 })}
               className="rounded border border-hairline bg-ink px-3 py-1 font-medium text-secondary hover:text-primary disabled:opacity-40"
             >
               Next
            </button>
          </div>
        </footer>
      ) : null}

      <CaseDetailsModal
        caseId={selectedCaseId}
        onClose={() => setSelectedCaseId(null)}
      />
    </div>
  )
}
