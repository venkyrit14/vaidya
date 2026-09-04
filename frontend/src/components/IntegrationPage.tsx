import { useSystemStatus } from '../hooks/useRecoveryData.ts'

export function IntegrationPage() {
  const { status, loading } = useSystemStatus()

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <h2 className="m-0 text-[18px] font-semibold text-primary">
            Integration Architecture & Gateway Connectivity
          </h2>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Payment gateway hooks, simulated sandbox environment, and event ingestion feeds
          </p>
        </div>

        <div className="flex items-center gap-2 rounded border border-hairline bg-panel px-3 py-1.5 text-[12px] font-medium text-secondary">
          <span className="live-indicator h-2 w-2 rounded-full bg-agent" />
          <span>Vite Proxy Active (/api → 127.0.0.1:8000)</span>
        </div>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
        <div className="flex flex-col gap-6">
          {/* Honest Notice Alert */}
          <div className="rounded-[6px] border border-agent/40 bg-agent/[0.04] p-4 text-[13px] text-secondary">
            <p className="m-0 font-semibold text-primary">Buildathon Prototype Architecture Notice</p>
            <p className="mt-1 mb-0 leading-relaxed">
              Vaidya operates in a <strong className="text-primary">high-fidelity prototype sandbox</strong> mode. The event schemas and fields (payment status, error codes, mandate tokens) are modeled strictly after publicly documented payment concepts and canonical Kaggle merchant fraud datasets. <em>Vaidya does not claim live production authorization on proprietary merchant rails</em>.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* Gateway & Webhook Ingestion */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <h3 className="m-0 text-[14px] font-semibold text-primary">
                Ingestion Surface Endpoints
              </h3>
              <p className="mt-1 mb-4 text-[12px] text-secondary">
                REST APIs for real-time loss event interception
              </p>
              <div className="flex flex-col gap-3 text-[12px]">
                <div className="rounded bg-ink p-3">
                  <div className="flex items-center justify-between font-data">
                    <span className="font-semibold text-agent">POST /api/recovery/analyze</span>
                    <span className="rounded bg-recovered/15 px-1.5 py-0.5 text-[10px] text-recovered font-medium">Active</span>
                  </div>
                  <p className="mt-1 mb-0 text-[11px] text-secondary">
                    Receives single transaction failure, cart abandonment, or invoice aging event for synchronous AI diagnosis and execution.
                  </p>
                </div>

                <div className="rounded bg-ink p-3">
                  <div className="flex items-center justify-between font-data">
                    <span className="font-semibold text-agent">POST /api/recovery/process-batch</span>
                    <span className="rounded bg-recovered/15 px-1.5 py-0.5 text-[10px] text-recovered font-medium">Active</span>
                  </div>
                  <p className="mt-1 mb-0 text-[11px] text-secondary">
                    Batched settlement processing over selected revenue surfaces with configurable limits.
                  </p>
                </div>
              </div>
            </div>

            {/* Downstream Execution Mode */}
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <h3 className="m-0 text-[14px] font-semibold text-primary">
                Downstream Action Execution
              </h3>
              <p className="mt-1 mb-4 text-[12px] text-secondary">
                Simulated settlement & notification dispatch
              </p>
              <div className="rounded bg-ink p-4 text-[12px]">
                <div className="flex justify-between border-b border-hairline/60 pb-2">
                  <span className="text-secondary">Execution Service Mode:</span>
                  <span className="font-data font-semibold text-primary">
                    {loading ? '...' : status?.execution_service.mode || 'prototype_simulation'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-hairline/60 py-2">
                  <span className="text-secondary">Payment Gateway Engine:</span>
                  <span className="font-data font-semibold text-agent">
                    {loading ? '...' : status?.execution_service.live_payment_gateway || 'simulated_sandbox'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-hairline/60 py-2">
                  <span className="text-secondary">Checkout Engagement:</span>
                  <span className="font-data text-primary">Simulated WhatsApp/SMS Hook</span>
                </div>
                <div className="flex justify-between pt-2">
                  <span className="text-secondary">B2B Invoice Scheduler:</span>
                  <span className="font-data text-primary">Simulated Promise-to-Pay Ledger</span>
                </div>
              </div>
            </div>
          </div>

          {/* Canonical Datasets Used */}
          <div className="rounded-[6px] border border-hairline bg-panel p-5">
            <h3 className="m-0 text-[14px] font-semibold text-primary">
              Canonical Ingestion Datasets
            </h3>
            <p className="mt-1 mb-4 text-[12px] text-secondary">
              Pre-generated and verified ground truth datasets used for retrieval and simulation
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4 text-[12px]">
              <div className="rounded bg-ink p-3">
                <span className="text-[11px] font-medium uppercase text-tertiary">Payment Failures</span>
                <p className="font-data m-0 mt-1 font-semibold text-primary">5,000 events</p>
                <p className="m-0 mt-0.5 text-[11px] text-secondary">payment_failure_events.csv</p>
              </div>
              <div className="rounded bg-ink p-3">
                <span className="text-[11px] font-medium uppercase text-tertiary">Checkout Abandonment</span>
                <p className="font-data m-0 mt-1 font-semibold text-primary">2,000 events</p>
                <p className="m-0 mt-0.5 text-[11px] text-secondary">checkout_abandonment_events.csv</p>
              </div>
              <div className="rounded bg-ink p-3">
                <span className="text-[11px] font-medium uppercase text-tertiary">Overdue Invoices</span>
                <p className="font-data m-0 mt-1 font-semibold text-primary">1,500 events</p>
                <p className="m-0 mt-0.5 text-[11px] text-secondary">overdue_invoice_events.csv</p>
              </div>
              <div className="rounded bg-ink p-3">
                <span className="text-[11px] font-medium uppercase text-tertiary">Historical RAG Corpus</span>
                <p className="font-data m-0 mt-1 font-semibold text-primary">3,001 cases</p>
                <p className="m-0 mt-0.5 text-[11px] text-secondary">historical_recovery_cases.csv</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
