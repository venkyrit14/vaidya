import { useState } from 'react'
import { ActionHistoryPage } from './components/ActionHistoryPage.tsx'
import { AnalyticsPage } from './components/AnalyticsPage.tsx'
import { AppShell } from './components/AppShell.tsx'
import { CaseExplorerPage } from './components/CaseExplorerPage.tsx'
import { CommandCenter } from './components/CommandCenter.tsx'
import { HumanReviewPage } from './components/HumanReviewPage.tsx'
import { IntegrationPage } from './components/IntegrationPage.tsx'
import { PoliciesPage } from './components/PoliciesPage.tsx'
import { SystemHealthPage } from './components/SystemHealthPage.tsx'
import type { NavItemId } from './components/Navigation.tsx'

function App() {
  const [activeItem, setActiveItem] = useState<NavItemId>('command-center')

  const renderCurrentPage = () => {
    switch (activeItem) {
      case 'command-center':
        return <CommandCenter />
      case 'live-recovery':
        return <CaseExplorerPage />
      case 'human-review':
        return <HumanReviewPage />
      case 'analytics':
        return <AnalyticsPage />
      case 'action-history':
        return <ActionHistoryPage />
      case 'policies':
        return <PoliciesPage />
      case 'system-health':
        return <SystemHealthPage />
      case 'integration':
        return <IntegrationPage />
      default:
        return <CommandCenter />
    }
  }

  return (
    <AppShell activeItem={activeItem} onNavigate={setActiveItem}>
      {renderCurrentPage()}
    </AppShell>
  )
}

export default App
