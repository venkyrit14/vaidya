import { useMemo, useState } from 'react'
import { BatchControls } from './BatchControls.tsx'
import type { FilterStatus } from './BatchControls.tsx'
import { CaseDetailsModal } from './CaseDetailsModal.tsx'
import { CommandHeader } from './CommandHeader.tsx'
import { KpiStrip } from './KpiStrip.tsx'
import { LiveFeed } from './LiveFeed.tsx'
import { processBatch } from '../api/recovery.ts'
import {
  useBatches,
  useRecoveryRecords,
  useRecoverySummary,
} from '../hooks/useRecoveryData.ts'

export function CommandCenter() {
  const { summary, loading: summaryLoading, refresh: refreshSummary } = useRecoverySummary(10000)
  const { batches, loading: batchesLoading, refresh: refreshBatches } = useBatches()
  const {
    data: recordsData,
    loading: recordsLoading,
    refresh: refreshRecords,
  } = useRecoveryRecords({ page: 1, limit: 50 })

  const [selectedBatchId, setSelectedBatchId] = useState<string>('BATCH_DEMO_01')
  const [filter, setFilter] = useState<FilterStatus>('all')
  const [running, setRunning] = useState(false)
  const [activeCount, setActiveCount] = useState(0)
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null)
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)

  // Derive valid batch ID based on loaded batches
  const effectiveBatchId = useMemo(() => {
    if (batches.length === 0) return selectedBatchId
    return batches.some((b) => b.batch_id === selectedBatchId)
      ? selectedBatchId
      : batches[0].batch_id
  }, [batches, selectedBatchId])

  // Filter records based on outcome/status
  const displayedRecords = useMemo(() => {
    const items = recordsData?.items || []
    if (filter === 'all') return items
    if (filter === 'recovered') {
      return items.filter((r) => r.outcome === 'recovered')
    }
    if (filter === 'human_review') {
      return items.filter(
        (r) => r.requires_human || r.outcome === 'pending' || r.outcome === 'human_review',
      )
    }
    if (filter === 'blocked') {
      return items.filter((r) => r.outcome === 'blocked')
    }
    return items
  }, [recordsData?.items, filter])

  const handleRefreshAll = () => {
    void refreshSummary()
    void refreshBatches()
    void refreshRecords()
  }

  const handleRunBatch = async () => {
    if (!effectiveBatchId || running) return
    setRunning(true)
    setFeedbackMessage(null)

    const batch = batches.find((b) => b.batch_id === effectiveBatchId)
    setActiveCount(batch ? Math.min(batch.total_events, 20) : 10)

    try {
      const resp = await processBatch({
        batch_id: effectiveBatchId,
        limit: 50,
      })
      setFeedbackMessage(
        `Successfully processed ${resp.processed_count} events from batch ${effectiveBatchId}`,
      )
      // Refresh backend datasets
      await Promise.all([refreshSummary(), refreshBatches(), refreshRecords()])
    } catch (err) {
      setFeedbackMessage(
        `Batch processing failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
      )
    } finally {
      setRunning(false)
      setActiveCount(0)
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <CommandHeader />
      <KpiStrip summary={summary} loading={summaryLoading} />

      {feedbackMessage ? (
        <div className="flex items-center justify-between border-b border-hairline bg-panel-raised px-6 py-2 text-[12px] text-primary">
          <span>{feedbackMessage}</span>
          <button
            type="button"
            onClick={() => setFeedbackMessage(null)}
            className="cursor-pointer text-tertiary hover:text-primary"
          >
            ✕
          </button>
        </div>
      ) : null}

      <BatchControls
        summary={summary}
        batches={batches}
        selectedBatchId={effectiveBatchId}
        running={running || batchesLoading}
        activeCasesCount={activeCount}
        filter={filter}
        onSelectBatch={setSelectedBatchId}
        onRunBatch={handleRunBatch}
        onRefresh={handleRefreshAll}
        onFilterChange={setFilter}
      />

      <LiveFeed
        records={displayedRecords}
        running={running || recordsLoading}
        onRunBatch={handleRunBatch}
        onSelectCase={(id) => setSelectedCaseId(id)}
      />

      {/* Dedicated Case Details Modal */}
      <CaseDetailsModal
        caseId={selectedCaseId}
        onClose={() => setSelectedCaseId(null)}
      />
    </div>
  )
}
