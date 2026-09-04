import type { ReactNode } from 'react'
import { LeftRail } from './LeftRail.tsx'
import type { NavItemId } from './Navigation.tsx'

type AppShellProps = {
  activeItem: NavItemId
  onNavigate?: (item: NavItemId) => void
  children: ReactNode
}

export function AppShell({ activeItem, onNavigate, children }: AppShellProps) {
  return (
    <div className="flex h-svh min-h-0 w-full bg-ink">
      <LeftRail activeItem={activeItem} onNavigate={onNavigate} />
      <main className="min-h-0 min-w-0 flex-1 overflow-hidden bg-ink">
        {children}
      </main>
    </div>
  )
}
