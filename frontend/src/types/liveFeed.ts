export type SimulatedAgentState =
  | 'detected'
  | 'diagnosing'
  | 'evidence'
  | 'decision'
  | 'policy'
  | 'action'
  | 'outcome'

export type FinalOutcome = 'recovered' | 'blocked' | 'human_review'

export type PolicyStatus =
  | 'APPROVED'
  | 'APPROVAL REQUIRED'
  | 'AUTOMATIC RECOVERY PROHIBITED'

export type LiveFeedEvent = {
  id: string
  caseId: string
  eventType: string
  amount: number
  rootCause: string
  customerProfile: string
  evidence: {
    caseCount: number
    successRate?: number
    note: string
  }
  decision: {
    action: string
    actionLabel: string
    confidence: number
  }
  policy: {
    status: PolicyStatus
    reason?: string
  }
  execution: {
    status: string
    description: string
  }
  finalOutcome: FinalOutcome
  recoveredAmount: number
  outcomeMessage: string
  simulatedState: SimulatedAgentState
  appearedAt: number
}

export type DemoCase = Omit<
  LiveFeedEvent,
  'id' | 'simulatedState' | 'appearedAt'
>
