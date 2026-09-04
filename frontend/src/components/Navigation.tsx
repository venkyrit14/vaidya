import type { ReactNode } from 'react'

export type NavItemId =
  | 'command-center'
  | 'live-recovery'
  | 'human-review'
  | 'analytics'
  | 'action-history'
  | 'policies'
  | 'system-health'
  | 'integration'

type NavItemConfig = {
  id: NavItemId
  label: string
  badge?: string | number
  badgeTone?: 'agent' | 'escalate' | 'muted'
}

type NavGroup = {
  title?: string
  items: NavItemConfig[]
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: 'Operations',
    items: [
      { id: 'command-center', label: 'Command Center' },
      { id: 'live-recovery', label: 'Case Explorer' },
      { id: 'human-review', label: 'Human Review', badgeTone: 'escalate' },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { id: 'analytics', label: 'Analytics' },
      { id: 'action-history', label: 'Action History' },
    ],
  },
  {
    title: 'System & Governance',
    items: [
      { id: 'policies', label: 'Policies' },
      { id: 'system-health', label: 'System Health' },
      { id: 'integration', label: 'Integration' },
    ],
  },
]

type NavigationProps = {
  activeItem: NavItemId
  onNavigate?: (item: NavItemId) => void
  humanReviewCount?: number
}

function NavIcon({ itemId }: { itemId: NavItemId }): ReactNode {
  switch (itemId) {
    case 'command-center':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <rect x="2" y="2" width="5" height="5" rx="1" />
          <rect x="9" y="2" width="5" height="5" rx="1" />
          <rect x="2" y="9" width="5" height="5" rx="1" />
          <rect x="9" y="9" width="5" height="5" rx="1" />
        </svg>
      )
    case 'live-recovery':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <polyline points="2 8 5 8 7 3 9 13 11 8 14 8" />
        </svg>
      )
    case 'human-review':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M11 14v-1.5a3.5 3.5 0 0 0-7 0V14" />
          <circle cx="7.5" cy="5.5" r="2.5" />
          <path d="M12.5 7.5a2 2 0 0 1 0 4" />
        </svg>
      )
    case 'analytics':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <line x1="13" y1="13" x2="13" y2="7" />
          <line x1="8" y1="13" x2="8" y2="4" />
          <line x1="3" y1="13" x2="3" y2="10" />
        </svg>
      )
    case 'action-history':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="8" cy="8" r="6" />
          <polyline points="8 4.5 8 8 10.5 9.5" />
        </svg>
      )
    case 'policies':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M8 2.5l5 2v4c0 3.5-2.5 5.5-5 6.5-2.5-1-5-3-5-6.5v-4l5-2z" />
        </svg>
      )
    case 'system-health':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <rect x="2" y="3" width="12" height="10" rx="1.5" />
          <line x1="5.5" y1="8" x2="10.5" y2="8" />
        </svg>
      )
    case 'integration':
      return (
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <polyline points="10.5 4 13.5 4 13.5 7" />
          <line x1="6.5" y1="9.5" x2="13.5" y2="2.5" />
          <path d="M12 10.5v3a1 1 0 0 1-1 1H3.5a1 1 0 0 1-1-1v-7.5a1 1 0 0 1 1-1h3" />
        </svg>
      )
  }
}

export function Navigation({
  activeItem,
  onNavigate,
  humanReviewCount,
}: NavigationProps) {
  return (
    <nav aria-label="Main Navigation" className="flex flex-col gap-6">
      {NAV_GROUPS.map((group, groupIdx) => (
        <div key={groupIdx} className="flex flex-col gap-1">
          {group.title ? (
            <p className="px-2 pb-1 text-[11px] font-semibold tracking-wider text-tertiary uppercase">
              {group.title}
            </p>
          ) : null}
          <ul className="m-0 flex list-none flex-col gap-1 p-0">
            {group.items.map((item) => {
              const isActive = item.id === activeItem
              const badge =
                item.id === 'human-review'
                  ? humanReviewCount
                  : item.badge

              return (
                <li key={item.id}>
                  <button
                    type="button"
                    aria-current={isActive ? 'page' : undefined}
                    onClick={() => onNavigate?.(item.id)}
                    className={`group flex w-full cursor-pointer items-center justify-between rounded-[4px] border px-2.5 py-2 text-left text-[13px] transition-colors ${
                      isActive
                        ? 'border-hairline bg-panel-raised font-medium text-primary'
                        : 'border-transparent text-secondary hover:bg-panel-raised/50 hover:text-primary'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span
                        className={`transition-colors ${
                          isActive
                            ? 'text-agent'
                            : 'text-tertiary group-hover:text-secondary'
                        }`}
                      >
                        <NavIcon itemId={item.id} />
                      </span>
                      <span>{item.label}</span>
                    </div>

                    {badge !== undefined &&
                    (typeof badge === 'number' ? badge > 0 : Boolean(badge)) ? (
                      <span
                        className={`font-data rounded-[999px] px-1.5 py-0.2 text-[11px] font-medium ${
                          item.badgeTone === 'escalate'
                            ? 'bg-escalate/15 text-escalate'
                            : item.badgeTone === 'agent'
                              ? 'bg-agent/15 text-agent'
                              : 'bg-panel-raised text-secondary'
                        }`}
                      >
                        {badge}
                      </span>
                    ) : null}
                  </button>
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </nav>
  )
}
