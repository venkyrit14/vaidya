import { useSystemStatus } from '../hooks/useRecoveryData.ts'

export function SystemHealthPage() {
  const { status, loading, error, refresh } = useSystemStatus(10000)

  if (loading && !status) {
    return (
      <div className="flex h-full items-center justify-center bg-ink text-secondary">
        <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
        <span className="ml-3 text-[13px]">Polling subsystem telemetry...</span>
      </div>
    )
  }

  const isNominal = !error && status !== null

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="m-0 text-[18px] font-semibold text-primary">
              System Telemetry & Operational Health
            </h2>
            <span
              className={`font-data rounded px-2 py-0.5 text-[11px] font-semibold uppercase ${
                isNominal
                  ? 'bg-recovered/15 text-recovered'
                  : 'bg-risk/15 text-risk'
              }`}
            >
              {isNominal ? 'ALL SUBSYSTEMS NOMINAL' : 'CONNECTIVITY DEGRADED'}
            </span>
          </div>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Continuous health telemetry across AI reasoning, RAG vector retrieval, policy gating, execution sandbox, and recovery ledger
          </p>
        </div>

        <button
          type="button"
          onClick={() => refresh()}
          className="cursor-pointer rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] text-primary hover:bg-panel-raised"
        >
          Ping Subsystems
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
        {error ? (
          <div className="mb-6 rounded-[6px] border border-risk/40 bg-risk/10 p-4 text-[13px] text-risk">
            <p className="font-semibold">Backend Gateway Unreachable</p>
            <p className="mt-1 text-[12px] opacity-90">{error.message}</p>
          </div>
        ) : null}

        {status ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* 1. Core API */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.api.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.api.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">FastAPI application server</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Version:</span>
                  <span className="font-data text-primary">{status.api.version}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Protocol:</span>
                  <span className="font-data text-primary">HTTP/JSON REST</span>
                </div>
              </div>
            </div>

            {/* 2. Decision Engine */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.decision_engine.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.decision_engine.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">Deterministic AI reasoning layer</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Initialized:</span>
                  <span className="font-data text-recovered">
                    {status.decision_engine.initialized ? 'TRUE' : 'FALSE'}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Action Spaces:</span>
                  <span className="font-data text-primary">
                    {status.decision_engine.action_spaces_count} surfaces configured
                  </span>
                </div>
              </div>
            </div>

            {/* 3. Retrieval Service */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.retrieval_service.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.retrieval_service.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">RAG historical similarity corpus</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Corpus Size:</span>
                  <span className="font-data text-primary">
                    {status.retrieval_service.corpus_size.toLocaleString()} cases
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Similarity Threshold:</span>
                  <span className="font-data text-primary">
                    {(status.retrieval_service.similarity_threshold * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Source Storage:</span>
                  <span className="font-data text-tertiary truncate max-w-[120px]">
                    {status.retrieval_service.storage_file}
                  </span>
                </div>
              </div>
            </div>

            {/* 4. Policy Engine */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.policy_engine.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.policy_engine.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">Safety boundary enforcement</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Max Auto Limit:</span>
                  <span className="font-data text-primary">
                    ₹{status.policy_engine.max_automation_amount.toLocaleString('en-IN')}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Min Confidence:</span>
                  <span className="font-data text-primary">
                    {(status.policy_engine.min_confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            {/* 5. Execution Service */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.execution_service.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.execution_service.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">Downstream gateway action executor</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Execution Mode:</span>
                  <span className="font-data text-primary">
                    {status.execution_service.mode}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Payment Gateway:</span>
                  <span className="font-data text-primary">
                    {status.execution_service.live_payment_gateway}
                  </span>
                </div>
              </div>
            </div>

            {/* 6. Recovery Tracker */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-semibold text-primary">
                  {status.recovery_tracker.name}
                </span>
                <span className="rounded bg-recovered/15 px-2 py-0.5 text-[10px] font-semibold text-recovered uppercase">
                  {status.recovery_tracker.status}
                </span>
              </div>
              <p className="mt-1 mb-3 text-[12px] text-secondary">Audit ledger & persistence store</p>
              <div className="rounded bg-ink p-3 text-[12px]">
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Persisted Records:</span>
                  <span className="font-data font-semibold text-agent">
                    {status.recovery_tracker.persisted_records_count} cases
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-tertiary">Ledger Storage:</span>
                  <span className="font-data text-tertiary">
                    {status.recovery_tracker.storage_file}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  )
}
