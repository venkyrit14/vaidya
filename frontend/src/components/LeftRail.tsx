import { Navigation } from './Navigation.tsx'
import type { NavItemId } from './Navigation.tsx'
import { useRecoverySummary, useSystemStatus } from '../hooks/useRecoveryData.ts'

type LeftRailProps = {
  activeItem: NavItemId
  onNavigate?: (item: NavItemId) => void
}

export function LeftRail({ activeItem, onNavigate }: LeftRailProps) {
  const { summary } = useRecoverySummary(15000)
  const { status, error } = useSystemStatus(15000)

  const isConnected = !error && status !== null

  return (
    <aside className="flex w-[240px] shrink-0 flex-col justify-between overflow-y-auto border-r border-hairline bg-panel px-3.5 py-5">
      <div className="flex flex-col gap-6">
        {/* Brand Header */}
        <header className="flex items-center gap-2.5 px-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-[4px] bg-agent/15 text-agent">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M6 3h12M6 8h12M6 13l8.5 8M6 13h3M9 13c6.667 0 6.667-10 0-10" />
            </svg>
          </div>
          <div>
            <h1 className="m-0 text-[14px] font-bold tracking-wider text-primary">
              VAIDYA
            </h1>
            <p className="m-0 text-[11px] text-tertiary">Recovery Agent</p>
          </div>
        </header>

        <hr className="m-0 border-0 border-t border-hairline" />

        {/* Navigation Grouping with Real Human Review Count */}
        <Navigation
          activeItem={activeItem}
          onNavigate={onNavigate}
          humanReviewCount={summary?.human_review_cases}
        />
      </div>

      {/* Honest System Status Footer */}
      <footer className="mt-6 border-t border-hairline pt-4 px-2">
        <div className="flex items-center justify-between text-[11px] text-tertiary">
          <span className="flex items-center gap-1.5">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                isConnected ? 'bg-recovered' : 'bg-risk'
              }`}
            />
            <span>{isConnected ? 'Subsystems Nominal' : 'Gateway Offline'}</span>
          </span>
          <span className="font-data">v{status?.api.version || '0.1.0'}</span>
        </div>
      </footer>
    </aside>
  )
}
