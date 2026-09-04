import type {
  DemoCase,
  LiveFeedEvent,
  SimulatedAgentState,
} from '../types/liveFeed.ts'

export const PIPELINE_STAGES: SimulatedAgentState[] = [
  'detected',
  'diagnosing',
  'evidence',
  'decision',
  'policy',
  'action',
  'outcome',
]

export const ROOT_CAUSE_LABELS: Record<string, string> = {
  network_error: 'Network timeout during payment',
  expired_card: 'Expired card',
  insufficient_funds: 'Insufficient funds',
  bank_timeout: 'Bank response timeout',
  mandate_failure: 'Recurring mandate execution failure',
  fraud_risk: 'Fraud risk detected',
  high_intent_abandonment: 'High-intent abandonment detected',
  checkout_hesitation: 'Checkout hesitation detected',
  repeated_abandonment: 'Repeated checkout abandonment',
  repeated_late_payer: 'Repeated late payer',
  recently_overdue: 'Recently overdue invoice',
  high_value_overdue: 'High-value overdue invoice',
  customer_dispute: 'Customer payment dispute',
}

export function formatRootCause(rawCause: string): string {
  if (ROOT_CAUSE_LABELS[rawCause]) {
    return ROOT_CAUSE_LABELS[rawCause]
  }
  return rawCause
    .replaceAll('_', ' ')
    .replace(/^./, (c) => c.toUpperCase())
}

export function formatCustomerProfile(profile: string): string {
  const map: Record<string, string> = {
    repeat_customer: 'Repeat customer',
    high_intent_shopper: 'High-intent shopper',
    b2b_account: 'B2B enterprise account',
    elevated_risk_account: 'Elevated risk account',
    high_value_enterprise: 'High-value enterprise',
  }
  return (
    map[profile] ||
    profile.replaceAll('_', ' ').replace(/^./, (c) => c.toUpperCase())
  )
}

export function formatEventType(eventType: string): string {
  const map: Record<string, string> = {
    payment_failure: 'Payment failure',
    checkout_abandonment: 'Checkout abandonment',
    overdue_invoice: 'Overdue invoice',
  }
  return (
    map[eventType] ||
    eventType.replaceAll('_', ' ').replace(/^./, (c) => c.toUpperCase())
  )
}

export function formatInr(amount: number): string {
  return `₹${amount.toLocaleString('en-IN')}`
}

export function getStateLabel(
  state: SimulatedAgentState,
  event: Pick<LiveFeedEvent, 'finalOutcome' | 'decision' | 'policy'>,
): string {
  switch (state) {
    case 'detected':
      return 'Detected'
    case 'diagnosing':
      return 'Diagnosing'
    case 'evidence':
      return 'Evidence found'
    case 'decision':
      return `Decision: ${event.decision.actionLabel}`
    case 'policy':
      return `Policy: ${event.policy.status}`
    case 'action':
      return 'Action executing'
    case 'outcome':
      if (event.finalOutcome === 'recovered') return 'Recovered'
      if (event.finalOutcome === 'blocked') return 'Blocked'
      return 'Human review'
  }
}

export function isTerminalState(state: SimulatedAgentState): boolean {
  return state === 'outcome'
}

export function getStageIndex(state: SimulatedAgentState): number {
  return PIPELINE_STAGES.indexOf(state)
}

