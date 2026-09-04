import { usePolicies } from '../hooks/useRecoveryData.ts'
import { formatEventType, formatInr } from '../lib/agentPipeline.ts'

export function PoliciesPage() {
  const { policies, loading, refresh } = usePolicies()

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center bg-ink text-secondary">
        <span className="live-indicator h-3 w-3 rounded-full bg-agent" />
        <span className="ml-3 text-[13px]">Querying PolicyEngine rules...</span>
      </div>
    )
  }

  if (!policies) {
    return (
      <div className="flex h-full items-center justify-center bg-ink text-secondary">
        <p className="text-[13px]">Unable to load PolicyEngine rules.</p>
      </div>
    )
  }

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-ink">
      <header className="flex shrink-0 items-center justify-between border-b border-hairline px-6 py-4">
        <div>
          <h2 className="m-0 text-[18px] font-semibold text-primary">
            Policy & Safety Governance Engine
          </h2>
          <p className="mt-0.5 mb-0 text-[13px] text-secondary">
            Deterministic safety boundaries, human escalation thresholds, and allowed action spaces enforced across Vaidya
          </p>
        </div>

        <button
          type="button"
          onClick={() => refresh()}
          className="cursor-pointer rounded-[4px] border border-hairline bg-panel px-3 py-1.5 text-[12px] text-primary hover:bg-panel-raised"
        >
          Refresh Rules
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
        <div className="flex flex-col gap-6">
          {/* Core Guardrails */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Max Automation Limit
              </span>
              <p className="font-data m-0 mt-2 text-[24px] font-bold text-primary">
                {formatInr(policies.max_automation_amount)}
              </p>
              <p className="m-0 mt-1 text-[12px] text-secondary">
                Transactions strictly above this threshold require human manager approval.
              </p>
            </div>

            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Min Confidence Threshold
              </span>
              <p className="font-data m-0 mt-2 text-[24px] font-bold text-primary">
                {(policies.min_automation_confidence * 100).toFixed(0)}%
              </p>
              <p className="m-0 mt-1 text-[12px] text-secondary">
                AI decisions below this confidence are halted for human verification.
              </p>
            </div>

            <div className="rounded-[6px] border border-hairline bg-panel p-5">
              <span className="text-[11px] font-medium uppercase tracking-wider text-tertiary">
                Supported Revenue Surfaces
              </span>
              <p className="font-data m-0 mt-2 text-[24px] font-bold text-agent">
                {policies.supported_event_types.length} Surfaces
              </p>
              <p className="m-0 mt-1 text-[12px] text-secondary">
                {policies.supported_event_types.join(', ')}
              </p>
            </div>
          </div>

          {/* Hard Safety Boundaries */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {/* Zero Tolerance Fraud Rule */}
            <div className="rounded-[6px] border border-risk/40 bg-risk/[0.02] p-5">
              <div className="flex items-center justify-between">
                <h3 className="m-0 text-[14px] font-semibold text-risk">
                  {policies.fraud_policy.rule}
                </h3>
                <span className="rounded bg-risk/15 px-2 py-0.5 text-[10px] font-semibold text-risk uppercase">
                  Zero Tolerance
                </span>
              </div>
              <p className="mt-2 text-[12px] leading-relaxed text-secondary">
                {policies.fraud_policy.description}
              </p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[11px]">
                <div className="rounded bg-ink p-2">
                  <span className="text-tertiary">Enforced Action:</span>
                  <p className="font-data m-0 mt-0.5 font-semibold text-primary">
                    {policies.fraud_policy.action}
                  </p>
                </div>
                <div className="rounded bg-ink p-2">
                  <span className="text-tertiary">Automation Allowed:</span>
                  <p className="font-data m-0 mt-0.5 font-semibold text-risk">
                    {policies.fraud_policy.allowed ? 'YES' : 'STRICTLY PROHIBITED'}
                  </p>
                </div>
              </div>
            </div>

            {/* High Value Review Rule */}
            <div className="rounded-[6px] border border-escalate/40 bg-escalate/[0.02] p-5">
              <div className="flex items-center justify-between">
                <h3 className="m-0 text-[14px] font-semibold text-escalate">
                  {policies.high_value_policy.rule}
                </h3>
                <span className="rounded bg-escalate/15 px-2 py-0.5 text-[10px] font-semibold text-escalate uppercase">
                  Threshold Gating
                </span>
              </div>
              <p className="mt-2 text-[12px] leading-relaxed text-secondary">
                {policies.high_value_policy.description}
              </p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[11px]">
                <div className="rounded bg-ink p-2">
                  <span className="text-tertiary">Review Threshold:</span>
                  <p className="font-data m-0 mt-0.5 font-semibold text-primary">
                    {formatInr(policies.high_value_policy.threshold)}
                  </p>
                </div>
                <div className="rounded bg-ink p-2">
                  <span className="text-tertiary">Enforced Action:</span>
                  <p className="font-data m-0 mt-0.5 font-semibold text-escalate">
                    {policies.high_value_policy.action}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Permitted Action Spaces */}
          <div className="rounded-[6px] border border-hairline bg-panel p-5">
            <h3 className="m-0 text-[14px] font-semibold text-primary">
              Allowed Autonomous Action Spaces per Surface
            </h3>
            <p className="mt-1 mb-4 text-[12px] text-secondary">
              Only pre-approved actions can be recommended or executed by Vaidya for each revenue risk surface
            </p>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {Object.entries(policies.allowed_actions).map(([surface, acts]) => (
                <div key={surface} className="rounded-[4px] border border-hairline bg-ink p-4 text-[12px]">
                  <span className="font-semibold text-primary">
                    {formatEventType(surface)}
                  </span>
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {acts.map((act) => (
                      <span
                        key={act}
                        className="font-data rounded border border-hairline bg-panel px-2 py-1 text-[11px] text-secondary"
                      >
                        {act}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
