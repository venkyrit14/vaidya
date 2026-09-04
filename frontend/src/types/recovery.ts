export type RecoveryRequest = {
  event_type: string
  root_cause?: string | null
  amount: number
  customer_profile: string
}

export type RecoveryResponse = {
  case_id: string
  event_type: string
  amount_at_risk: number
  decision: string
  action: string
  confidence: number
  expected_recovery: number
  policy_allowed: boolean
  risk_level: string
  requires_human: boolean
  execution_status: string
  outcome: string
  recovered_amount: number
  remaining_amount: number
  message: string
  timestamp?: string | null
}

export type RecoverySummaryResponse = {
  total_cases: number
  total_amount_at_risk: number
  total_recovered: number
  total_remaining: number
  recovery_rate: number
  successful_recoveries: number
  failed_recoveries: number
  partial_recoveries: number
  blocked_cases: number
  human_review_cases: number
  outcomes: Record<string, number>
  actions: Record<string, number>
  event_types: Record<string, number>
  available_source_events: number
  available_source_amount: number
}

export type RecoveryRecord = {
  case_id: string
  event_type: string
  amount_at_risk: number
  action: string
  execution_status: string
  outcome: string
  recovered_amount: number
  remaining_amount: number
  requires_human: boolean
  timestamp: string
  message: string
}

export type PaginatedRecordsResponse = {
  items: RecoveryRecord[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export type BatchSummary = {
  batch_id: string
  title: string
  surface: string
  description: string
  total_events: number
  total_amount_at_risk: number
  processed_count: number
}

export type BatchEvent = {
  event_id: string
  event_type: string
  amount: number
  root_cause: string
  customer_profile: string
  customer_id: string
  timestamp: string
}

export type BatchEventsResponse = {
  batch_id: string
  items: BatchEvent[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export type ProcessBatchRequest = {
  batch_id: string
  limit?: number
}

export type ProcessBatchResultItem = {
  case_id: string
  event_id: string
  event_type: string
  amount_at_risk: number
  decision: string
  action: string
  confidence: number
  expected_recovery: number
  policy_allowed: boolean
  risk_level: string
  requires_human: boolean
  execution_status: string
  outcome: string
  recovered_amount: number
  remaining_amount: number
  message: string
  timestamp?: string | null
}

export type ProcessBatchResponse = {
  batch_id: string
  processed_count: number
  results: ProcessBatchResultItem[]
}

export type PolicyConfig = {
  max_automation_amount: number
  min_automation_confidence: number
  supported_event_types: string[]
  allowed_actions: Record<string, string[]>
  fraud_policy: {
    rule: string
    action: string
    allowed: boolean
    expected_recovery: number
    risk_level: string
    requires_human: boolean
    description: string
  }
  high_value_policy: {
    rule: string
    threshold: number
    action: string
    description: string
  }
}

export type SubsystemStatus = {
  name: string
  status: string
  [key: string]: unknown
}

export type SystemStatus = {
  api: SubsystemStatus & { version: string }
  decision_engine: SubsystemStatus & {
    initialized: boolean
    action_spaces_count: number
  }
  retrieval_service: SubsystemStatus & {
    corpus_size: number
    similarity_threshold: number
    storage_file: string
  }
  policy_engine: SubsystemStatus & {
    max_automation_amount: number
    min_confidence: number
  }
  execution_service: SubsystemStatus & {
    mode: string
    live_payment_gateway: string
  }
  recovery_tracker: SubsystemStatus & {
    persisted_records_count: number
    storage_file: string
  }
}

export type DecisionContext = {
  decision: string
  action: string
  confidence: number
  expected_recovery: number
  reason: string
  historical_cases_count?: number
  evidence?: Array<Record<string, unknown>>
  action_analysis?: Array<Record<string, unknown>>
}

export type PolicyContext = {
  allowed: boolean
  decision: string
  reason: string
  risk_level: string
  requires_human: boolean
}

export type CaseDetailsResponse = {
  record: RecoveryRecord
  decision_context: DecisionContext
  policy_context: PolicyContext
}