export const DEMO_CASES: DemoCase[] = [
  {
    caseId: 'PAY-89211',
    eventType: 'payment_failure',
    amount: 6200,
    rootCause: 'network_error',
    customerProfile: 'repeat_customer',
    evidence: {
      caseCount: 10,
      successRate: 80,
      note: '10 similar historical cases · 80% recovery on retry',
    },
    decision: {
      action: 'RETRY',
      actionLabel: 'Retry payment',
      confidence: 89.92,
    },
    policy: {
      status: 'APPROVED',
      reason: 'Standard network timeout recovery authorized',
    },
    execution: {
      status: 'RETRY IN PROGRESS',
      description: 'Automated gateway retry initiated',
    },
    finalOutcome: 'recovered',
    recoveredAmount: 6200,
    outcomeMessage: 'Payment retried successfully · ₹6,200 recovered',
  },
  {
    caseId: 'CHK-44120',
    eventType: 'checkout_abandonment',
    amount: 5000,
    rootCause: 'high_intent_abandonment',
    customerProfile: 'high_intent_shopper',
    evidence: {
      caseCount: 276,
      successRate: 74,
      note: '276 similar historical cases · High checkout intent detected',
    },
    decision: {
      action: 'TARGETED_REMINDER',
      actionLabel: 'Targeted reminder',
      confidence: 92.4,
    },
    policy: {
      status: 'APPROVED',
      reason: 'Engagement policy compliant · Safe for recovery message',
    },
    execution: {
      status: 'Recovery message queued',
      description: 'Simulated personalized checkout reminder dispatched',
    },
    finalOutcome: 'recovered',
    recoveredAmount: 5000,
    outcomeMessage:
      'Customer returned to checkout · Payment completed · ₹5,000 recovered',
  },
  {
    caseId: 'INV-10943',
    eventType: 'overdue_invoice',
    amount: 50000,
    rootCause: 'repeated_late_payer',
    customerProfile: 'b2b_account',
    evidence: {
      caseCount: 8,
      successRate: 87.5,
      note: '8 previous invoices · 5 previous late payments settled via schedule',
    },
    decision: {
      action: 'PROMISE_TO_PAY',
      actionLabel: 'Promise to pay',
      confidence: 85.15,
    },
    policy: {
      status: 'APPROVED',
      reason: 'Under ₹1,00,000 threshold · Flexible schedule allowed',
    },
    execution: {
      status: 'Promise-to-pay scheduled',
      description: 'Structured 7-day payment commitment registered',
    },
    finalOutcome: 'recovered',
    recoveredAmount: 50000,
    outcomeMessage: 'Promise-to-pay fulfilled · ₹50,000 recovered',
  },
  {
    caseId: 'FRD-99014',
    eventType: 'payment_failure',
    amount: 10000,
    rootCause: 'fraud_risk',
    customerProfile: 'elevated_risk_account',
    evidence: {
      caseCount: 42,
      note: 'Risk engine trigger · Device fingerprint & IP velocity mismatch',
    },
    decision: {
      action: 'BLOCK_AND_ESCALATE',
      actionLabel: 'Block & escalate',
      confidence: 98.7,
    },
    policy: {
      status: 'AUTOMATIC RECOVERY PROHIBITED',
      reason: 'Zero-tolerance risk block · Security review mandated',
    },
    execution: {
      status: 'Security block active',
      description: 'Transaction halted · Account token isolated',
    },
    finalOutcome: 'blocked',
    recoveredAmount: 0,
    outcomeMessage: 'BLOCKED · Human / security review required',
  },
  {
    caseId: 'INV-88301',
    eventType: 'overdue_invoice',
    amount: 250000,
    rootCause: 'repeated_late_payer',
    customerProfile: 'high_value_enterprise',
    evidence: {
      caseCount: 15,
      note: 'High-value enterprise tier · Credit exposure limit reached',
    },
    decision: {
      action: 'PROMISE_TO_PAY',
      actionLabel: 'Promise to pay',
      confidence: 88.0,
    },
    policy: {
      status: 'APPROVAL REQUIRED',
      reason: 'Amount exceeds ₹1,00,000 automatic handling limit',
    },
    execution: {
      status: 'Awaiting manager approval',
      description: 'Routed to enterprise risk operations queue',
    },
    finalOutcome: 'human_review',
    recoveredAmount: 0,
    outcomeMessage: 'HUMAN REVIEW · Manual approval required before recovery',
  },
]
