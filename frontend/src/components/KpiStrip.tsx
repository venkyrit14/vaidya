import { formatInr } from '../lib/agentPipeline.ts'
import type { RecoverySummaryResponse } from '../types/recovery.ts'

type KpiStripProps = {
  summary: RecoverySummaryResponse | null
  loading?: boolean
}

export function KpiStrip({ summary, loading }: KpiStripProps) {
  const atRiskVal = summary ? formatInr(summary.total_amount_at_risk) : '—'
  const atRiskSub = summary ? `${summary.total_cases} cases tracked` : 'Loading...'

  const recoveredVal = summary ? formatInr(summary.total_recovered) : '—'
  const recoveredSub = summary
    ? `${summary.successful_recoveries} successful (${summary.partial_recoveries} partial)`
    : 'Loading...'

  const remainingVal = summary ? formatInr(summary.total_remaining) : '—'
  const remainingSub = summary
    ? `${summary.blocked_cases} blocked · ${summary.human_review_cases} human review`
    : 'Loading...'

  const rateVal = summary ? `${summary.recovery_rate.toFixed(1)}%` : '—'
  const rateSub = summary
    ? `${summary.available_source_events.toLocaleString('en-IN')} uningested source events`
    : 'Loading...'

  const metrics = [
    {
      label: 'Amount At Risk',
      value: atRiskVal,
      sublabel: atRiskSub,
      sublabelTone: 'neutral' as const,
    },
    {
      label: 'Recovered Revenue',
      value: recoveredVal,
      sublabel: recoveredSub,
      sublabelTone: 'positive' as const,
    },
    {
      label: 'Remaining / Gated',
      value: remainingVal,
      sublabel: remainingSub,
      sublabelTone: 'neutral' as const,
    },
    {
      label: 'Recovery Rate',
      value: rateVal,
      sublabel: rateSub,
      sublabelTone: 'positive' as const,
    },
  ]

  return (
    <section
      aria-label="Revenue recovery metrics"
      className="grid shrink-0 grid-cols-2 border-b border-hairline bg-ink lg:grid-cols-4"
    >
      {metrics.map((item, idx) => (
        <div
          key={item.label}
          className={`px-6 py-4 border-hairline ${
            idx < 2 ? 'border-b lg:border-b-0' : ''
          } ${idx % 2 === 0 ? 'border-r' : ''} ${
            idx < 3 ? 'lg:border-r' : ''
          }`}
        >
          <p className="m-0 text-[12px] font-medium text-secondary">{item.label}</p>
          <div className="mt-1.5 flex items-baseline gap-2.5">
            <span
              className={`font-data text-[22px] font-semibold tracking-tight text-primary ${
                loading ? 'animate-pulse opacity-60' : ''
              }`}
            >
              {item.value}
            </span>
            <span
              className={`font-data text-[12px] ${
                item.sublabelTone === 'positive'
                  ? 'text-recovered'
                  : 'text-tertiary'
              }`}
            >
              {item.sublabel}
            </span>
          </div>
        </div>
      ))}
    </section>
  )
}
